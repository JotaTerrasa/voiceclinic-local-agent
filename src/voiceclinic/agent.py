from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

from voiceclinic.config import Settings
from voiceclinic.guardrails import ClinicalPolicyObserver, PolicyEvaluation
from voiceclinic.llm import build_llm_client
from voiceclinic.scheduling import Scheduler, SchedulingError, format_appointment
from voiceclinic.text import contains_any, normalize_text

SPECIALTIES = {
    "general": "medicina general",
    "medicina": "medicina general",
    "medicina general": "medicina general",
    "cabecera": "medicina general",
    "cardio": "cardiologia",
    "cardiologia": "cardiologia",
    "cardiologo": "cardiologia",
    "derma": "dermatologia",
    "dermatologia": "dermatologia",
    "dermatologo": "dermatologia",
}


FAQ = {
    "horario": "La clinica atiende de lunes a viernes de 09:00 a 14:00.",
    "documentacion": "Para la cita trae DNI o tarjeta sanitaria y cualquier informe reciente.",
    "urgencia": "Si es una urgencia medica, llama al 112 o acude a urgencias.",
}


@dataclass(frozen=True)
class AgentReply:
    text: str
    action: str
    data: dict


@dataclass(frozen=True)
class Intent:
    name: str
    specialty: str | None = None
    when: datetime | None = None
    reason: str = "Consulta solicitada por telefono"


