from __future__ import annotations

import asyncio
import math
import struct
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from voiceclinic.agent import ClinicAgent
from voiceclinic.config import Settings
from voiceclinic.voice.stt import LocalWhisperSTT, VoiceDependencyError
from voiceclinic.voice.tts import PiperTTS

TYPE_TERMINATE = 0x00
TYPE_UUID = 0x01
TYPE_DTMF = 0x03
TYPE_PCM_8K = 0x10


@dataclass
class TurnBuffer:
    frames: bytearray
    speaking: bool = False
    silent_frames: int = 0


class AudioSocketAgentServer:
    """Minimal Asterisk AudioSocket bridge.

    This is intentionally small: it proves the local telephony path and keeps the
    appointment logic in the shared ClinicAgent. For production you would add
    interruption handling, call recording policy, monitoring and better VAD.
    """

    def __init__(self, settings: Settings, host: str = "0.0.0.0", port: int = 9092):
        self.settings = settings
        self.host = host
        self.port = port

    async def serve_forever(self) -> None:
        server = await asyncio.start_server(self._handle_call, self.host, self.port)
        print(f"AudioSocket escuchando en {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def _handle_call(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        call_id = str(uuid4())
        buffer = TurnBuffer(frames=bytearray())
        agent = ClinicAgent(self.settings.db_path, settings=self.settings)

        try:
            await self._send_text(
                writer,
                "Hola, soy el agente de citas de la clinica. Dime en que puedo ayudarte.",
            )
            while not reader.at_eof():
                packet_type, payload = await _read_packet(reader)
                if packet_type == TYPE_TERMINATE:
                    break
                if packet_type == TYPE_UUID:
                    call_id = str(uuid4())
                    continue
                if packet_type == TYPE_DTMF:
                    continue
                if packet_type != TYPE_PCM_8K:
                    continue

                completed_audio = _collect_turn(buffer, payload)
                if not completed_audio:
                    continue

                transcript = await asyncio.to_thread(self._transcribe_pcm, completed_audio, call_id)
                if not transcript:
                    continue
                reply = await agent.handle_text(transcript)
                await self._send_text(writer, reply.text)
        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    def _transcribe_pcm(self, pcm: bytes, call_id: str) -> str | None:
        artifact_dir = Path(tempfile.gettempdir()) / "voiceclinic-calls"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        wav_path = artifact_dir / f"{call_id}-{uuid4()}.wav"
        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(pcm)
        try:
            return LocalWhisperSTT(self.settings.whisper_model).transcribe(wav_path)
        except VoiceDependencyError as exc:
            print(f"STT no disponible: {exc}")
            return None

    async def _send_text(self, writer: asyncio.StreamWriter, text: str) -> None:
        artifact_dir = Path(tempfile.gettempdir()) / "voiceclinic-calls"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        raw_path = artifact_dir / f"{uuid4()}.raw"
        try:
            PiperTTS(self.settings).synthesize_pcm8k(text, raw_path)
        except VoiceDependencyError as exc:
            print(f"TTS no disponible: {exc}. Respuesta: {text}")
            return

        audio = raw_path.read_bytes()
        for offset in range(0, len(audio), 320):
            await _write_packet(writer, TYPE_PCM_8K, audio[offset : offset + 320])
            await asyncio.sleep(0.02)


async def _read_packet(reader: asyncio.StreamReader) -> tuple[int, bytes]:
    header = await reader.readexactly(3)
    packet_type = header[0]
    length = int.from_bytes(header[1:3], byteorder="big")
    payload = await reader.readexactly(length) if length else b""
    return packet_type, payload


async def _write_packet(writer: asyncio.StreamWriter, packet_type: int, payload: bytes) -> None:
    writer.write(bytes([packet_type]) + len(payload).to_bytes(2, byteorder="big") + payload)
    await writer.drain()


def _collect_turn(buffer: TurnBuffer, frame: bytes) -> bytes | None:
    rms = _rms(frame)
    is_speech = rms > 450

    if is_speech:
        buffer.speaking = True
        buffer.silent_frames = 0
        buffer.frames.extend(frame)
        return None

    if not buffer.speaking:
        return None

    buffer.silent_frames += 1
    buffer.frames.extend(frame)
    if buffer.silent_frames < 35:
        return None

    completed = bytes(buffer.frames)
    buffer.frames.clear()
    buffer.speaking = False
    buffer.silent_frames = 0
    if len(completed) < 8000:
        return None
    return completed


def _rms(frame: bytes) -> float:
    if len(frame) < 2:
        return 0.0
    sample_count = len(frame) // 2
    samples = struct.unpack(f"<{sample_count}h", frame[: sample_count * 2])
    return math.sqrt(sum(sample * sample for sample in samples) / sample_count)
