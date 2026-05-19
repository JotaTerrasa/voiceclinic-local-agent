# Setup / Instalación

## English

### Requirements

- Python 3.11 or newer. Python 3.12 is recommended.
- `make`.
- Ollama, if you want LLM-based intent extraction.
- Docker, if you want the containerized stack.
- ffmpeg, faster-whisper and Piper only if you want local voice input/output.

### Local setup

```bash
cp .env.example .env
make setup
make reset-db
make api
```

The API runs at:

```text
http://127.0.0.1:8000
```

The browser demo is available at:

```text
http://127.0.0.1:8000/demo/
```

If your default `python3` is older than 3.11, specify the interpreter explicitly:

```bash
make setup PYTHON=python3.12
```

### Ollama

Recommended model:

```bash
ollama pull qwen3:30b
```

The model is configured through `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:30b
OLLAMA_TIMEOUT_SECONDS=20
```

The agent still works without Ollama by falling back to deterministic rules.

### Voice dependencies

Install the Python voice dependency:

```bash
make setup-voice
```

Configure Piper in `.env`:

```env
PIPER_BIN=piper
PIPER_MODEL=models/es_ES-your-voice.onnx
PIPER_CONFIG=models/es_ES-your-voice.onnx.json
FFMPEG_BIN=ffmpeg
```

The voice endpoint is:

```text
POST /voice/turn
```

It accepts microphone audio, transcribes it locally and returns the agent
response. If Piper is configured, it also returns a WAV response URL.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Download the Ollama model inside the Ollama container:

```bash
docker compose exec ollama ollama pull qwen3:30b
```

### Local SIP telephony

1. Copy `infra/asterisk/pjsip.conf` and `infra/asterisk/extensions.conf` into
   your Asterisk configuration.
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

Extension `7001` answers the call and connects it to the local AudioSocket
server.

## Español

### Requisitos

- Python 3.11 o superior. Se recomienda Python 3.12.
- `make`.
- Ollama, si quieres extracción de intención basada en LLM.
- Docker, si quieres levantar el stack en contenedores.
- ffmpeg, faster-whisper y Piper solo si quieres entrada/salida de voz local.

### Instalación local

```bash
cp .env.example .env
make setup
make reset-db
make api
```

La API se levanta en:

```text
http://127.0.0.1:8000
```

La demo web está disponible en:

```text
http://127.0.0.1:8000/demo/
```

Si tu `python3` por defecto es anterior a 3.11, indica el intérprete:

```bash
make setup PYTHON=python3.12
```

### Ollama

Modelo recomendado:

```bash
ollama pull qwen3:30b
```

El modelo se configura en `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:30b
OLLAMA_TIMEOUT_SECONDS=20
```

El agente sigue funcionando sin Ollama gracias a reglas deterministas.

### Dependencias de voz

Instala la dependencia Python para voz:

```bash
make setup-voice
```

Configura Piper en `.env`:

```env
PIPER_BIN=piper
PIPER_MODEL=models/es_ES-your-voice.onnx
PIPER_CONFIG=models/es_ES-your-voice.onnx.json
FFMPEG_BIN=ffmpeg
```

El endpoint de voz es:

```text
POST /voice/turn
```

Acepta audio del micrófono, lo transcribe localmente y devuelve la respuesta del
agente. Si Piper está configurado, también devuelve una URL WAV con la respuesta
hablada.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Descarga el modelo dentro del contenedor de Ollama:

```bash
docker compose exec ollama ollama pull qwen3:30b
```

### Telefonía SIP local

1. Copia `infra/asterisk/pjsip.conf` y `infra/asterisk/extensions.conf` a tu
   configuración de Asterisk.
2. Arranca el puente AudioSocket:

```bash
make audiosocket
```

3. Registra un softphone SIP:

```text
Usuario: 6001
Password: voiceclinic
Servidor: 127.0.0.1
Extensión demo: 7001
```

La extensión `7001` contesta la llamada y la conecta al servidor local de
AudioSocket.
