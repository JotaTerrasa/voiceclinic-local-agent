from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    db_path: Path
    llm_provider: str
    orchestration_mode: str
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: float
    openai_base_url: str
    openai_api_key: str | None
    openai_model: str
    openai_timeout_seconds: float
    whisper_model: str
    piper_bin: str
    piper_model: str | None
    piper_config: str | None
    ffmpeg_bin: str
    audiosocket_host: str
    audiosocket_port: int


def load_settings(env_file: str | None = ".env") -> Settings:
    if env_file:
        load_dotenv(env_file, override=False)

    return Settings(
        db_path=Path(os.getenv("VOICECLINIC_DB", "data/clinic.db")),
        llm_provider=os.getenv("LLM_PROVIDER", "ollama").strip().lower(),
        orchestration_mode=os.getenv("ORCHESTRATION_MODE", "direct").strip().lower(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen3:30b"),
        ollama_timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "20")),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20")),
        whisper_model=os.getenv("WHISPER_MODEL", "small"),
        piper_bin=os.getenv("PIPER_BIN", "piper"),
        piper_model=os.getenv("PIPER_MODEL") or None,
        piper_config=os.getenv("PIPER_CONFIG") or None,
        ffmpeg_bin=os.getenv("FFMPEG_BIN", "ffmpeg"),
        audiosocket_host=os.getenv("AUDIOSOCKET_HOST", "0.0.0.0"),
        audiosocket_port=int(os.getenv("AUDIOSOCKET_PORT", "9092")),
    )
