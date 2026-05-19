from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from voiceclinic.config import Settings, load_settings
from voiceclinic.llm import OpenAICompatibleChatClient, build_llm_client


def _settings(**overrides) -> Settings:
    base = Settings(
        db_path=Path("data/clinic.db"),
        llm_provider="ollama",
        orchestration_mode="direct",
        ollama_base_url="http://localhost:11434/v1",
        ollama_model="qwen3:30b",
        ollama_timeout_seconds=20,
        openai_base_url="https://api.openai.com/v1",
        openai_api_key=None,
        openai_model="gpt-4.1-mini",
        openai_timeout_seconds=20,
        whisper_model="small",
        piper_bin="piper",
        piper_model=None,
        piper_config=None,
        ffmpeg_bin="ffmpeg",
        audiosocket_host="0.0.0.0",
        audiosocket_port=9092,
    )
    return replace(base, **overrides)


def test_builds_ollama_client_by_default():
    client = build_llm_client(_settings())

    assert isinstance(client, OpenAICompatibleChatClient)
    assert client.provider == "ollama"
    assert client.model == "qwen3:30b"
    assert client.api_key is None


def test_builds_openai_client_when_key_is_configured():
    client = build_llm_client(
        _settings(
            llm_provider="openai",
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
        )
    )

    assert isinstance(client, OpenAICompatibleChatClient)
    assert client.provider == "openai"
    assert client.model == "gpt-4.1-mini"
    assert client.api_key == "test-key"


def test_disables_openai_client_without_key():
    client = build_llm_client(_settings(llm_provider="openai", openai_api_key=None))

    assert client is None


def test_load_settings_reads_provider_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("ORCHESTRATION_MODE", "langgraph")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")

    settings = load_settings(env_file=None)

    assert settings.llm_provider == "openai"
    assert settings.orchestration_mode == "langgraph"
    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "gpt-4.1-mini"
