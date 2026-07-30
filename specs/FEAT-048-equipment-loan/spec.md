---
id: FEAT-048
tags: [activos, prestamos, empleados, inventario]
policies: []
---

# Feature Specification: Registro de Préstamos de Equipos de Oficina

**Feature Branch**: `048-equipment-loan`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Desarrolla una feature simple para registrar préstamos de equipos de oficina entre empleados (qué equipo, quién lo presta, fecha de devolución)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar un préstamo de equipo (Priority: P1)

Como empleado, quiero registrar que tomo prestado un equipo de oficina identificable, indicando quién me lo entrega y cuándo lo devolveré, para que quede trazabilidad de la responsabilidad sobre el activo.

**Why this priority**: Es el valor central del feature. Sin el acto de registrar el préstamo, no existe el sistema.

**Independent Test**: Un usuario puede registrar un préstamo indicando equipo, prestador y fecha de devolución; el préstamo queda visible en el registro con fecha de creación. Entrega valor inmediatamente.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene el formulario de nuevo préstamo abierto, **When** selecciona un equipo, un prestador y una fecha de devolución y pulsa guardar, **Then** el préstamo queda registrado con estado "Activo" y una marca de tiempo de creación.
2. **Given** que el usuario intenta guardar sin seleccionar equipo, **When** pulsa guardar, **Then** el sistema bloquea el guardado e indica que el equipo es obligatorio.
3. **Given** que el usuario ingresa una fecha de devolución anterior a la fecha actual, **When** pulsa guardar, **Then** el sistema bloquea el guardado e indica que la fecha de devolución debe ser futura.

---

### User Story 2 - Consultar préstamos registrados y su estado (Priority: P2)

Como empleado o encargado de oficina, quiero ver la lista de préstamos registrados, ordenados por los más recientes y filtrables por estado (Activo / Devuelto / Vencido), para saber qué equipos están prestados y a quién.

**Why this priority**: Sin visibilidad, los préstamos registrados pierden utilidad operativa.

**Independent Test**: Con varios préstamos registrados, el usuario puede abrir la lista, filtrar por "Activo" y localizar un préstamo específico por equipo o por empleado.

**Acceptance Scenarios**:

1. **Given** que existen 10 préstamos de los cuales 4 están activos, **When** el usuario abre la lista y filtra por estado "Activo", **Then** solo se muestran los 4 préstamos activos ordenados del más reciente al más antiguo.
2. **Given** que existe un préstamo cuya fecha de devolución ya pasó y no ha sido devuelto, **When** el usuario abre la lista, **Then** el préstamo se muestra con estado "Vencido".
3. **Given** que el usuario escribe un nombre de empleado en el buscador, **When** filtra, **Then** solo se muestran los préstamos donde ese nombre aparece como prestatario o prestador.

---

### User Story 3 - Registrar la devolución de un equipo (Priority: P3)

Como prestador o encargado, quiero marcar un préstamo como devuelto en la fecha en que el equipo regresa, para mantener el registro de activos al día.

**Why this priority**: Refina el ciclo de vida del préstamo y mantiene la integridad del registro a largo plazo.

**Independent Test**: El usuario localiza un préstamo activo, marca la devolución y el estado pasa a "Devuelto" con la fecha de devolución real registrada.

**Acceptance Scenarios**:

1. **Given** un préstamo con estado "Activo", **When** el usuario pulsa "Registrar devolución" y confirma, **Then** el préstamo pasa a estado "Devuelto" y se registra la fecha real de devolución.
2. **Given** un préstamo ya devuelto, **When** el usuario intenta registrar devolución nuevamente, **Then** el sistema bloquea la acción e indica que el préstamo ya fue cerrado.

---

### Edge Cases

