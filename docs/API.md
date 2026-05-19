# API / API REST

## English

Base URL:

```text
http://127.0.0.1:8000
```

### Health

```http
GET /health
```

Returns service status and the configured database path.

### Demo reset

```http
POST /demo/reset
```

Resets the SQLite database with demo patients, doctors and slots.

### Patients

```http
GET /patients
```

Returns demo patients.

### Available slots

```http
GET /slots?specialty=cardiologia&limit=5
```

Returns available appointment slots. `specialty` is optional.

### Appointments

```http
GET /appointments?phone=%2B34600111222
```

Returns active appointments for the patient phone number.

### Agent chat

```http
POST /agent/chat
Content-Type: application/json
```

```json
{
  "message": "Quiero una cita de cardiología mañana a las 10",
  "patient_phone": "+34600111222",
  "session_id": "demo-session"
}
```

Example response:

```json
{
  "text": "Perfecto, te he reservado una cita...",
  "action": "booked",
  "data": {
    "id": 1,
    "specialty": "cardiologia"
  },
  "session_id": "demo-session"
}
```

Guardrail responses use actions such as `guardrail_medical_emergency` and include
the policy directives in `data.guardrails`.

### Voice turn

```http
POST /voice/turn
Content-Type: multipart/form-data
```

Fields:

- `audio`: uploaded audio file.
- `patient_phone`: optional patient phone number.
- `session_id`: optional session identifier.

This endpoint requires faster-whisper. It returns the transcript, agent response
and, when Piper is configured, an `audio_url`.

## Español

URL base:

```text
http://127.0.0.1:8000
```

### Estado del servicio

```http
GET /health
```

Devuelve el estado del servicio y la ruta configurada de la base de datos.

### Reinicio de demo

```http
POST /demo/reset
```

Reinicia la base SQLite con pacientes, doctores y huecos de demostración.

### Pacientes

```http
GET /patients
```

Devuelve los pacientes de demostración.

### Huecos disponibles

```http
GET /slots?specialty=cardiologia&limit=5
```

Devuelve huecos disponibles. `specialty` es opcional.

### Citas

```http
GET /appointments?phone=%2B34600111222
```

Devuelve las citas activas asociadas al teléfono del paciente.

### Chat del agente

```http
POST /agent/chat
Content-Type: application/json
```

```json
{
  "message": "Quiero una cita de cardiología mañana a las 10",
  "patient_phone": "+34600111222",
  "session_id": "demo-session"
}
```

Ejemplo de respuesta:

```json
{
  "text": "Perfecto, te he reservado una cita...",
  "action": "booked",
  "data": {
    "id": 1,
    "specialty": "cardiologia"
  },
  "session_id": "demo-session"
}
```

Las respuestas de guardrail usan acciones como `guardrail_medical_emergency` e
incluyen las directivas de política en `data.guardrails`.

### Turno de voz

```http
POST /voice/turn
Content-Type: multipart/form-data
```

Campos:

- `audio`: archivo de audio.
- `patient_phone`: teléfono opcional del paciente.
- `session_id`: identificador opcional de sesión.

Este endpoint requiere faster-whisper. Devuelve el transcript, la respuesta del
agente y, si Piper está configurado, un `audio_url`.
