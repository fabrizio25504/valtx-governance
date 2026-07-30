---
id: FEAT-045
titulo: Sistema de recordatorios con fecha de vencimiento
tags: [recordatorio, vencimiento, notificacion, agenda]
policies: []
owner: producto@valtx.pe
estado: draft
---

# FEAT-045 · Sistema de recordatorios con fecha de vencimiento

## Contexto
El usuariogestiona tareas pendientes y necesita crear recordatorios con una fecha
de vencimiento para no perder plazos. La Capa 0 no activa Policy Cards específicas
(no hay PII/sensibles implicados); se aplica el principio general de trazabilidad
`PRIN-TRACE-001`.

## User Scenarios & Testing

### User Story 1 - Crear recordatorio con vencimiento (Priority: P1)
Como usuario, quiero crear un recordatorio indicando un título, una descripción y
una fecha de vencimiento, para no olvidar mis tareas.

**Why this priority**: es el flujo mínimo viable; sin crear recordatorios no existe
ningún otro flujo.
**Independent Test**: crear un recordatorio y verificar que aparece en la lista con
la fecha de vencimiento mostrada.

**Acceptance Scenarios**:
1. **Given** un usuario autenticado, **When** ingresa título, descripción y fecha de vencimiento válidos, **Then** el sistema crea el recordatorio y muestra la fecha de vencimiento.
2. **Given** el usuario deja la fecha de vencimiento vacía, **When** intenta crear el recordatorio, **Then** el sistema rechaza la creación con un mensaje claro.

### User Story 2 - Listar y filtrar recordatorios próximos a vencer (Priority: P2)
Como usuario, quiero ver mis recordatorios ordenados por fecha de vencimiento y
filtrar los que vencen hoy o en los próximos días, para priorizar mis tareas.

**Why this priority**: sin visualización la creación no aporta valor operativo.
**Independent Test**: dado un set de recordatorios con distintas fechas, listarlos y
verificar el orden ascendente por vencimiento.

**Acceptance Scenarios**:
1. **Given** varios recordatorios creados con distintas fechas, **When** el usuario abre la lista, **Then** el sistema los muestra ordenados del más próximo a vencer al más lejano.
2. **Given** recordatorios con vencimiento hoy, **When** el usuario aplica el filtro "vence hoy", **Then** el sistema muestra únicamente los que vencen en la fecha actual.

### User Story 3 - Marcar recordatorio como completado (Priority: P3)
Como usuario, quiero marcar un recordatorio como completado para distinguir las
tareas ya atendidas de las pendientes.

**Why this priority**: mejora la gestión pero no bloquea el flujo principal.
**Independent Test**: marcar un recordatorio pendiente y verificar que cambia de estado.

**Acceptance Scenarios**:
1. **Given** un recordatorio pendiente, **When** el usuario lo marca como completado, **Then** el sistema actualiza su estado y deja de resaltarlo como pendiente.

### Edge Cases
- **Given** la fecha de vencimiento está en el pasado al crear el recordatorio, **When** el usuario guarda, **Then** el sistema advierte pero permite crear el recordatorio como vencido.
- **Given** la fecha de vencimiento es hoy pero ya pasó la hora actual, **When** se lista, **Then** el sistema lo marca como "vencido" y no solo como "vence hoy".

## Requirements (EARS)

- **REQ-REM-001** — WHEN el usuario envía título, descripción y fecha de
  vencimiento válidos,
  THE SYSTEM SHALL crear un recordatorio único, persistente y con estado "pendiente".
  _Cumple: PRIN-TRACE-001 (presentación del binding)._

- **REQ-REM-002** — IF la fecha de vencimiento del recordatorio es igual o
  anterior a la fecha actual,
  THE SYSTEM SHALL marcar visualmente el recordatorio como "vencido".

- **REQ-REM-003** — WHEN el usuario solicita la lista de recordatorios,
  THE SYSTEM SHALL mostrarlos ordenados de forma ascendente por fecha de vencimiento.

- **REQ-REM-004** — IF el usuario aplica el filtro "vence hoy",
  THE SYSTEM SHALL mostrar únicamente los recordatorios cuya fecha de vencimiento
  coincide con la fecha actual.

- **REQ-REM-005** — WHEN el usuario marca un recordatorio como completado,
  THE SYSTEM SHALL actualizar su estado a "completado" y excluirlo del conteo de
  pendientes.

- **REQ-REM-006** — IF el título o la fecha de vencimiento faltan al crear,
  THE SYSTEM SHALL rechazar la creación e informar al usuario los campos obligatorios.

## Key Entities

- **Reminder**: representa un recordatorio. Atributos:
  - `id` (identificador único)
  - `title` (obligatorio)
  - `description` (opcional)
  - `due_date` (fecha de vencimiento, obligatoria)
  - `status` (pendiente | completado | vencido — derivado de `due_date` y acciones del usuario)
  - `created_at`, `updated_at` (auditoría)

## Success Criteria

- **SC-001**: Un usuario completa la creación de un recordatorio en menos de 30 segundos.
- **SC-002**: La lista de recordatorios muestra el orden correcto por vencimiento en el 100% de los casos.
- **SC-003**: El 95% de los usuarios identifica correctamente los recordatorios vencidos frente a los pendientes en la primera interacción.
- **SC-004**: El sistema responde a las acciones de listado/filtrado en menos de 1 segundo para conjuntos de hasta 1.000 recordatorios.

## Assumptions

- El sistema cuenta con un usuario autenticado; la autenticación se reutiliza del sistema existente (fuera de alcance de este feature).
- La fecha de vencimiento se gestiona sin zona horaria en v1 (fecha calendaria).
- Las notificaciones push/email están fuera de alcance de este feature (sólo gestión y visualización).
- El campo `description` es opcional y de texto plano; no se permite adjuntar archivos en v1.

## Trazabilidad normativa
| REQ | Principio / Policy Card | Fuente |
|-----|-------------------------|--------|
| REQ-REM-001 | PRIN-TRACE-001 | Constitución Valtx (trazabilidad capacidad) |
| REQ-REM-002 | PRIN-TRACE-001 | Constitución Valtx (binding estado derivado) |
| REQ-REM-003 | PRIN-TRACE-001 | Constitución Valtx (binding orden) |
| REQ-REM-004 | PRIN-TRACE-001 | Constitución Valtx (binding filtro) |
| REQ-REM-005 | PRIN-TRACE-001 | Constitución Valtx (binding estado) |
| REQ-REM-006 | PRIN-TRACE-001 | Constitución Valtx (binding validación) |

## Nota para el agente
No existe `src/reminders*` todavía. Este spec es la entrada para la fase de planning
(`/speckit-plan`). Cada requisito debe citarse en el código como `# REQ-REM-NNN`
para pasar el gate `ci/check_traceability.py`.
