from __future__ import annotations

from datetime import date, datetime

import pytest

from voiceclinic.db import reset_db
from voiceclinic.scheduling import Scheduler, SchedulingError


def test_booking_consumes_slot(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    scheduler = Scheduler(db_path)

    slots = scheduler.list_available_slots(
        specialty="cardiologia",
        after=datetime(2026, 5, 20, 9, 0),
        limit=1,
    )
    appointment = scheduler.book_slot(patient_id=1, slot_id=slots[0].id, reason="Revision")

    assert appointment.status == "booked"
    assert appointment.specialty == "cardiologia"
    assert appointment.starts_at == "2026-05-20T09:00"
    with pytest.raises(SchedulingError):
        scheduler.book_slot(patient_id=1, slot_id=slots[0].id, reason="Duplicada")


def test_reschedule_releases_previous_slot(tmp_path):
    db_path = tmp_path / "clinic.db"
    reset_db(db_path, start_date=date(2026, 5, 19))
    scheduler = Scheduler(db_path)

    appointment = scheduler.book_first_available(
        patient_phone="+34600111222",
        specialty="dermatologia",
        after=datetime(2026, 5, 20, 9, 0),
        reason="Consulta",
    )
    moved = scheduler.reschedule_next_appointment(
        patient_phone="+34600111222",
        after=datetime(2026, 5, 21, 9, 0),
    )

    assert moved.id == appointment.id
    assert moved.starts_at == "2026-05-21T09:00"
    released = scheduler.list_available_slots(
        specialty="dermatologia",
        after=datetime(2026, 5, 20, 9, 0),
        limit=1,
    )
    assert released[0].starts_at == "2026-05-20T09:00"
