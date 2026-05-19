from __future__ import annotations

from pathlib import Path


class VoiceDependencyError(RuntimeError):
    pass


class LocalWhisperSTT:
    def __init__(self, model_name: str = "small"):
        self.model_name = model_name
        self._model = None

    def transcribe(self, audio_path: Path | str) -> str:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise VoiceDependencyError(
                "Falta faster-whisper. Instala las dependencias de voz con `uv sync --extra voice`."
            ) from exc

        if self._model is None:
            self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        segments, _ = self._model.transcribe(str(audio_path), vad_filter=True, language="es")
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise VoiceDependencyError("No he podido transcribir audio util.")
        return text
