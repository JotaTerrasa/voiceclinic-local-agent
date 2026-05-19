from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import date
from pathlib import Path

from voiceclinic.agent import ClinicAgent, parse_datetime_hint
from voiceclinic.config import Settings
from voiceclinic.db import reset_db


def test_parse_spanish_datetime_hint():
    parsed = parse_datetime_hint("manana a las 10", today=date(2026, 5, 19))

    assert parsed.isoformat(timespec="minutes") == "2026-05-20T10:00"


def test_agent_books_cardiology_appointment(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, today=date(2026, 5, 19))

    reply = asyncio.run(
        agent.handle_text(
            "Quiero pedir una cita de cardiologia manana a las 10",
            patient_phone="+34600111222",
        )
    )

    assert reply.action == "booked"
    assert reply.data["specialty"] == "cardiologia"
    assert reply.data["starts_at"] == "2026-05-20T10:00"


def test_agent_cancels_next_appointment(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, today=date(2026, 5, 19))
    asyncio.run(agent.handle_text("Necesito una cita de dermatologia manana a las 11"))

    reply = asyncio.run(agent.handle_text("Quiero cancelar mi cita"))

    assert reply.action == "cancelled"
    assert reply.data["status"] == "cancelled"


def test_agent_blocks_routine_booking_for_emergency_symptoms(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, today=date(2026, 5, 19))

    reply = asyncio.run(
        agent.handle_text(
            "Tengo dolor en el pecho y no puedo respirar, quiero una cita manana",
            patient_phone="+34600111222",
            session_id="call-1",
        )
    )

    assert reply.action == "guardrail_medical_emergency"
    assert "112" in reply.text
    assert reply.data["guardrails"]["should_interrupt"] is True


def test_agent_does_not_answer_diagnosis_requests(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    agent = ClinicAgent(db_path, today=date(2026, 5, 19))

    reply = asyncio.run(
        agent.handle_text(
            "Me puedes decir si lo que tengo es grave?",
            patient_phone="+34600111222",
            session_id="call-2",
        )
    )

    assert reply.action == "guardrail_diagnosis_request"
    assert "No puedo darte un diagnostico" in reply.text


def test_agent_langgraph_mode_falls_back_or_runs_when_optional_extra_is_available(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    settings = _settings(db_path=db_path, orchestration_mode="langgraph", llm_provider="none")
    agent = ClinicAgent(db_path, settings=settings, today=date(2026, 5, 19))

    reply = asyncio.run(
        agent.handle_text(
            "Quiero pedir una cita de medicina general manana a las 9",
            patient_phone="+34600111222",
            session_id="langgraph-call",
        )
    )

    assert reply.action == "booked"
    assert reply.data["specialty"] == "medicina general"


def _settings(**overrides) -> Settings:
    base = Settings(
        db_path=Path("data/clinic.db"),
        llm_provider="none",
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
