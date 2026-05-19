# Roadmap

## English

### Current V0

- Local scheduler and demo data.
- API chat and web demo.
- Rule-based extraction with optional Ollama support.
- Local clinical observer guardrails for emergencies, diagnosis and prescription requests.
- Local STT with faster-whisper.
- Local TTS with Piper.
- Initial Asterisk AudioSocket bridge.

### Portfolio V1

- Call dashboard with transcript, actions and latency metrics.
- Better VAD and barge-in handling.
- LiveKit `conversation_item_added` observer integration.
- Strict JSON tool calling with validation for both agent and observer.
- Post-call summary export.
- Local recording with consent.

### Simulated Production V2

- Postgres, migrations and audit trail.
- Privacy and retention policies.
- Human handoff queue.
- Self-hosted LiveKit SIP with a real SIP trunk.
- Observability: traces, metrics and dashboard.

## Espanol

### V0 Actual

- Agenda local y datos demo.
- Chat por API y demo web.
- Extraccion por reglas con soporte opcional de Ollama.
- Observer clinico local para emergencias, diagnostico y peticiones de medicacion.
- STT local con faster-whisper.
- TTS local con Piper.
- Puente Asterisk AudioSocket inicial.

### V1 Portfolio

- Panel de llamadas con transcript, acciones y metricas de latencia.
- Mejor VAD y manejo de interrupciones.
- Integracion del observer con `conversation_item_added` de LiveKit.
- Tool calling JSON estricto con validacion para agente y observer.
- Export de resumen post-llamada.
- Grabacion local con consentimiento.

### V2 Produccion Simulada

- Postgres, migraciones y auditoria.
- Politicas de privacidad y retencion.
- Cola de handoff humano.
- LiveKit SIP self-hosted con trunk SIP real.
- Observabilidad: traces, metricas y dashboard.
