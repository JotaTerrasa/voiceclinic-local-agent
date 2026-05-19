# Roadmap

## English

### Current version

- Local scheduling domain with demo patients, doctors, slots and appointments.
- FastAPI backend and browser-based demo.
- Deterministic intent handling with optional Ollama-based extraction.
- `qwen3:30b` as the recommended local LLM for a single RTX 4090.
- Clinical guardrail observer for emergencies, self-harm, diagnosis requests,
  prescription requests and third-party data.
- Optional local STT with faster-whisper.
- Optional local TTS with Piper.
- Initial Asterisk AudioSocket bridge for local SIP calls.
- Bilingual documentation in English and Spanish.

### Portfolio V1

- Call dashboard with transcript, actions, latency and guardrail events.
- Better voice activity detection and interruption handling.
- LiveKit Agents integration using `conversation_item_added` for the observer.
- Structured tool-calling schema with stricter validation.
- Post-call summary export.
- Local call recording with explicit consent.
- Docker profile for GPU-enabled Ollama.

### Simulated production V2

- Postgres, migrations and a full audit trail.
- Stronger patient identity verification.
- Human handoff queue.
- Privacy and data-retention policies.
- Observability with traces, metrics and dashboards.
- Self-hosted LiveKit SIP path with a real SIP trunk.
- Evaluation suite for appointments, guardrails and conversation quality.

## Español

### Versión actual

- Dominio local de agenda con pacientes, doctores, huecos y citas de demostración.
- Backend FastAPI y demo en navegador.
- Manejo determinista de intención con extracción opcional mediante Ollama.
- `qwen3:30b` como LLM local recomendado para una RTX 4090.
- Observador de guardrails clínicos para emergencias, autolesión, diagnóstico,
  recetas y datos de terceros.
- STT local opcional con faster-whisper.
- TTS local opcional con Piper.
- Puente inicial de Asterisk AudioSocket para llamadas SIP locales.
- Documentación bilingüe en inglés y español.

### V1 de portfolio

- Panel de llamadas con transcript, acciones, latencia y eventos de guardrails.
- Mejor detección de actividad de voz y manejo de interrupciones.
- Integración con LiveKit Agents usando `conversation_item_added` para el observador.
- Esquema de tool calling estructurado con validación más estricta.
- Exportación de resumen posterior a la llamada.
- Grabación local con consentimiento explícito.
- Perfil Docker para Ollama con GPU.

### V2 de producción simulada

- Postgres, migraciones y auditoría completa.
- Verificación de identidad del paciente más robusta.
- Cola de derivación a humano.
- Políticas de privacidad y retención de datos.
- Observabilidad con trazas, métricas y dashboards.
- Ruta LiveKit SIP autoalojada con un trunk SIP real.
- Suite de evaluación para citas, guardrails y calidad conversacional.
