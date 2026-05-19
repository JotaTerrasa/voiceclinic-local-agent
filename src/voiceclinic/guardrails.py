from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import ClassVar

from voiceclinic.text import contains_any, normalize_text


@dataclass(frozen=True)
class PolicyDirective:
    key: str
    severity: str
    details: str
    instruction: str
    response_text: str
    blocks_action: bool
    newly_injected: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PolicyEvaluation:
    session_id: str
    directives: tuple[PolicyDirective, ...]

    @property
    def primary(self) -> PolicyDirective | None:
        return self.directives[0] if self.directives else None

    @property
    def should_interrupt(self) -> bool:
        return bool(self.primary and self.primary.blocks_action)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "should_interrupt": self.should_interrupt,
            "directives": [directive.to_dict() for directive in self.directives],
        }


class ClinicalPolicyObserver:
    """Domain guardrail observer for a clinical appointment agent.

    The observer is intentionally independent from LiveKit. LiveKit can feed it
    from `conversation_item_added`, while the local API feeds it directly on
    every user turn.
    """

    DEFAULT_SESSION_ID: ClassVar[str] = "default"
    MAX_TURNS: ClassVar[int] = 10

    def __init__(self) -> None:
        self.conversation_history: dict[str, list[str]] = {}
        self.injected_directives: dict[str, set[str]] = {}

    def clear(self) -> None:
        self.conversation_history.clear()
        self.injected_directives.clear()

    def observe_user_turn(self, text: str, session_id: str | None = None) -> PolicyEvaluation:
        session_key = session_id or self.DEFAULT_SESSION_ID
        history = self.conversation_history.setdefault(session_key, [])
        history.append(text)
        del history[:-self.MAX_TURNS]

        detected = self._evaluate_rules("\n".join(history[-3:]))
        injected = self.injected_directives.setdefault(session_key, set())
        directives = []
        for directive in detected:
            directives.append(
                PolicyDirective(
                    key=directive.key,
                    severity=directive.severity,
                    details=directive.details,
                    instruction=directive.instruction,
                    response_text=directive.response_text,
                    blocks_action=directive.blocks_action,
                    newly_injected=directive.key not in injected,
                )
            )
            injected.add(directive.key)

        return PolicyEvaluation(session_id=session_key, directives=tuple(directives))

    def _evaluate_rules(self, transcript: str) -> tuple[PolicyDirective, ...]:
        normalized = normalize_text(transcript)
        directives: list[PolicyDirective] = []

        if contains_any(
            normalized,
            (
                "me quiero suicidar",
                "quiero morirme",
                "quiero morir",
                "hacerme dano",
                "autolesion",
                "suicide",
                "kill myself",
                "self harm",
            ),
        ):
            directives.append(GUARDRAIL_DIRECTIVES["self_harm"])

        if contains_any(
            normalized,
            (
                "dolor en el pecho",
                "no puedo respirar",
                "me cuesta respirar",
                "se ha desmayado",
                "perdida de conciencia",
                "convulsion",
                "ictus",
                "infarto",
                "sangrado abundante",
                "chest pain",
                "cannot breathe",
                "stroke",
                "heart attack",
            ),
        ):
            directives.append(GUARDRAIL_DIRECTIVES["medical_emergency"])

        if _is_prescription_request(normalized):
            directives.append(GUARDRAIL_DIRECTIVES["prescription_request"])

        if _is_diagnosis_request(normalized):
            directives.append(GUARDRAIL_DIRECTIVES["diagnosis_request"])

        if contains_any(
            normalized,
            (
                "para mi hijo",
                "para mi hija",
                "para mi madre",
                "para mi padre",
                "datos de otro paciente",
                "historial de otra persona",
                "for my child",
                "for my mother",
                "for my father",
            ),
        ):
            directives.append(GUARDRAIL_DIRECTIVES["third_party_data"])

        return tuple(_dedupe_by_key(directives))


