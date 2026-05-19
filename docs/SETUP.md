# Setup / Instalación

## English

VoiceClinic is designed to run on Windows, macOS and Linux. The primary task
runner is `scripts/dev.py`, which avoids shell-specific commands and handles
virtual-environment paths across platforms.

### Requirements

- Python 3.11 or newer. Python 3.12 is recommended.
- Ollama, if you want LLM-based intent extraction.
- Docker, if you want the containerized stack.
- ffmpeg, faster-whisper and Piper only if you want local voice input/output.
- Asterisk only if you want local SIP telephony.

### Python command by platform

Use whichever command points to Python 3.11+ on your machine:

```bash
python scripts/dev.py --help
python3 scripts/dev.py --help
py -3.12 scripts/dev.py --help
```

In the examples below, replace `python` with `python3` or `py -3.12` if needed.

### Local setup

```bash
python scripts/dev.py copy-env
python scripts/dev.py setup
python scripts/dev.py reset-db
python scripts/dev.py api
```

The API runs at:

```text
http://127.0.0.1:8000
```

The browser demo is available at:

```text
http://127.0.0.1:8000/demo/
```

Text-only mode:

```bash
python scripts/dev.py chat
```

### Optional Makefile shortcuts

`make` is still available as a convenience wrapper on macOS/Linux and on Windows
environments that have `make` installed:

```bash
make setup
make api
make test
```

The Python runner is the recommended cross-platform path.

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

### OpenAI provider

To use OpenAI instead of Ollama, configure `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4.1-mini
```

The code uses an OpenAI-compatible chat-completions provider, so the agent can
switch between local Ollama and OpenAI without changing the scheduling logic.

### LangGraph orchestration

Direct orchestration is the default because it has no optional dependencies:

```env
ORCHESTRATION_MODE=direct
```

To run the optional LangGraph turn lifecycle:

```bash
python scripts/dev.py setup-orchestration
```

Then set:

```env
ORCHESTRATION_MODE=langgraph
```

The graph currently models the turn as `observe_policy -> infer_intent ->
execute_action`, with a blocking branch when a clinical guardrail fires. It uses
a `messages` state key so the compiled graph can also be wrapped by LiveKit's
LangChain adapter.

### LiveKit + LangGraph adapter

Install the optional LiveKit integration:

```bash
python scripts/dev.py setup-livekit
```

This installs `livekit-agents[langchain]` and LangGraph. Use
`voiceclinic.orchestration.build_livekit_graph(agent)` when you want the
compiled graph, or `voiceclinic.livekit_agent.build_langgraph_llm_adapter()`
when you want a ready-to-pass LiveKit `LLMAdapter`.

The pattern is:

```python
from livekit.agents import AgentSession

from voiceclinic.livekit_agent import build_langgraph_llm_adapter

session = AgentSession(
    llm=build_langgraph_llm_adapter(),
    # stt=..., tts=..., vad=...
)
```

See [LiveKit + LangGraph](LIVEKIT_LANGGRAPH.md) for the complete bilingual
integration notes.

### Voice dependencies

Install the Python voice dependency:

```bash
python scripts/dev.py setup-voice
```

Configure Piper in `.env`:

```env
PIPER_BIN=piper
PIPER_MODEL=models/es_ES-your-voice.onnx
PIPER_CONFIG=models/es_ES-your-voice.onnx.json
FFMPEG_BIN=ffmpeg
```

If `piper` or `ffmpeg` are not in `PATH`, use absolute paths. Windows `.exe`
paths are supported.

The voice endpoint is:

```text
POST /voice/turn
```

It accepts microphone audio, transcribes it locally and returns the agent
response. If Piper is configured, it also returns a WAV response URL.

### Docker

CPU-compatible stack:

```bash
python scripts/dev.py copy-env
python scripts/dev.py docker-up
```

NVIDIA GPU override for CUDA-capable Linux or Windows/WSL2 Docker setups:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

Download the Ollama model inside the Ollama container:

```bash
docker compose exec ollama ollama pull qwen3:30b
```

### Local SIP telephony

Local SIP telephony is easiest on Linux or in a Linux VM/container. On Windows,
use WSL2 or a Linux VM for Asterisk.

1. Copy `infra/asterisk/pjsip.conf` and `infra/asterisk/extensions.conf` into
   your Asterisk configuration.
   If Asterisk runs inside Docker Desktop, replace `127.0.0.1` in
   `extensions.conf` with `host.docker.internal`.
2. Start the AudioSocket bridge:

