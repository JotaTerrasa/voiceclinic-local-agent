from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import date, datetime, time, timedelta
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE,
  birth_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  specialty TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS slots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL REFERENCES doctors(id),
  starts_at TEXT NOT NULL,
  ends_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'free',
  UNIQUE (doctor_id, starts_at)
);

CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL REFERENCES patients(id),
  doctor_id INTEGER NOT NULL REFERENCES doctors(id),
  starts_at TEXT NOT NULL,
  ends_at TEXT NOT NULL,
  reason TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'booked',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_slots_lookup ON slots(status, starts_at);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id, status, starts_at);
"""


def connect(db_path: Path | str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: Path | str) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)


def reset_db(db_path: Path | str, start_date: date | None = None) -> None:
    path = Path(db_path)
    if path.exists():
        path.unlink()
    init_db(path)
    seed_demo_data(path, start_date=start_date)


def seed_demo_data(db_path: Path | str, start_date: date | None = None) -> None:
    start = start_date or date.today()
    with connect(db_path) as connection:
        if _table_has_rows(connection, "patients"):
            return

        connection.executemany(
            "INSERT INTO patients(full_name, phone, birth_date) VALUES (?, ?, ?)",
            [
                ("Ana Martinez", "+34600111222", "1984-03-17"),
                ("Luis Garcia", "+34600333444", "1976-11-02"),
                ("Marta Sanchez", "+34600555666", "1991-08-29"),
            ],
        )
        connection.executemany(
            "INSERT INTO doctors(full_name, specialty) VALUES (?, ?)",
            [
                ("Dra. Sofia Romero", "medicina general"),
                ("Dr. Mateo Vidal", "cardiologia"),
                ("Dra. Laura Nieto", "dermatologia"),
            ],
        )

        doctors = connection.execute("SELECT id, specialty FROM doctors").fetchall()
        slots = list(_generate_slots(doctors, start))
        connection.executemany(
            "INSERT INTO slots(doctor_id, starts_at, ends_at, status) VALUES (?, ?, ?, 'free')",
            slots,
        )


def _table_has_rows(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(f"SELECT EXISTS(SELECT 1 FROM {table})").fetchone()
    return bool(row[0])


def _generate_slots(doctors: Iterable[sqlite3.Row], start: date) -> Iterable[tuple[int, str, str]]:
    work_start = time(hour=9, minute=0)
    for day_offset in range(1, 15):
        current_day = start + timedelta(days=day_offset)
        if current_day.weekday() >= 5:
            continue
        for doctor in doctors:
            for slot_index in range(10):
                starts_at = datetime.combine(current_day, work_start) + timedelta(
                    minutes=30 * slot_index
                )
                ends_at = starts_at + timedelta(minutes=30)
                yield (
                    doctor["id"],
                    starts_at.isoformat(timespec="minutes"),
                    ends_at.isoformat(timespec="minutes"),
                )
