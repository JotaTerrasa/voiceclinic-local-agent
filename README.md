# VoiceClinic Local Agent

Local, self-hosted voice agent for patient appointment management. The project
is designed as an AI portfolio piece: it shows how to combine local LLMs, local
speech components, telephony integration, clinical guardrails and a simple
scheduling backend without relying on hosted voice-agent platforms.

This is a demo system. It is not medical software and must not be used to manage
real patients without proper clinical, legal, privacy and security review.

## English

### What it does

VoiceClinic handles common front-desk workflows for a healthcare clinic:

- books appointments;
- reschedules existing appointments;
- cancels appointments;
- answers basic administrative questions;
- detects high-risk clinical situations through a separate guardrail observer;
- exposes the same agent logic through a web demo, REST API and local telephony bridge.

### Architecture at a glance

```mermaid
flowchart LR
  User["Patient / caller"] --> Channel["Web, API or SIP"]
  Channel --> STT["Local STT optional"]
  STT --> Agent["ClinicAgent"]
  Channel --> Agent
  Agent --> Guardrails["ClinicalPolicyObserver"]
  Guardrails --> Agent
  Agent --> Scheduler["SQLite scheduler"]
  Agent --> Ollama["Ollama local LLM"]
  Agent --> TTS["Local TTS optional"]
  TTS --> Channel
```

Main components:

- **FastAPI** for the backend and web demo.
- **SQLite** for demo patients, doctors, slots and appointments.
- **Ollama** with `qwen3:30b` as the recommended local LLM for a single RTX 4090.
- **faster-whisper** for optional local speech-to-text.
- **Piper** for optional local text-to-speech.
- **Asterisk + AudioSocket** for local SIP calls from a softphone.
- **LiveKit-ready design** for a future WebRTC/SIP path.

### Quick start

Requirements:

- Python 3.11 or newer. Python 3.12 is recommended.
- Ollama, if you want LLM-based intent extraction.
- Docker, only if you want the containerized stack.

```bash
cp .env.example .env
make setup
make reset-db
make api
```

Open:

```text
http://127.0.0.1:8000/demo/
```

Text-only mode:

```bash
make chat
```

Recommended Ollama model:

```bash
ollama pull qwen3:30b
```

### Documentation

- [Setup](docs/SETUP.md): local, voice, Docker and telephony setup.
- [Architecture](docs/ARCHITECTURE.md): components, flows and design decisions.
- [API](docs/API.md): REST endpoints and example requests.
- [Guardrails](docs/GUARDRAILS.md): clinical observer pattern and policy categories.
- [Demo Script](docs/DEMO_SCRIPT.md): portfolio-ready demo flow.
- [Roadmap](docs/ROADMAP.md): current scope and next iterations.

### Validation

```bash
make test
make lint
```

Current test coverage focuses on scheduling transactions, agent behavior and
clinical guardrails.

### References

- LiveKit local server: https://docs.livekit.io/transport/self-hosting/local/
- LiveKit SIP self-hosted: https://docs.livekit.io/transport/self-hosting/sip-server/
- LiveKit observer-pattern guardrails: https://livekit.com/blog/observer-pattern-voice-agent-guardrails
- Asterisk AudioSocket: https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- Piper: https://github.com/OHF-Voice/piper1-gpl

## Español

### Qué hace

VoiceClinic cubre flujos habituales de recepción en una clínica:

- reserva citas;
- cambia citas existentes;
- cancela citas;
- responde consultas administrativas básicas;
- detecta situaciones clínicas de riesgo mediante un observador de guardrails;
- expone la misma lógica por demo web, API REST y puente de telefonía local.

### Arquitectura en resumen

```mermaid
flowchart LR
  User["Paciente / llamada"] --> Channel["Web, API o SIP"]
  Channel --> STT["STT local opcional"]
  STT --> Agent["ClinicAgent"]
  Channel --> Agent
  Agent --> Guardrails["ClinicalPolicyObserver"]
  Guardrails --> Agent
  Agent --> Scheduler["Agenda SQLite"]
  Agent --> Ollama["LLM local con Ollama"]
  Agent --> TTS["TTS local opcional"]
  TTS --> Channel
```

Componentes principales:

- **FastAPI** para backend y demo web.
- **SQLite** para pacientes, doctores, huecos y citas de demostración.
- **Ollama** con `qwen3:30b` como LLM local recomendado para una RTX 4090.
- **faster-whisper** para transcripción local opcional.
- **Piper** para síntesis de voz local opcional.
- **Asterisk + AudioSocket** para llamadas SIP locales desde un softphone.
- **Diseño preparado para LiveKit** como evolución futura hacia WebRTC/SIP.

### Inicio rápido

Requisitos:

- Python 3.11 o superior. Se recomienda Python 3.12.
- Ollama, si quieres extracción de intención basada en LLM.
- Docker, solo si quieres levantar el stack en contenedores.

```bash
cp .env.example .env
make setup
make reset-db
make api
```

Abre:

```text
http://127.0.0.1:8000/demo/
```

Modo solo texto:

```bash
make chat
```

Modelo recomendado para Ollama:

```bash
ollama pull qwen3:30b
```

### Documentación

- [Instalación](docs/SETUP.md): configuración local, voz, Docker y telefonía.
- [Arquitectura](docs/ARCHITECTURE.md): componentes, flujos y decisiones técnicas.
- [API](docs/API.md): endpoints REST y ejemplos de petición.
- [Guardrails](docs/GUARDRAILS.md): patrón de observador clínico y categorías de política.
- [Guion de Demo](docs/DEMO_SCRIPT.md): recorrido listo para portfolio.
- [Roadmap](docs/ROADMAP.md): alcance actual y siguientes iteraciones.

### Validación

```bash
make test
make lint
```

La cobertura actual se centra en transacciones de agenda, comportamiento del
agente y guardrails clínicos.

### Referencias

- LiveKit local server: https://docs.livekit.io/transport/self-hosting/local/
- LiveKit SIP self-hosted: https://docs.livekit.io/transport/self-hosting/sip-server/
- LiveKit observer-pattern guardrails: https://livekit.com/blog/observer-pattern-voice-agent-guardrails
- Asterisk AudioSocket: https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- Piper: https://github.com/OHF-Voice/piper1-gpl