def _is_diagnosis_request(normalized: str) -> bool:
    return contains_any(
        normalized,
        (
            "que tengo",
            "que enfermedad",
            "diagnostic",
            "diagnostico",
            "es grave",
            "me puedes decir si",
            "do i have",
            "what do i have",
        ),
    )


def _is_prescription_request(normalized: str) -> bool:
    if not contains_any(
        normalized,
        (
            "receta",
            "recetar",
            "dosis",
            "medicamento",
            "antibiotico",
            "tratamiento",
            "prescription",
            "dosage",
            "antibiotic",
        ),
    ):
        return False
    return contains_any(
        normalized,
        (
            "dime",
            "puedo tomar",
            "que tomo",
            "cuanto",
            "mandame",
            "necesito que me recetes",
            "what should i take",
            "can i take",
            "send me",
        ),
    )


def _dedupe_by_key(directives: list[PolicyDirective]) -> list[PolicyDirective]:
    seen: set[str] = set()
    deduped: list[PolicyDirective] = []
    for directive in directives:
        if directive.key in seen:
            continue
        seen.add(directive.key)
        deduped.append(directive)
    return deduped


GUARDRAIL_DIRECTIVES = {
    "self_harm": PolicyDirective(
        key="self_harm",
        severity="critical",
        details="The caller may be describing self-harm or suicidal ideation.",
        instruction=(
            "[POLICY: SELF HARM] Stop appointment handling. Encourage the caller to "
            "contact emergency services immediately and stay with another person if possible."
        ),
        response_text=(
            "Siento que estes pasando por esto. No puedo gestionarlo como una cita normal. "
            "Si estas en peligro inmediato, llama al 112 o a tu servicio local de emergencias "
            "ahora. Si puedes, quedate acompanado y pide ayuda a alguien cercano."
        ),
        blocks_action=True,
    ),
    "medical_emergency": PolicyDirective(
        key="medical_emergency",
        severity="critical",
        details="The caller described symptoms that may require emergency care.",
        instruction=(
            "[POLICY: MEDICAL EMERGENCY] Do not book a routine appointment. Direct the "
            "caller to emergency services or urgent care immediately."
        ),
        response_text=(
            "Por los sintomas que describes, esto puede requerir atencion urgente. "
            "No deberias esperar a una cita ordinaria. Llama al 112 o acude a urgencias "
            "ahora mismo."
        ),
        blocks_action=True,
    ),
    "diagnosis_request": PolicyDirective(
        key="diagnosis_request",
        severity="high",
        details="The caller is asking for diagnosis or clinical interpretation.",
        instruction=(
            "[POLICY: DIAGNOSIS REQUEST] Do not diagnose. Offer appointment scheduling "
            "or recommend urgent care if symptoms are severe."
        ),
        response_text=(
            "No puedo darte un diagnostico por telefono. Puedo ayudarte a reservar una "
            "cita con un profesional para que valore tus sintomas."
        ),
        blocks_action=True,
    ),
    "prescription_request": PolicyDirective(
        key="prescription_request",
        severity="high",
        details="The caller is asking for medication, dosage or prescription instructions.",
        instruction=(
            "[POLICY: PRESCRIPTION REQUEST] Do not prescribe medication or dosage. "
            "Offer appointment scheduling with a clinician."
        ),
        response_text=(
            "No puedo indicar medicacion, dosis ni emitir recetas por esta via. "
            "Puedo ayudarte a reservar una cita para revisarlo con un medico."
        ),
        blocks_action=True,
    ),
    "third_party_data": PolicyDirective(
        key="third_party_data",
        severity="medium",
        details="The caller may be asking about another patient's information.",
        instruction=(
            "[POLICY: THIRD PARTY DATA] Verify identity and relationship before "
            "disclosing or changing patient information."
        ),
        response_text=(
            "Por privacidad, antes de consultar o cambiar datos de otra persona hay que "
            "verificar identidad y autorizacion."
        ),
        blocks_action=False,
    ),
}
