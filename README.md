# VoiceClinic Local

## English

Local phone agent for an AI portfolio project. It manages patient appointment
booking, rescheduling, cancellations and basic clinic questions using a
self-hosted stack.

The project follows the idea behind `LiveKit Local Setup - Self-Hosted Voice AI`,
adapted to healthcare workflows and without relying on closed voice-agent
platforms.

### Stack

- Local orchestration: FastAPI + Python.
- Scheduling: SQLite with demo patients, doctors, slots and appointments.
- Local LLM: Ollama through an OpenAI-compatible endpoint.
- Local STT: faster-whisper, optional for the voice demo.
- Local TTS: Piper, optional for spoken responses.
- Local telephony: Asterisk + AudioSocket for SIP calls from a softphone.
- Realtime/WebRTC: local LiveKit prepared for a future LiveKit SIP/WebRTC path.

### Run Locally

```bash
cp .env.example .env
make setup
make reset-db
make api
```

Open `http://127.0.0.1:8000/demo/`.

You can also test the text-only agent in another terminal:

```bash
make chat
```

Example prompts:

```text
Quiero una cita de cardiologia manana a las 10
Quiero cambiar mi cita al viernes a las 11
Que citas tengo?
Quiero cancelar mi cita
Que documentos tengo que llevar?
```

### Ollama

Start Ollama and download the recommended local model:

```bash
ollama pull qwen3:30b
```

The agent can run without Ollama using deterministic rules, but Ollama improves
natural-language intent extraction.

`qwen3:30b` is the default because it fits a single RTX 4090 24GB more
comfortably than 70B-class models while providing stronger multilingual and
agentic behavior than small 8B models. If you prefer a dense model and can accept
lower throughput, `qwen3:32b` is the closest drop-in alternative.

### Local Voice

Install the voice dependencies:

```bash
make setup-voice
```

For TTS, install Piper and configure a Spanish voice in `.env`:

```env
PIPER_BIN=piper
PIPER_MODEL=models/es_ES-your-voice.onnx
PIPER_CONFIG=models/es_ES-your-voice.onnx.json
```

The web demo uses `POST /voice/turn`: microphone audio, local transcription,
appointment tooling and an audio response when Piper is configured.

### Clinical Guardrails

The project includes a local `ClinicalPolicyObserver` inspired by LiveKit's
background observer pattern for voice-agent guardrails:

- It listens to each user turn.
- It evaluates clinical policy risks independently from appointment logic.
- It injects actionable directives into the agent flow before tools run.

Current guardrails cover medical emergencies, self-harm, diagnosis requests,
prescription/dosage requests and third-party patient data. For example, chest
pain plus breathing difficulty blocks routine booking and directs the caller to
emergency care.

Reference: https://livekit.com/blog/observer-pattern-voice-agent-guardrails

### Local Telephony With Asterisk

1. Copy `infra/asterisk/pjsip.conf` and `infra/asterisk/extensions.conf` into
   your local Asterisk configuration.
2. Start the AudioSocket bridge:

```bash
make audiosocket
```

3. Register a SIP softphone:

```text
User: 6001
Password: voiceclinic
Server: 127.0.0.1
Demo extension: 7001
```

Extension `7001` answers the call and connects audio to the local AudioSocket
server.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Main services:

- Demo API: `http://127.0.0.1:8000/demo/`
- Ollama: `http://127.0.0.1:11434`
- Local LiveKit: `ws://127.0.0.1:7880` with `devkey / secret`

Download the model inside the Ollama container:

```bash
docker compose exec ollama ollama pull qwen3:30b
```

### Tests

```bash
make test
```

### Technical Sources

- LiveKit local server: https://docs.livekit.io/transport/self-hosting/local/
- LiveKit SIP self-hosted: https://docs.livekit.io/transport/self-hosting/sip-server/
- LiveKit Agents + Ollama: https://docs.livekit.io/agents/models/llm/ollama/
- Asterisk AudioSocket: https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- Piper: https://github.com/OHF-Voice/piper1-gpl

## Espanol

Agente telefonico local para portfolio de IA. Gestiona reservas de citas,
cambios, cancelaciones y consultas sencillas de pacientes con un stack
self-hosted.

