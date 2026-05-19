from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from voiceclinic.db import connect
from voiceclinic.text import normalize_text


class SchedulingError(RuntimeError):
    pass


@dataclass(frozen=True)
class Patient:
    id: int
    full_name: str
    phone: str
    birth_date: str


@dataclass(frozen=True)
class Slot:
    id: int
    doctor_id: int
    doctor_name: str
    specialty: str
    starts_at: str
    ends_at: str


@dataclass(frozen=True)
class Appointment:
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    specialty: str
    starts_at: str
    ends_at: str
    reason: str
    status: str


class Scheduler:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)

    def find_patient_by_phone(self, phone: str) -> Patient | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT id, full_name, phone, birth_date FROM patients WHERE phone = ?",
                (phone,),
            ).fetchone()
        return _patient_from_row(row) if row else None

    def list_patients(self) -> list[Patient]:
        with connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, full_name, phone, birth_date FROM patients ORDER BY full_name"
            ).fetchall()
        return [_patient_from_row(row) for row in rows]

    def list_available_slots(
        self,
        specialty: str | None = None,
        after: datetime | None = None,
        limit: int = 5,
    ) -> list[Slot]:
        filters = ["s.status = 'free'"]
        params: list[str] = []
        if specialty:
            filters.append("d.specialty = ?")
            params.append(normalize_text(specialty))
        if after:
            filters.append("s.starts_at >= ?")
            params.append(after.isoformat(timespec="minutes"))

        query = f"""
            SELECT s.id, s.doctor_id, d.full_name AS doctor_name,
                   d.specialty, s.starts_at, s.ends_at
            FROM slots s
            JOIN doctors d ON d.id = s.doctor_id
            WHERE {' AND '.join(filters)}
            ORDER BY s.starts_at ASC
            LIMIT ?
        """
        params.append(str(limit))
        with connect(self.db_path) as connection:
            rows = connection.execute(query, params).fetchall()
        return [_slot_from_row(row) for row in rows]

    def book_first_available(
        self,
        patient_phone: str,
        specialty: str,
        after: datetime,
        reason: str,
    ) -> Appointment:
        patient = self.find_patient_by_phone(patient_phone)
        if not patient:
            raise SchedulingError("No encuentro un paciente con ese telefono.")
        slots = self.list_available_slots(specialty=specialty, after=after, limit=1)
        if not slots:
            raise SchedulingError("No hay huecos disponibles para esa especialidad.")
        return self.book_slot(patient.id, slots[0].id, reason=reason)

    def book_slot(self, patient_id: int, slot_id: int, reason: str) -> Appointment:
        now = datetime.now(UTC).isoformat(timespec="seconds")
        with connect(self.db_path) as connection:
            slot = connection.execute(
                """
                SELECT s.id, s.doctor_id, d.full_name AS doctor_name,
                       d.specialty, s.starts_at, s.ends_at
                FROM slots s
                JOIN doctors d ON d.id = s.doctor_id
                WHERE s.id = ? AND s.status = 'free'
                """,
                (slot_id,),
            ).fetchone()
            if not slot:
                raise SchedulingError("Ese hueco ya no esta disponible.")

            cursor = connection.execute(
                """
                INSERT INTO appointments(
                    patient_id, doctor_id, starts_at, ends_at,
                    reason, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, 'booked', ?, ?)
                """,
                (
                    patient_id,
                    slot["doctor_id"],
                    slot["starts_at"],
                    slot["ends_at"],
                    reason,
                    now,
                    now,
                ),
            )
            connection.execute("UPDATE slots SET status = 'booked' WHERE id = ?", (slot_id,))
            appointment_id = cursor.lastrowid
            connection.commit()
        return self.get_appointment(appointment_id)

    def list_patient_appointments(
        self,
        patient_phone: str,
        include_cancelled: bool = False,
    ) -> list[Appointment]:
        patient = self.find_patient_by_phone(patient_phone)
        if not patient:
            return []
        status_filter = "" if include_cancelled else "AND a.status != 'cancelled'"
        with connect(self.db_path) as connection:
            rows = connection.execute(
                f"""
                SELECT a.id, a.patient_id, p.full_name AS patient_name, a.doctor_id,
                       d.full_name AS doctor_name, d.specialty, a.starts_at,
                       a.ends_at, a.reason, a.status
                FROM appointments a
                JOIN patients p ON p.id = a.patient_id
                JOIN doctors d ON d.id = a.doctor_id
                WHERE a.patient_id = ? {status_filter}
                ORDER BY a.starts_at ASC
                """,
                (patient.id,),
            ).fetchall()
        return [_appointment_from_row(row) for row in rows]

    def get_appointment(self, appointment_id: int) -> Appointment:
        with connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT a.id, a.patient_id, p.full_name AS patient_name, a.doctor_id,
                       d.full_name AS doctor_name, d.specialty, a.starts_at,
                       a.ends_at, a.reason, a.status
                FROM appointments a
                JOIN patients p ON p.id = a.patient_id
                JOIN doctors d ON d.id = a.doctor_id
                WHERE a.id = ?
                """,
                (appointment_id,),
            ).fetchone()
        if not row:
            raise SchedulingError("No encuentro esa cita.")
        return _appointment_from_row(row)

    def cancel_next_appointment(self, patient_phone: str) -> Appointment:
        appointments = [
            item
            for item in self.list_patient_appointments(patient_phone)
            if item.status == "booked"
        ]
        if not appointments:
            raise SchedulingError("No hay citas activas para cancelar.")
        appointment = appointments[0]
        now = datetime.now(UTC).isoformat(timespec="seconds")
        with connect(self.db_path) as connection:
            connection.execute(
                "UPDATE appointments SET status = 'cancelled', updated_at = ? WHERE id = ?",
                (now, appointment.id),
            )
            connection.execute(
                """
                UPDATE slots
                SET status = 'free'
                WHERE doctor_id = ? AND starts_at = ?
                """,
                (appointment.doctor_id, appointment.starts_at),
            )
            connection.commit()
        return self.get_appointment(appointment.id)

    def reschedule_next_appointment(
        self,
        patient_phone: str,
        after: datetime,
        specialty: str | None = None,
    ) -> Appointment:
        appointments = [
            item
            for item in self.list_patient_appointments(patient_phone)
            if item.status == "booked"
        ]
        if not appointments:
            raise SchedulingError("No hay citas activas para cambiar.")
        appointment = appointments[0]
        target_specialty = specialty or appointment.specialty
        slots = self.list_available_slots(specialty=target_specialty, after=after, limit=1)
        if not slots:
            raise SchedulingError("No hay huecos disponibles para cambiar la cita.")
        new_slot = slots[0]
        now = datetime.now(UTC).isoformat(timespec="seconds")

        with connect(self.db_path) as connection:
            connection.execute(
                "UPDATE slots SET status = 'free' WHERE doctor_id = ? AND starts_at = ?",
                (appointment.doctor_id, appointment.starts_at),
            )
            connection.execute("UPDATE slots SET status = 'booked' WHERE id = ?", (new_slot.id,))
            connection.execute(
                """
                UPDATE appointments
                SET doctor_id = ?, starts_at = ?, ends_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_slot.doctor_id, new_slot.starts_at, new_slot.ends_at, now, appointment.id),
            )
            connection.commit()
        return self.get_appointment(appointment.id)


