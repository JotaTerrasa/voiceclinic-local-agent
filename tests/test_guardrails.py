from __future__ import annotations

from voiceclinic.guardrails import ClinicalPolicyObserver


def test_observer_detects_medical_emergency():
    observer = ClinicalPolicyObserver()

    evaluation = observer.observe_user_turn(
        "Tengo dolor en el pecho y me cuesta respirar",
        session_id="call-1",
    )

    assert evaluation.should_interrupt is True
    assert evaluation.primary is not None
    assert evaluation.primary.key == "medical_emergency"
    assert evaluation.primary.newly_injected is True


def test_observer_deduplicates_policy_injections_per_session():
    observer = ClinicalPolicyObserver()
    observer.observe_user_turn("Tengo dolor en el pecho", session_id="call-1")

    evaluation = observer.observe_user_turn("Sigo con dolor en el pecho", session_id="call-1")

    assert evaluation.primary is not None
    assert evaluation.primary.key == "medical_emergency"
    assert evaluation.primary.newly_injected is False


def test_observer_marks_third_party_data_as_advisory():
    observer = ClinicalPolicyObserver()

    evaluation = observer.observe_user_turn("Quiero una cita para mi madre", session_id="call-1")

    assert evaluation.should_interrupt is False
    assert evaluation.primary is not None
    assert evaluation.primary.key == "third_party_data"
