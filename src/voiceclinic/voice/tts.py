from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from voiceclinic.config import Settings
from voiceclinic.voice.stt import VoiceDependencyError


class PiperTTS:
    def __init__(self, settings: Settings):
        self.settings = settings

    def synthesize(self, text: str, output_wav: Path | str) -> Path:
        if not self.settings.piper_model:
            raise VoiceDependencyError("Falta PIPER_MODEL en .env.")
        if shutil.which(self.settings.piper_bin) is None:
            raise VoiceDependencyError(f"No encuentro el binario Piper: {self.settings.piper_bin}")

        output_path = Path(output_wav)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.settings.piper_bin,
            "--model",
            self.settings.piper_model,
            "--output_file",
            str(output_path),
        ]
        if self.settings.piper_config:
            command.extend(["--config", self.settings.piper_config])
        subprocess.run(command, input=text, text=True, check=True, capture_output=True)
        return output_path

    def synthesize_pcm8k(self, text: str, output_raw: Path | str) -> Path:
        raw_path = Path(output_raw)
        wav_path = raw_path.with_suffix(".wav")
        self.synthesize(text, wav_path)
        if shutil.which(self.settings.ffmpeg_bin) is None:
            raise VoiceDependencyError(f"No encuentro ffmpeg: {self.settings.ffmpeg_bin}")
        subprocess.run(
            [
                self.settings.ffmpeg_bin,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(wav_path),
                "-f",
                "s16le",
                "-acodec",
                "pcm_s16le",
                "-ac",
                "1",
                "-ar",
                "8000",
                str(raw_path),
            ],
            check=True,
        )
        return raw_path
