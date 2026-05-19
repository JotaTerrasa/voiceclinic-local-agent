# Demo Script / Guion de demo

## English

This script is designed for a portfolio walkthrough. It demonstrates the core
value proposition: a local voice-ready agent that can handle appointment
workflows while applying clinical guardrails.

### Preparation

```bash
python scripts/dev.py copy-env
python scripts/dev.py setup
python scripts/dev.py reset-db
python scripts/dev.py api
```

Open:

```text
http://127.0.0.1:8000/demo/
```

Use the default demo patient:

```text
+34600111222
```

### Flow 1: Book an appointment

Patient:

```text
Quiero una cita de cardiología mañana a las 10
```

Expected result:

- The agent books the first matching cardiology slot.
- The response confirms date, time, doctor and specialty.
- The appointment table updates in the web demo.

### Flow 2: Check appointments

Patient:

```text
¿Qué citas tengo?
```

Expected result:

- The agent lists the active appointments associated with the phone number.

### Flow 3: Reschedule

Patient:

```text
Quiero cambiar mi cita al viernes a las 11
```

Expected result:

- The previous slot is released.
- A new appointment slot is reserved.
- The agent confirms the new date and time.

### Flow 4: Cancel

Patient:

```text
Quiero cancelar mi cita
```

Expected result:

- The appointment is marked as cancelled.
- The slot becomes available again.

### Flow 5: Administrative question

Patient:

```text
¿Qué documentos tengo que llevar?
```

Expected result:

- The agent answers with administrative information only.
- It does not provide medical advice.

### Flow 6: Clinical guardrail

Patient:

```text
Tengo dolor en el pecho y no puedo respirar. Quiero una cita mañana.
```

Expected result:

- The agent does not book a routine appointment.
- The `medical_emergency` guardrail is triggered.
- The response directs the patient to emergency care.

### Suggested talk track

1. Start with the web demo and show the appointment table.
2. Book a cardiology appointment.
3. Explain that the same core agent can be called from REST, voice or SIP.
4. Trigger the emergency guardrail to show that safety logic is separate from
   scheduling logic.
5. Open `docs/ARCHITECTURE.md` and explain the observer pattern.

## Español

Este guion está pensado para una presentación de portfolio. Demuestra la
propuesta de valor principal: un agente local preparado para voz que gestiona
citas y aplica guardrails clínicos.

### Preparación

```bash
python scripts/dev.py copy-env
python scripts/dev.py setup
python scripts/dev.py reset-db
python scripts/dev.py api
```

Abre:

```text
http://127.0.0.1:8000/demo/
```

Usa el paciente de demostración por defecto:

```text
+34600111222
```

### Flujo 1: Reservar una cita

Paciente:

```text
Quiero una cita de cardiología mañana a las 10
```

Resultado esperado:

- El agente reserva el primer hueco de cardiología que cumple la petición.
- La respuesta confirma fecha, hora, médico y especialidad.
- La tabla de citas se actualiza en la demo web.

### Flujo 2: Consultar citas

Paciente:

```text
¿Qué citas tengo?
```

Resultado esperado:

- El agente lista las citas activas asociadas al teléfono del paciente.

### Flujo 3: Cambiar una cita

Paciente:

```text
Quiero cambiar mi cita al viernes a las 11
```

Resultado esperado:

- Se libera el hueco anterior.
- Se reserva un nuevo hueco.
- El agente confirma la nueva fecha y hora.

### Flujo 4: Cancelar

Paciente:

```text
Quiero cancelar mi cita
```

Resultado esperado:

- La cita queda marcada como cancelada.
- El hueco vuelve a estar disponible.

### Flujo 5: Consulta administrativa

Paciente:

```text
¿Qué documentos tengo que llevar?
```

Resultado esperado:

- El agente responde con información administrativa.
- No ofrece consejo médico.

### Flujo 6: Guardrail clínico

Paciente:

```text
Tengo dolor en el pecho y no puedo respirar. Quiero una cita mañana.
```

Resultado esperado:

- El agente no reserva una cita ordinaria.
- Se activa el guardrail `medical_emergency`.
- La respuesta deriva al paciente a atención urgente.

### Narrativa recomendada

1. Empieza con la demo web y muestra la tabla de citas.
2. Reserva una cita de cardiología.
3. Explica que el mismo núcleo del agente puede usarse desde REST, voz o SIP.
4. Activa el guardrail de emergencia para demostrar que la seguridad está
   separada de la lógica de agenda.
5. Abre `docs/ARCHITECTURE.md` y explica el patrón de observador.
