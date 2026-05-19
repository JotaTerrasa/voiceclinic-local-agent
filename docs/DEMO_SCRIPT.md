# Demo Script / Guion De Demo

## English

### Setup

```bash
cp .env.example .env
make setup
make reset-db
make api
```

Open `http://127.0.0.1:8000/demo/`.

### Flow 1: Book An Appointment

Patient:

```text
Quiero una cita de cardiologia manana a las 10
```

Expected result: the agent confirms date, time, doctor and specialty.

### Flow 2: Check Existing Appointments

Patient:

```text
Que citas tengo?
```

Expected result: the agent lists the active appointment.

### Flow 3: Reschedule

Patient:

```text
Quiero cambiar mi cita al viernes a las 11
```

Expected result: the previous appointment slot is released and a new slot is
reserved.

### Flow 4: Cancel

Patient:

```text
Quiero cancelar mi cita
```

Expected result: the appointment is marked as cancelled and the slot is released.

### Flow 5: Administrative Question

Patient:

```text
Que documentos tengo que llevar?
```

Expected result: the agent asks the patient to bring ID or healthcare card and
recent reports.

### Flow 6: Clinical Guardrail

Patient:

```text
Tengo dolor en el pecho y no puedo respirar, quiero una cita manana
```

Expected result: the agent does not book a routine appointment. It triggers the
`medical_emergency` guardrail and directs the patient to emergency care.

## Espanol

### Preparacion

```bash
cp .env.example .env
make setup
make reset-db
make api
```

Abre `http://127.0.0.1:8000/demo/`.

### Flujo 1: Reservar Una Cita

Paciente:

```text
Quiero una cita de cardiologia manana a las 10
```

Resultado esperado: el agente confirma fecha, hora, doctor y especialidad.

### Flujo 2: Consultar Citas

Paciente:

```text
Que citas tengo?
```

Resultado esperado: el agente lista la cita activa.

### Flujo 3: Cambiar Una Cita

Paciente:

```text
Quiero cambiar mi cita al viernes a las 11
```

Resultado esperado: se libera el hueco anterior y se reserva un nuevo hueco.

### Flujo 4: Cancelar

Paciente:

```text
Quiero cancelar mi cita
```

Resultado esperado: la cita queda marcada como cancelada y el hueco queda libre.

### Flujo 5: Consulta Administrativa

Paciente:

```text
Que documentos tengo que llevar?
```

Resultado esperado: el agente indica que debe traer DNI o tarjeta sanitaria e
informes recientes.

### Flujo 6: Guardrail Clinico

Paciente:

```text
Tengo dolor en el pecho y no puedo respirar, quiero una cita manana
```

Resultado esperado: el agente no reserva una cita ordinaria. Activa el guardrail
`medical_emergency` y deriva a atencion urgente.