class ClinicAgent:
    def __init__(
        self,
        db_path: Path | str,
        settings: Settings | None = None,
        policy_observer: ClinicalPolicyObserver | None = None,
        today: date | None = None,
    ):
        self.scheduler = Scheduler(db_path)
        self.settings = settings
        self.policy_observer = policy_observer or ClinicalPolicyObserver()
        self.today = today
        self.llm = build_llm_client(settings)

    async def handle_text(
        self,
        message: str,
        patient_phone: str = "+34600111222",
        session_id: str | None = None,
    ) -> AgentReply:
        if self.settings and self.settings.orchestration_mode == "langgraph":
            try:
                from voiceclinic.orchestration import LangGraphClinicOrchestrator

                return await LangGraphClinicOrchestrator(self).run(
                    message=message,
                    patient_phone=patient_phone,
                    session_id=session_id,
                )
            except ImportError:
                pass

        return await self._handle_text_direct(
            message=message,
            patient_phone=patient_phone,
            session_id=session_id,
        )

    async def _handle_text_direct(
        self,
        message: str,
        patient_phone: str,
        session_id: str | None,
    ) -> AgentReply:
        policy = self._observe_policy(message, session_id)
        if policy.should_interrupt and policy.primary:
            return self._guardrail_reply(policy)

        intent = await self._infer_intent(message)
        return await self._execute_intent(intent, policy, patient_phone, message)

    def _observe_policy(self, message: str, session_id: str | None) -> PolicyEvaluation:
        return self.policy_observer.observe_user_turn(message, session_id=session_id)

    def _guardrail_reply(self, policy: PolicyEvaluation) -> AgentReply:
        if not policy.primary:
            return AgentReply(
                text="No puedo continuar con esta solicitud.",
                action="guardrail",
                data={},
            )
        return AgentReply(
            text=policy.primary.response_text,
            action=f"guardrail_{policy.primary.key}",
            data={"guardrails": policy.to_dict()},
        )

    async def _execute_intent(
        self,
        intent: Intent,
        policy: PolicyEvaluation,
        patient_phone: str,
        message: str,
    ) -> AgentReply:
        try:
            if intent.name == "book":
                specialty = intent.specialty or "medicina general"
                when = intent.when or self._default_after()
                appointment = self.scheduler.book_first_available(
                    patient_phone=patient_phone,
                    specialty=specialty,
                    after=when,
                    reason=intent.reason,
                )
                text = f"Perfecto, te he reservado una cita el {format_appointment(appointment)}."
                return self._with_policy(
                    AgentReply(text=text, action="booked", data=asdict(appointment)),
                    policy,
                )

            if intent.name == "reschedule":
                appointment = self.scheduler.reschedule_next_appointment(
                    patient_phone=patient_phone,
                    after=intent.when or self._default_after(),
                    specialty=intent.specialty,
                )
                text = f"Listo, he cambiado tu cita al {format_appointment(appointment)}."
                return self._with_policy(
                    AgentReply(text=text, action="rescheduled", data=asdict(appointment)),
                    policy,
                )

            if intent.name == "cancel":
                appointment = self.scheduler.cancel_next_appointment(patient_phone)
                text = f"He cancelado tu cita del {format_appointment(appointment)}."
                return self._with_policy(
                    AgentReply(text=text, action="cancelled", data=asdict(appointment)),
                    policy,
                )

            if intent.name == "list":
                appointments = self.scheduler.list_patient_appointments(patient_phone)
                if not appointments:
                    return self._with_policy(
                        AgentReply(
                            text="No veo citas activas asociadas a tu telefono.",
                            action="listed",
                            data={"appointments": []},
                        ),
                        policy,
                    )
                formatted = "; ".join(format_appointment(item) for item in appointments)
                return self._with_policy(
                    AgentReply(
                        text=f"Tienes estas citas activas: {formatted}.",
                        action="listed",
                        data={"appointments": [asdict(item) for item in appointments]},
                    ),
                    policy,
                )

            if intent.name == "faq":
                answer = self._answer_faq(message)
                return self._with_policy(AgentReply(text=answer, action="faq", data={}), policy)

            slots = self.scheduler.list_available_slots(
                specialty=intent.specialty,
                after=intent.when or self._default_after(),
                limit=3,
            )
            if not slots:
                return self._with_policy(
                    AgentReply(
                        text="No encuentro huecos disponibles con esos criterios.",
                        action="availability",
                        data={"slots": []},
                    ),
                    policy,
                )
            formatted = "; ".join(
                f"{slot.starts_at.replace('T', ' ')} con {slot.doctor_name}"
                for slot in slots
            )
            return self._with_policy(
                AgentReply(
                    text=f"Los primeros huecos disponibles son: {formatted}.",
                    action="availability",
                    data={"slots": [asdict(slot) for slot in slots]},
                ),
                policy,
            )
        except SchedulingError as exc:
            return self._with_policy(AgentReply(text=str(exc), action="error", data={}), policy)

    def _with_policy(self, reply: AgentReply, policy: PolicyEvaluation) -> AgentReply:
        if not policy.directives:
            return reply

        data = dict(reply.data)
        data["guardrails"] = policy.to_dict()
        advisory = next(
            (directive for directive in policy.directives if not directive.blocks_action),
            None,
        )
        text = reply.text
        if advisory:
            text = f"{advisory.response_text} {reply.text}"
        return AgentReply(text=text, action=reply.action, data=data)

    async def _infer_intent(self, message: str) -> Intent:
        if self.llm:
            extracted = await self._infer_intent_with_llm(message)
            if extracted:
                return extracted
        return self._infer_intent_with_rules(message)

    async def _infer_intent_with_llm(self, message: str) -> Intent | None:
        system = (
            "Extrae la intencion de una llamada a una clinica. "
            "Responde solo JSON con: intent, specialty, date_hint, time_hint, reason. "
            "intent puede ser book, reschedule, cancel, list, availability o faq. "
            "specialty puede ser medicina general, cardiologia, dermatologia o null."
        )
        payload = await self.llm.extract_json(system, message) if self.llm else None
        if not payload:
            return None

        intent_name = str(payload.get("intent", "")).strip().lower()
        if intent_name not in {"book", "reschedule", "cancel", "list", "availability", "faq"}:
            return None
        specialty = _normalize_specialty(payload.get("specialty"))
        when = parse_datetime_hint(
            " ".join(str(payload.get(key, "") or "") for key in ("date_hint", "time_hint")),
            today=self.today,
        )
        return Intent(
            name=intent_name,
            specialty=specialty,
            when=when,
            reason=str(payload.get("reason") or "Consulta solicitada por telefono"),
        )

    def _infer_intent_with_rules(self, message: str) -> Intent:
        normalized = normalize_text(message)
        specialty = _detect_specialty(normalized)
        when = parse_datetime_hint(message, today=self.today)

        if contains_any(normalized, ("cancel", "anula", "anular", "borrar")):
            return Intent(name="cancel", specialty=specialty, when=when)
        if contains_any(normalized, ("cambiar", "cambio", "mover", "modificar", "reprogramar")):
            return Intent(name="reschedule", specialty=specialty, when=when)
        if contains_any(normalized, ("mis citas", "que citas", "tengo cita", "consultar cita")):
            return Intent(name="list", specialty=specialty, when=when)
        if contains_any(normalized, ("hueco", "disponible", "disponibilidad")):
            return Intent(name="availability", specialty=specialty, when=when)
        if contains_any(
            normalized,
            ("horario", "documentacion", "documentos", "urgencia", "urgente"),
        ):
            return Intent(name="faq", specialty=specialty, when=when)
        if contains_any(normalized, ("cita", "reserv", "pedir", "agendar", "consulta")):
            return Intent(name="book", specialty=specialty, when=when)
        return Intent(name="faq", specialty=specialty, when=when)

    def _answer_faq(self, message: str) -> str:
        normalized = normalize_text(message)
        if "urg" in normalized:
            return FAQ["urgencia"]
        if "document" in normalized or "dni" in normalized or "tarjeta" in normalized:
            return FAQ["documentacion"]
        return FAQ["horario"]

    def _default_after(self) -> datetime:
        base = self.today or date.today()
        return datetime.combine(base + timedelta(days=1), time(hour=9, minute=0))


