---
id: FEAT-049
tags: [salas, reservas, reuniones, agenda, empleados]
policies: []
---

# Feature Specification: Reserva de Salas de Reuniones

**Feature Branch**: `049-meeting-room-booking`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Desarrolla una feature simple para reservar salas de reuniones (que sala, quien reserva, fecha y hora, duracion)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reservar una sala de reuniones (Priority: P1)

Como empleado, quiero seleccionar una sala, indicar la fecha y hora, la duración y mi nombre como responsable de la reserva, para asegurar que la sala esté disponible cuando la necesito.

**Why this priority**: Es el valor central del feature. Sin el acto de registrar la reserva, no existe el sistema.

**Independent Test**: Un usuario puede registrar una reserva indicando sala, responsable, fecha, hora y duración; la reserva queda visible con estado "Confirmada" y una marca de tiempo de creación. Entrega valor inmediatamente.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene el formulario de nueva reserva abierto, **When** selecciona una sala, un responsable, una fecha, una hora de inicio y una duración y pulsa guardar, **Then** la reserva queda registrada con estado "Confirmada" y una marca de tiempo de creación.
2. **Given** que el usuario intenta guardar sin seleccionar sala, **When** pulsa guardar, **Then** el sistema bloquea el guardado e indica que la sala es obligatoria.
3. **Given** que el usuario intenta guardar sin indicar responsable, **When** pulsa guardar, **Then** el sistema bloquea el guardado e indica que el responsable es obligatorio.
4. **Given** que el usuario intenta guardar sin indicar fecha, hora o duración, **When** pulsa guardar, **Then** el sistema bloquea el guardado e indica cuál campo obligatorio falta.

---

### User Story 2 - Evitar reservas solapadas en la misma sala (Priority: P2)

Como empleado, quiero que el sistema me impida reservar una sala en un horario que ya está ocupado, para que dos reservas no colisionen.

**Why this priority**: Garantiza la integridad del calendario de la sala; sin esta validación, una reserva no tiene valor confiable (riesgo de doble uso).

**Independent Test**: Dada una reserva existente para la sala "Andes" de 10:00 a 11:00, el usuario intenta reservar la misma sala de 10:30 a 11:30; el sistema bloquea la acción e indica el conflicto con la reserva existente.

**Acceptance Scenarios**:

1. **Given** que existe una reserva confirmada para la sala "Andes" de 10:00 a 11:00 el 2026-08-01, **When** el usuario intenta reservar la misma sala de 10:30 a 11:30 el mismo día, **Then** el sistema bloquea el guardado e indica que la sala ya está reservada en ese horario.
2. **Given** que existe una reserva confirmada para la sala "Andes" de 10:00 a 11:00 el 2026-08-01, **When** el usuario intenta reservar la misma sala de 11:00 a 12:00 el mismo día, **Then** la reserva se registra correctamente, ya que el fin de la reserva previa coincide con el inicio de la nueva (sin solapamiento).
3. **Given** que existe una reserva confirmada para la sala "Andes" de 10:00 a 11:00 el 2026-08-01, **When** el usuario intenta reservar la sala "Pacifico" de 10:30 a 11:30 el mismo día, **Then** la reserva se registra correctamente, ya que es una sala diferente.

---

### User Story 3 - Consultar reservas registradas (Priority: P3)

Como empleado o encargado, quiero ver la lista de reservas, ordenadas por las más recientes y filtrables por sala y fecha, para saber qué salas están reservadas y cuándo.

**Why this priority**: Sin visibilidad, las reservas registradas pierden utilidad operativa para los usuarios.

**Independent Test**: Con varias reservas registradas, el usuario puede abrir la lista, filtrar por una sala específica y localizar reservas por fecha o responsable.

**Acceptance Scenarios**:

1. **Given** que existen 12 reservas de las cuales 5 corresponden a la sala "Andes", **When** el usuario abre la lista y filtra por la sala "Andes", **Then** solo se muestran las 5 reservas de esa sala, ordenadas de la más reciente a la más antigua.
2. **Given** que el usuario selecciona la fecha 2026-08-01, **When** filtra la lista por fecha, **Then** solo se muestran las reservas cuya fecha de inicio coincide con ese día.
3. **Given** que el usuario escribe el nombre de un responsable en el buscador, **When** filtra, **Then** solo se muestran las reservas donde ese nombre es el responsable.

---

### Edge Cases