- ¿Qué sucede cuando se registra un préstamo de un equipo que ya tiene un préstamo activo sin devolver? → el sistema bloquea el nuevo préstamo e indica que el equipo ya está prestado y a quién.
- ¿Cómo se maneja una fecha de devolución nula? → se rechaza el guardado; la fecha de devolución es obligatoria para todo préstamo.
- ¿Qué pasa si un préstamo se registra con un empleado inexistente en el directorio? → el sistema solo acepta empleados válidos del directorio (campo autocompletable); nombres libres no se admiten.
- ¿Qué sucede al intentar registrar un préstamo con fecha de devolución a más de 365 días? → se permite con advertencia al usuario.

## Requirements *(mandatory)*

### Functional Requirements

- **REQ-PRESTAMO-001**: The system SHALL allow a user to register a loan capturing the equipment being loaned, the lender (quien presta), the borrower (quien recibe) and a return due date.
- **REQ-PRESTAMO-002**: When the user saves a loan without selecting equipment, lender or borrower, the system SHALL reject the save and SHALL indicate which mandatory fields are missing.
- **REQ-PRESTAMO-003**: The system SHALL reject any loan whose return due date is in the past relative to the current date.
- **REQ-PRESTAMO-004**: The system SHALL persist every loan with a unique identifier, a creation timestamp, the actor registering it, and an initial status of "Activo".
- **REQ-PRESTAMO-005**: When the user attempts to register a loan for equipment that already has an active loan, the system SHALL block the action and SHALL inform which loan currently holds the equipment.
- **REQ-PRESTAMO-006**: The system SHALL list loans ordered by creation date, most recent first, and SHALL allow filtering by status (Activo, Devuelto, Vencido).
- **REQ-PRESTAMO-007**: When a loan's return due date has passed and it has not been returned, the system SHALL display its status as "Vencido".
- **REQ-PRESTAMO-008**: The system SHALL allow an authorized user to register the return of a loaned equipment, changing its status to "Devuelto" and recording the actual return date.
- **REQ-PRESTAMO-009**: When a user attempts to register a return on a loan already marked "Devuelto", the system SHALL block the action and SHALL inform that the loan is closed.
- **REQ-PRESTAMO-010**: The system SHALL allow searching loans by borrower or lender name and SHALL filter the list accordingly.
- **REQ-PRESTAMO-011**: The system SHALL only accept employees existing in the directory as lender or borrower; free-text names SHALL be rejected.

### Key Entities *(include if feature involves data)*

- **Equipo**: activo de oficina identificable. Atributos: identificador único, nombre/descripción, tipo (opcional). Cada equipo puede estar prestado a lo sumo en un préstamo activo a la vez.
- **Empleado**: persona del directorio que puede actuar como prestador o prestatario. Atributos: identificador único del directorio, nombre.
- **Préstamo**: registro de un equipo entregado a un empleado por otro. Atributos: identificador único, equipo (ref), prestador (ref a Empleado), prestatario (ref a Empleado), fecha de préstamo, fecha de devolución pactada, fecha de devolución real (opcional), estado (Activo / Devuelto / Vencido), actor que registró el préstamo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can register a loan in under 60 seconds once the form is open.
- **SC-002**: 95% of loan searches by employee or status return matching results in under 500 milliseconds from the user's perspective.
- **SC-003**: 90% of users successfully register, filter and close a loan on first attempt without guidance.
- **SC-004**: The system supports a registry of up to 5,000 historical loans without noticeable degradation of the list view.

## Assumptions

- El directorio de empleados ya existe y puede consultarse para validar y autocompletar prestadores y prestatarios.
- El catálogo de equipos ya existe (o se mantiene informalmente) y un equipo se identifica de forma unívoca en v1.
- El alcance de v1 es un solo equipo prestado a un empleado a la vez (sin préstamos parciales ni Multiple prestatarios por préstamo).
- No se requiere autenticación avanzada en v1; todo empleado con acceso al sistema puede registrar y cerrar préstamos.
- No se envían recordatorios automáticos por correo en v1; el estado "Vencido" es visible en la lista, pero las notificaciones quedan fuera de alcance.
- La edición de un préstamo existente queda limitada al cierre (devolución); no se permite modificar la fecha pactada una vez registrado en v1.
- No hay sanciones ni cálculo de multas en v1; el feature se limita a registro y trazabilidad.