def _detect_specialty(normalized_message: str) -> str | None:
    for needle, specialty in SPECIALTIES.items():
        if needle in normalized_message:
            return specialty
    return None


def _normalize_specialty(value: object) -> str | None:
    if not value:
        return None
    normalized = normalize_text(str(value))
    return SPECIALTIES.get(normalized) or _detect_specialty(normalized)


def parse_datetime_hint(value: str, today: date | None = None) -> datetime | None:
    normalized = normalize_text(value)
    base = today or date.today()
    iso_match = re.search(r"(20\d{2}-\d{2}-\d{2})[ t](\d{1,2}:\d{2})", normalized)
    if iso_match:
        return datetime.fromisoformat(f"{iso_match.group(1)}T{iso_match.group(2)}")
    parsed_date = _parse_date(normalized, base)
    parsed_time = _parse_time(normalized) or time(hour=9, minute=0)
    if parsed_date:
        return datetime.combine(parsed_date, parsed_time)
    return None


def _parse_date(value: str, base: date) -> date | None:
    if "pasado manana" in value:
        return base + timedelta(days=2)
    if "manana" in value:
        return base + timedelta(days=1)
    if "hoy" in value:
        return base

    iso_match = re.search(r"(20\d{2})-(\d{2})-(\d{2})", value)
    if iso_match:
        return date(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))

    slash_match = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(20\d{2}))?\b", value)
    if slash_match:
        year = int(slash_match.group(3)) if slash_match.group(3) else base.year
        return date(year, int(slash_match.group(2)), int(slash_match.group(1)))

    weekdays = {
        "lunes": 0,
        "martes": 1,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4,
    }
    for name, weekday in weekdays.items():
        if name in value:
            days_ahead = (weekday - base.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return base + timedelta(days=days_ahead)
    return None


def _parse_time(value: str) -> time | None:
    match = re.search(r"\b(\d{1,2}):(\d{2})\b", value)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour=hour, minute=minute)

    match = re.search(r"\b(?:a las|las)\s+(\d{1,2})(?:\s+y\s+(\d{2}))?\b", value)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour=hour, minute=minute)
    return None
