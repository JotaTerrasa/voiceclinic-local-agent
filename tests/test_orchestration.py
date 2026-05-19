from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from voiceclinic.agent import ClinicAgent
from voiceclinic.config import Settings
from voiceclinic.db import reset_db


def test_livekit_graph_accepts_message_state_and_returns_ai_message(tmp_path):
    pytest.importorskip("langgraph")
    messages = pytest.importorskip("langchain_core.messages")
    from voiceclinic.orchestration import build_livekit_graph

    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, settings=_settings(db_path=db_path), today=date(2026, 5, 19))
    graph = build_livekit_graph(agent)

    state = asyncio.run(
        graph.ainvoke(
            {
                "messages": [
                    messages.HumanMessage(
                        content="Quiero pedir una cita de cardiologia manana a las 10"
                    )
                ],
                "patient_phone": "+34600111222",
                "session_id": "livekit-graph-booking",
            }
        )
    )

    assert state["reply"].action == "booked"
    assert isinstance(state["messages"][-1], messages.AIMessage)
    assert state["messages"][-1].additional_kwargs["voiceclinic_action"] == "booked"


def test_livekit_graph_streams_messages_mode(tmp_path):
    pytest.importorskip("langgraph")
    messages = pytest.importorskip("langchain_core.messages")
    from voiceclinic.orchestration import build_livekit_graph

    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, settings=_settings(db_path=db_path), today=date(2026, 5, 19))
    graph = build_livekit_graph(agent)

    async def collect_chunks():
        chunks = []
        async for chunk in graph.astream(
            {
                "messages": [messages.HumanMessage(content="Que horario tiene la clinica?")],
                "patient_phone": "+34600111222",
                "session_id": "livekit-graph-streaming",
            },
            stream_mode="messages",
        ):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_chunks())

    assert chunks


def test_livekit_graph_blocks_guardrail_before_scheduling(tmp_path):
    pytest.importorskip("langgraph")
    messages = pytest.importorskip("langchain_core.messages")
    from voiceclinic.orchestration import build_livekit_graph

    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, settings=_settings(db_path=db_path), today=date(2026, 5, 19))
    graph = build_livekit_graph(agent)

    state = asyncio.run(
        graph.ainvoke(
            {
                "messages": [
                    messages.HumanMessage(
                        content="Tengo dolor en el pecho y no puedo respirar, quiero cita"
                    )
                ],
                "patient_phone": "+34600111222",
                "session_id": "livekit-graph-guardrail",
            }
        )
    )

    assert state["reply"].action == "guardrail_medical_emergency"
    assert "112" in state["messages"][-1].content


def _settings(**overrides) -> Settings:
    base = Settings(
        db_path=Path("data/clinic.db"),
        llm_provider="none",
        orchestration_mode="langgraph",
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