```bash
python scripts/dev.py audiosocket
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

VoiceClinic está diseñado para ejecutarse en Windows, macOS y Linux. El runner
principal es `scripts/dev.py`, que evita comandos específicos de una shell y
resuelve las rutas del entorno virtual en cada plataforma.

### Requisitos

- Python 3.11 o superior. Se recomienda Python 3.12.
- Ollama, si quieres extracción de intención basada en LLM.
- Docker, si quieres levantar el stack en contenedores.
- ffmpeg, faster-whisper y Piper solo si quieres entrada/salida de voz local.
- Asterisk solo si quieres telefonía SIP local.

### Comando de Python por plataforma

Usa el comando que apunte a Python 3.11+ en tu máquina:

```bash
python scripts/dev.py --help
python3 scripts/dev.py --help
py -3.12 scripts/dev.py --help
```

En los ejemplos siguientes, cambia `python` por `python3` o `py -3.12` si hace
falta.

### Instalación local

```bash
python scripts/dev.py copy-env
python scripts/dev.py setup
python scripts/dev.py reset-db
python scripts/dev.py api
```

La API se levanta en:

```text
http://127.0.0.1:8000
```

La demo web está disponible en:

```text
http://127.0.0.1:8000/demo/
```

Modo solo texto:

```bash
python scripts/dev.py chat
```

### Atajos opcionales con Makefile

`make` sigue disponible como wrapper cómodo en macOS/Linux y en entornos Windows
que tengan `make` instalado:

```bash
make setup
make api
make test
```

El runner Python es la vía recomendada para compatibilidad multiplataforma.

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

### Provider OpenAI

Para usar OpenAI en lugar de Ollama, configura `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4.1-mini
```

El código usa un provider compatible con chat completions de OpenAI, por lo que
el agente puede cambiar entre Ollama local y OpenAI sin modificar la lógica de
agenda.

### Orquestación con LangGraph

La orquestación directa es la opción por defecto porque no requiere dependencias
opcionales:

```env
ORCHESTRATION_MODE=direct
```

Para ejecutar el ciclo de turno con LangGraph:

```bash
python scripts/dev.py setup-orchestration
```

Después configura:

```env
ORCHESTRATION_MODE=langgraph
```

El grafo actual modela el turno como `observe_policy -> infer_intent ->
execute_action`, con una rama bloqueante cuando se activa un guardrail clínico.
Usa una clave de estado `messages`, por lo que el grafo compilado también puede
envolverse con el adaptador LangChain de LiveKit.

### Adaptador LiveKit + LangGraph

Instala la integración opcional de LiveKit:

```bash
python scripts/dev.py setup-livekit
```

Esto instala `livekit-agents[langchain]` y LangGraph. Usa
`voiceclinic.orchestration.build_livekit_graph(agent)` si quieres el grafo
compilado, o `voiceclinic.livekit_agent.build_langgraph_llm_adapter()` si quieres
un `LLMAdapter` de LiveKit listo para pasar a `AgentSession`.

El patrón es:

```python
from livekit.agents import AgentSession

from voiceclinic.livekit_agent import build_langgraph_llm_adapter

session = AgentSession(
    llm=build_langgraph_llm_adapter(),
    # stt=..., tts=..., vad=...
)
```

Consulta [LiveKit + LangGraph](LIVEKIT_LANGGRAPH.md) para las notas completas de
integración bilingüe.

### Dependencias de voz

Instala la dependencia Python para voz:

```bash
python scripts/dev.py setup-voice
```

Configura Piper en `.env`:

```env
PIPER_BIN=piper
PIPER_MODEL=models/es_ES-your-voice.onnx
PIPER_CONFIG=models/es_ES-your-voice.onnx.json
FFMPEG_BIN=ffmpeg
```

Si `piper` o `ffmpeg` no están en `PATH`, usa rutas absolutas. Las rutas `.exe`
de Windows son compatibles.

El endpoint de voz es:

```text
POST /voice/turn
```

Acepta audio del micrófono, lo transcribe localmente y devuelve la respuesta del
agente. Si Piper está configurado, también devuelve una URL WAV con la respuesta
hablada.

### Docker

Stack compatible con CPU:

```bash
python scripts/dev.py copy-env
python scripts/dev.py docker-up
```

Override para GPU NVIDIA en Linux con CUDA o Windows/WSL2 con Docker:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

Descarga el modelo dentro del contenedor de Ollama:

```bash
docker compose exec ollama ollama pull qwen3:30b
```

### Telefonía SIP local

La telefonía SIP local es más sencilla en Linux o en una VM/contenedor Linux. En
Windows, usa WSL2 o una VM Linux para Asterisk.

1. Copia `infra/asterisk/pjsip.conf` y `infra/asterisk/extensions.conf` a tu
   configuración de Asterisk.
   Si Asterisk se ejecuta dentro de Docker Desktop, sustituye `127.0.0.1` en
   `extensions.conf` por `host.docker.internal`.
2. Arranca el puente AudioSocket:

```bash
python scripts/dev.py audiosocket
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
