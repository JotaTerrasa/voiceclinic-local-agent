# Guardrails / Guardrails Clinicos

## English

This project adapts LiveKit's background observer pattern to a local clinical
appointment agent.

The LiveKit pattern has three steps:

1. Listen to committed user turns.
2. Evaluate policy in a separate observer.
3. Inject an actionable instruction into the active agent.

In this repo, `ClinicalPolicyObserver` is independent from LiveKit so it works
in the FastAPI demo, CLI and future LiveKit sessions. The current API calls it
directly before the agent runs appointment tools. A future LiveKit integration
can feed the same observer from `conversation_item_added`.

### Current Categories

- `medical_emergency`: chest pain, breathing difficulty, stroke/heart-attack
  language, fainting, seizures or heavy bleeding. Blocks routine booking.
- `self_harm`: self-harm or suicidal ideation. Blocks routine booking.
- `diagnosis_request`: asks the agent to diagnose or interpret symptoms. Blocks
  diagnosis and offers appointment scheduling.
- `prescription_request`: asks for medication, dosage or prescription handling.
  Blocks medical instruction and offers appointment scheduling.
- `third_party_data`: asks about another patient's data. Adds a privacy warning
  before continuing.

### Why It Matters

Prompt-only safety rules compete with the agent's main job. Separating policy
observation from appointment execution makes the system easier to test and easier
to extend. It also lets the voice agent remain focused on low-latency conversation
while safety policy evolves independently.

Reference: https://livekit.com/blog/observer-pattern-voice-agent-guardrails

## Espanol

Este proyecto adapta el background observer pattern de LiveKit a un agente local
de citas clinicas.

El patron de LiveKit tiene tres pasos:

1. Escuchar los turnos confirmados del usuario.
2. Evaluar politicas en un observador separado.
3. Inyectar una instruccion accionable en el agente activo.

En este repo, `ClinicalPolicyObserver` es independiente de LiveKit para funcionar
en la demo FastAPI, CLI y futuras sesiones LiveKit. La API actual lo llama
directamente antes de que el agente ejecute herramientas de agenda. Una futura
integracion con LiveKit puede alimentar el mismo observer desde
`conversation_item_added`.

### Categorias Actuales

- `medical_emergency`: dolor en el pecho, dificultad respiratoria, lenguaje de
  ictus/infarto, desmayo, convulsiones o sangrado abundante. Bloquea la reserva
  ordinaria.
- `self_harm`: autolesion o ideacion suicida. Bloquea la reserva ordinaria.
- `diagnosis_request`: pide al agente diagnosticar o interpretar sintomas.
  Bloquea el diagnostico y ofrece cita.
- `prescription_request`: pide medicacion, dosis o gestion de receta. Bloquea la
  instruccion medica y ofrece cita.
- `third_party_data`: pide datos de otro paciente. Anade una advertencia de
  privacidad antes de continuar.

### Por Que Importa

Las reglas de seguridad solo en prompt compiten con el trabajo principal del
agente. Separar observacion de politicas y ejecucion de citas hace que el sistema
sea mas facil de probar y extender. Tambien permite que el agente de voz se
centre en conversacion de baja latencia mientras las politicas evolucionan de
forma independiente.

Referencia: https://livekit.com/blog/observer-pattern-voice-agent-guardrails