def _patient_from_row(row) -> Patient:
    return Patient(
        id=row["id"],
        full_name=row["full_name"],
        phone=row["phone"],
        birth_date=row["birth_date"],
    )


def _slot_from_row(row) -> Slot:
    return Slot(
        id=row["id"],
        doctor_id=row["doctor_id"],
        doctor_name=row["doctor_name"],
        specialty=row["specialty"],
        starts_at=row["starts_at"],
        ends_at=row["ends_at"],
    )


def _appointment_from_row(row) -> Appointment:
    return Appointment(
        id=row["id"],
        patient_id=row["patient_id"],
        patient_name=row["patient_name"],
        doctor_id=row["doctor_id"],
        doctor_name=row["doctor_name"],
        specialty=row["specialty"],
        starts_at=row["starts_at"],
        ends_at=row["ends_at"],
        reason=row["reason"],
        status=row["status"],
    )


def format_appointment(appointment: Appointment) -> str:
    starts_at = datetime.fromisoformat(appointment.starts_at)
    return (
        f"{starts_at:%d/%m/%Y a las %H:%M} con {appointment.doctor_name} "
        f"({appointment.specialty})"
    )


def next_business_datetime(start: datetime) -> datetime:
    candidate = start + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate.replace(hour=9, minute=0, second=0, microsecond=0)