- ¿Qué sucede cuando se reserva una sala para una fecha u hora pasada? → el sistema bloquea el guardado e indica que la fecha/hora de inicio debe ser futura.
- ¿Cómo se maneja una duración de cero minutos o negativa? → se rechaza el guardado; la duración debe ser un valor positivo (ej. mínimo 15 minutos).
- ¿Qué pasa si una reserva se registra con un responsable inexistente en el directorio? → el sistema solo acepta empleados válidos del directorio (campo autocompletable); nombres libres no se admiten.
- ¿Qué sucede al intentar reservar con una duración mayor a 8 horas? → se permite con advertencia al usuario, ya que excede una jornada laboral típica.
- ¿Qué pasa si dos usuarios intentan reservar la misma sala en horarios solapados casi al mismo tiempo? → la primera reserva en confirmarse gana; la segunda recibe el mensaje de conflicto.

## Requirements *(mandatory)*

### Functional Requirements

- **REQ-RESERVA-001**: The system SHALL allow a user to register a booking capturing the meeting room, the responsible person (quien reserva), the date, the start time and the duration.
- **REQ-RESERVA-002**: When the user saves a booking without selecting room, responsible, date, start time or duration, the system SHALL reject the save and SHALL indicate which mandatory fields are missing.
- **REQ-RESERVA-003**: The system SHALL reject any booking whose start date and time is in the past relative to the current date and time.
- **REQ-RESERVA-004**: The system SHALL reject any booking whose duration is zero or negative; duration SHALL be a positive value with a minimum of 15 minutes.
- **REQ-RESERVA-005**: The system SHALL persist every booking with a unique identifier, a creation timestamp, the actor registering it, and an initial status of "Confirmada".
- **REQ-RESERVA-006**: When the user attempts to register a booking for a room that already has a confirmed booking with an overlapping time range on the same date, the system SHALL block the action and SHALL inform which existing booking conflict was detected (room, start and end time).
- **REQ-RESERVA-007**: Two bookings on the same room SHALL be considered non-overlapping when the end time of one equals the start time of the other; the system SHALL allow consecutive bookings in that case.
- **REQ-RESERVA-008**: The system SHALL compute the end time of a booking as the start time plus the duration.
- **REQ-RESERVA-009**: The system SHALL list bookings ordered by creation date, most recent first, and SHALL allow filtering by room and by date.
- **REQ-RESERVA-010**: The system SHALL allow searching bookings by responsible person name and SHALL filter the list accordingly.
- **REQ-RESERVA-011**: The system SHALL only accept employees existing in the directory as the responsible person; free-text names SHALL be rejected.
- **REQ-RESERVA-012**: The system SHALL validate that the selected room exists in the room catalog before persisting the booking.

### Key Entities *(include if feature involves data)*

- **Sala**: espacio físico identificable para reuniones. Atributos: identificador único, nombre, capacidad (opcional), ubicación (opcional). Una sala puede tener múltiples reservas, pero a lo sumo una reserva confirmada por franja horaria.
- **Empleado**: persona del directorio que actúa como responsable de la reserva. Atributos: identificador único del directorio, nombre.
- **Reserva**: registro del uso de una sala por un empleado en una franja horaria. Atributos: identificador único, sala (ref), responsable (ref a Empleado), fecha, hora de inicio, duración, hora de fin (calculada), estado (Confirmada / Cancelada), actor que registró la reserva, marca de tiempo de creación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can register a booking in under 60 seconds once the form is open.
- **SC-002**: 95% of booking searches by room, date or responsible return matching results in under 500 milliseconds from the user's perspective.
- **SC-003**: 90% of users successfully register, filter and locate a booking on first attempt without guidance.
- **SC-004**: The system supports a registry of up to 10,000 historical bookings without noticeable degradation of the list view.

## Assumptions

- El directorio de empleados ya existe y puede consultarse para validar y autocompletar responsables de reservas.
- El catálogo de salas de reuniones ya existe (o se mantiene informalmente) y una sala se identifica de forma unívoca en v1.
- El alcance de v1 es una sola sala reservada por un empleado en una franja horaria (sin reservas recurrentes ni reservas multisede).
- No se requiere autenticación avanzada en v1; todo empleado con acceso al sistema puede registrar reservas.
- No se envían recordatorios automáticos por correo ni invitaciones a calendarios externos en v1; la cancelación de una reserva queda fuera de alcance (solo registro y consulta).
- La edición de una reserva existente queda limitada a la creación; no se permite modificar fecha, hora o duración una vez registrada en v1.
- La zona horaria es única y consistente (no se manejan reservas跨-zona horaria en v1).
- Las reservas se gestionan en incrementos de 15 minutos (alineación estándar de franjas horarias).
