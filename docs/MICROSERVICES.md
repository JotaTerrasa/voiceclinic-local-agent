# Microservices / Microservicios

## English

The repository currently runs as a modular monolith because that is the fastest
way to demo the product locally. The code is organized so it can be split into
microservices when the project moves toward an enterprise deployment.

### Target Services

| Service | Responsibility | Current implementation |
| --- | --- | --- |
| `agent-api` | Conversation entrypoint, orchestration and response assembly | `voiceclinic.api`, `voiceclinic.agent`, `voiceclinic.orchestration` |
| `scheduler-service` | Appointment availability, booking, rescheduling and cancellation | `voiceclinic.scheduling`, `voiceclinic.db` |
| `guardrails-service` | Clinical policy detection and safety directives | `voiceclinic.guardrails` |
| `voice-gateway` | SIP/WebRTC audio bridge, STT and TTS | `voiceclinic.telephony`, `voiceclinic.voice` |
| `post-call-functions` | Summaries, audit export and notifications | Future Azure Functions |

### Service Contracts

- `agent-api` should call `scheduler-service` through HTTP or async commands,
  never by direct database access.
- `scheduler-service` should own all appointment transactions.
- `guardrails-service` should be stateless or store only policy event metadata.
- `voice-gateway` should not contain scheduling logic.
- background jobs should consume events from a queue rather than blocking the
  live conversation.

### Migration Path

1. Keep the current modular monolith for local demo speed.
2. Replace direct `Scheduler` calls in `ClinicAgent` with an HTTP client.
3. Move `voiceclinic.scheduling` and `voiceclinic.db` into `scheduler-service`.
4. Move `ClinicalPolicyObserver` into `guardrails-service`.
5. Emit post-call and appointment events to Service Bus.
6. Add Azure Functions for summaries, audit export and notifications.

## Español

El repositorio funciona actualmente como monolito modular porque es la forma más
rápida de demostrar el producto en local. El código está organizado para poder
separarse en microservicios cuando el proyecto avance hacia un despliegue
empresarial.

### Servicios objetivo

| Servicio | Responsabilidad | Implementación actual |
| --- | --- | --- |
| `agent-api` | Entrada conversacional, orquestación y respuesta final | `voiceclinic.api`, `voiceclinic.agent`, `voiceclinic.orchestration` |
| `scheduler-service` | Disponibilidad, reservas, cambios y cancelaciones | `voiceclinic.scheduling`, `voiceclinic.db` |
| `guardrails-service` | Detección de políticas clínicas y directivas de seguridad | `voiceclinic.guardrails` |
| `voice-gateway` | Puente de audio SIP/WebRTC, STT y TTS | `voiceclinic.telephony`, `voiceclinic.voice` |
| `post-call-functions` | Resúmenes, auditoría y notificaciones | Futuras Azure Functions |

### Contratos de servicio

- `agent-api` debería llamar a `scheduler-service` por HTTP o comandos
  asíncronos, nunca mediante acceso directo a base de datos.
- `scheduler-service` debería ser dueño de todas las transacciones de agenda.
- `guardrails-service` debería ser stateless o guardar solo metadatos de eventos
  de política.
- `voice-gateway` no debería contener lógica de agenda.
- los trabajos en segundo plano deberían consumir eventos de una cola en lugar
  de bloquear la conversación en vivo.

### Camino de migración

1. Mantener el monolito modular actual para velocidad de demo local.
2. Sustituir las llamadas directas a `Scheduler` en `ClinicAgent` por un cliente HTTP.
3. Mover `voiceclinic.scheduling` y `voiceclinic.db` a `scheduler-service`.
4. Mover `ClinicalPolicyObserver` a `guardrails-service`.
5. Emitir eventos post-llamada y eventos de cita a Service Bus.
6. Añadir Azure Functions para resúmenes, auditoría y notificaciones.