El proyecto sigue la idea del video `LiveKit Local Setup - Self-Hosted Voice AI`,
adaptada a flujos sanitarios y sin depender de plataformas cerradas de agentes
de voz.

### Stack

- Orquestacion local: FastAPI + Python.
- Agenda: SQLite con datos demo de pacientes, doctores, huecos y citas.
- LLM local: Ollama mediante endpoint compatible con OpenAI.
- STT local: faster-whisper, opcional para la demo de voz.
- TTS local: Piper, opcional para respuestas habladas.
- Telefonia local: Asterisk + AudioSocket para llamadas SIP desde un softphone.
- Realtime/WebRTC: LiveKit local preparado para evolucionar hacia LiveKit SIP/WebRTC.

### Ejecutar En Local

```bash
cp .env.example .env
make setup
make reset-db
make api
```

Abre `http://127.0.0.1:8000/demo/`.

Tambien puedes probar el agente solo por texto en otra terminal:

```bash
make chat
```

Ejemplos:

```text
Quiero una cita de cardiologia manana a las 10
Quiero cambiar mi cita al viernes a las 11
Que citas tengo?
Quiero cancelar mi cita
Que documentos tengo que llevar?
```

### Ollama

Arranca Ollama y descarga el modelo local recomendado:

```bash
ollama pull qwen3:30b
```

El agente puede funcionar sin Ollama usando reglas deterministas, pero Ollama
mejora la extraccion de intenciones en lenguaje natural.

`qwen3:30b` queda como modelo por defecto porque entra mejor en una RTX 4090 de
24 GB que modelos de 70B, manteniendo mejor comportamiento multilingue y
agentico que modelos pequenos de 8B. Si prefieres un modelo denso y aceptas
menor velocidad, `qwen3:32b` es la alternativa mas cercana.

### Voz Local

Instala las dependencias de voz:

```bash
make setup-voice
```

Para TTS, instala Piper y configura una voz en espanol en `.env`:

```env
PIPER_BIN=piper
PIPER_MODEL=models/es_ES-your-voice.onnx
PIPER_CONFIG=models/es_ES-your-voice.onnx.json
```

La demo web usa `POST /voice/turn`: audio del microfono, transcripcion local,
herramienta de agenda y respuesta en audio si Piper esta configurado.

### Guardrails Clinicos

El proyecto incluye un `ClinicalPolicyObserver` local inspirado en el background
observer pattern de LiveKit para guardrails de agentes de voz:

- Escucha cada turno del usuario.
- Evalua riesgos clinicos de forma independiente a la logica de citas.
- Inyecta directivas accionables en el flujo del agente antes de ejecutar herramientas.

Los guardrails actuales cubren emergencias medicas, autolesion, peticiones de
diagnostico, peticiones de receta/dosis y datos de terceros. Por ejemplo, dolor
en el pecho con dificultad respiratoria bloquea la reserva ordinaria y deriva a
atencion urgente.

Referencia: https://livekit.com/blog/observer-pattern-voice-agent-guardrails

### Telefonia Local Con Asterisk

1. Copia `infra/asterisk/pjsip.conf` y `infra/asterisk/extensions.conf` a tu
   configuracion local de Asterisk.
2. Arranca el puente AudioSocket:

```bash
make audiosocket
```

3. Registra un softphone SIP:

```text
Usuario: 6001
Password: voiceclinic
Servidor: 127.0.0.1
Extension demo: 7001
```

La extension `7001` contesta la llamada y conecta el audio al servidor local por
AudioSocket.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Servicios principales:

- API demo: `http://127.0.0.1:8000/demo/`
- Ollama: `http://127.0.0.1:11434`
- LiveKit local: `ws://127.0.0.1:7880` con `devkey / secret`

Descarga el modelo dentro del contenedor de Ollama:

```bash
docker compose exec ollama ollama pull qwen3:30b
```

### Tests

```bash
make test
```

### Fuentes Tecnicas

- LiveKit local server: https://docs.livekit.io/transport/self-hosting/local/
- LiveKit SIP self-hosted: https://docs.livekit.io/transport/self-hosting/sip-server/
- LiveKit Agents + Ollama: https://docs.livekit.io/agents/models/llm/ollama/
- Asterisk AudioSocket: https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- Piper: https://github.com/OHF-Voice/piper1-gpl
