# Platform Notes / Notas de plataforma

## English

### Support Matrix

| Feature | Windows | macOS | Linux |
| --- | --- | --- | --- |
| FastAPI backend | Supported | Supported | Supported |
| Web demo | Supported | Supported | Supported |
| SQLite scheduler | Supported | Supported | Supported |
| Ollama local LLM | Supported | Supported | Supported |
| NVIDIA CUDA | Supported with NVIDIA drivers or WSL2 | Not applicable | Supported |
| Apple Silicon acceleration | Not applicable | Supported by native Ollama | Not applicable |
| faster-whisper CPU | Supported | Supported | Supported |
| faster-whisper CUDA | Supported with compatible PyTorch/CUDA setup | Not applicable | Supported |
| Piper TTS | Supported with binary installed | Supported with binary installed | Supported with binary installed |
| Asterisk SIP | Use WSL2 or Linux VM | Possible, Linux recommended | Recommended |

### Windows

- Use PowerShell or Windows Terminal.
- Prefer the Python launcher:

```powershell
py -3.12 scripts/dev.py setup
py -3.12 scripts/dev.py api
```

- For CUDA, use current NVIDIA drivers. Docker GPU support usually works best
  through WSL2.
- For Asterisk, use WSL2, Docker or a Linux VM.

### macOS

- Use native Ollama for best Apple Silicon acceleration.
- CUDA is not available on macOS.
- The core API, web demo, SQLite scheduler and tests run normally.
- SIP telephony is possible, but Linux is the cleaner target for Asterisk.

### Linux

- Linux is the best target for the full stack: API, Ollama, CUDA, Docker,
  Asterisk and AudioSocket.
- For NVIDIA acceleration, install the NVIDIA driver and container toolkit if
  you want GPU support inside Docker.

### CUDA Notes

The project is compatible with CPU-only execution, but a CUDA-capable NVIDIA GPU
significantly improves local LLM and speech workloads. A single RTX 4090 is a
good target for `qwen3:30b` in Ollama.

Use the GPU Docker override when Docker has NVIDIA GPU access:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

## Español

### Matriz de soporte

| Funcionalidad | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Backend FastAPI | Compatible | Compatible | Compatible |
| Demo web | Compatible | Compatible | Compatible |
| Agenda SQLite | Compatible | Compatible | Compatible |
| LLM local con Ollama | Compatible | Compatible | Compatible |
| NVIDIA CUDA | Compatible con drivers NVIDIA o WSL2 | No aplica | Compatible |
| Aceleración Apple Silicon | No aplica | Compatible con Ollama nativo | No aplica |
| faster-whisper CPU | Compatible | Compatible | Compatible |
| faster-whisper CUDA | Compatible con setup PyTorch/CUDA adecuado | No aplica | Compatible |
| Piper TTS | Compatible con binario instalado | Compatible con binario instalado | Compatible con binario instalado |
| Asterisk SIP | Usar WSL2 o VM Linux | Posible, Linux recomendado | Recomendado |

### Windows

- Usa PowerShell o Windows Terminal.
- Se recomienda el launcher de Python:

```powershell
py -3.12 scripts/dev.py setup
py -3.12 scripts/dev.py api
```

- Para CUDA, usa drivers NVIDIA actualizados. El soporte GPU en Docker suele ir
  mejor mediante WSL2.
- Para Asterisk, usa WSL2, Docker o una VM Linux.

### macOS

- Usa Ollama nativo para aprovechar mejor Apple Silicon.
- CUDA no está disponible en macOS.
- La API, la demo web, la agenda SQLite y los tests funcionan con normalidad.
- La telefonía SIP es posible, pero Linux es el entorno más limpio para Asterisk.

### Linux

- Linux es el mejor objetivo para el stack completo: API, Ollama, CUDA, Docker,
  Asterisk y AudioSocket.
- Para aceleración NVIDIA, instala el driver NVIDIA y el container toolkit si
  quieres usar GPU dentro de Docker.

### Notas sobre CUDA

El proyecto funciona en CPU, pero una GPU NVIDIA con CUDA mejora mucho las cargas
locales de LLM y voz. Una RTX 4090 es un buen objetivo para `qwen3:30b` en
Ollama.

Usa el override GPU de Docker cuando Docker tenga acceso a la GPU NVIDIA:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```
