from __future__ import annotations

import asyncio
from datetime import date

from voiceclinic.agent import ClinicAgent, parse_datetime_hint
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
