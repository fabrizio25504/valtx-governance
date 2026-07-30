---
id: FEAT-047
titulo: Registro de tickets de atención TI
tags: [tickets, soporte-ti, formulario, registros, pii]
policies: [POL-PE-MINIM-004, POL-PE-REGISTRO-008, POL-PE-SEG-006]
owner: producto@valtx.pe
estado: draft
---

<!-- CONVENCIÓN VALTX (obligatoria para pasar los gates de CI):
  1. Rellena `tags` con los triggers reales → la Capa 0 carga las Policy Cards
     relevantes y valida su vigencia (ci/policy_freshness.py + context_bundler.py).
  2. Cada requisito funcional lleva un ID REQ-XXX-### y CITA la Policy Card / principio
     que cumple (ver sección "Trazabilidad normativa" abajo).
  3. El código debe citar esos REQ en comentarios (# REQ-XXX-###) — ci/check_traceability.py
     bloquea REQ inexistentes (alucinaciones).
  4. Los .feature deben etiquetar cada escenario con @REQ-XXX-### — ci/coverage_graph.py
     exige 100% de cobertura EARS↔Gherkin.
-->

# Feature Specification: Registro de tickets de atención TI

**Feature Branch**: `047-ti-ticket-registration`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "desarrolla una feature que sirva para registrar tickets de atencion TI, algo simple"

## Contexto

El equipo de TI necesita un mecanismo simple y auditable para receiving y trackear solicitudes
de soporte de los usuarios internos (incidencias y pedidos puntuales). Este feature cubre el
ciclo mínimo: abrir un ticket describiendo el problema, dejarlo registrado con estado
inicial, listar los tickets abiertos, y avanzar su estado hasta el cierre. La captura
incluye datos personales del solicitante (nombre/área y contacto) por lo que la Capa 0
activa `POL-PE-MINIM-004` (minimización de campos), `POL-PE-REGISTRO-008` (inscripción del
banco de datos en el RNPDP antes de go-live) y `POL-PE-SEG-006` (medidas de seguridad del
tratamiento).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar un ticket de soporte (Priority: P1)

Como colaborador, quiero abrir un ticket describiendo mi incidencia o solicitud TI para
que el equipo de soporte pueda atenderla y dejar constancia de la misma.

**Why this priority**: Es el valor central del feature. Si no se puede registrar un ticket,
no existe cola de atención ni trazabilidad.

**Independent Test**: Un colaborador completa el formulario mínimo (solicitante, asunto,
descripción, categoría, prioridad), envía y ve su ticket en la lista con un código
identificador y estado "Abierto". Entrega valor inmediatamente.

**Acceptance Scenarios**:

1. **Given** que el colaborador tiene el formulario abierto, **When** completa los campos
   obligatorios y pulsa "Registrar", **Then** el sistema crea el ticket con un
   identificador único, marca temporal de creación y estado "Abierto".
2. **Given** que el colaborador omite un campo obligatorio (p. ej. asunto), **When**
   intenta registrar, **Then** el sistema bloquea el envío e indica el campo faltante
   sin perder el resto de la información ingresada.

---

### User Story 2 - Consultar tickets registrados (Priority: P2)

Como miemmbro del equipo de soporte TI, quiero ver la lista de tickets ordenados por
recencia y poder filtrar por estado/categoría para organizar la atención.

**Why this priority**: Sin visibilidad de la cola, los tickets registrados no se atienden.
Permite priorizar y evitar duplicados.

**Independent Test**: Con varios tickets registrados, el soportista abre la lista, aplica
un filtro por estado "Abierto" y ve solo los tickets pendientes de atención.

**Acceptance Scenarios**:

1. **Given** que existen 20 tickets en distintos estados, **When** el soportista abre la
   lista, **Then** se muestran los más recientes primero con código, asunto, prioridad y
   estado.
2. **Given** que el soportista filtra por estado "Abierto", **When** aplica el filtro,
   **Then** sólo permanecen visibles los tickets con ese estado.

---

### User Story 3 - Avanzar y cerrar un ticket (Priority: P3)

Como soportista, quiero cambiar el estado de un ticket (En Proceso → Resuelto → Cerrado)
y dejar una nota de resolución para cerrar el loop con el solicitante.

**Why this priority**: Cambia el ticket de un registro pasivo a un flujo atendible y deja
evidencia de cierre auditable.

**Independent Test**: El soportista toma un ticket "Abierto", lo pasa a "En Proceso",
luego "Resuelto" con una nota, y finalmente "Cerrado"; la lista refleja el último estado
y la nota queda visible en el historial del ticket.

**Acceptance Scenarios**:

1. **Given** un ticket en estado "Abierto", **When** el soportista cambia el estado a
   "En Proceso", **Then** el sistema registra el cambio con marca temporal y usuario
   responsable.
2. **Given** un ticket en estado "Resuelto", **When** el soportista agrega la nota de
   resolución y lo pasa a "Cerrado", **Then** el ticket permanece consultable pero ya
   no aparece en el filtro de "Abierto".

---

### Edge Cases

- ¿Qué sucede cuando dos usuarios intentan registrar tickets con el mismo asunto? →
  permitido; cada ticket recibe su propio ID único y se gestionan como colas separadas.
- ¿Cómo se maneja un ticket abandonado en "En Proceso" mucho tiempo? → el sistema lo
  marca como "Estancado" tras un umbral configurable de días sin actualización, sin
  cerrarlo automáticamente.
- ¿Qué pasa si el solicitante reabre un ticket ya "Cerrado"? → se crea un nuevo ticket
  vinculado al original por referencia, no se reabre el cerrado.
- ¿Qué sucede si se envía una descripción vacía o solo con espacios? → el sistema
  rechaza el envío y solicita contenido significativo.

## Requirements *(mandatory)*

### Functional Requirements

- **REQ-TICK-001** — The system SHALL allow a collaborator to register an IT support
  ticket capturing only the minimum necessary fields: requester identification,
  contact, subject, description, category and priority.
  _Cumple: POL-PE-MINIM-004 (Ley 29733 Art. 6, 7) · PRIN-PRIV-001._

- **REQ-TICK-002** — When the requester submits a ticket with an empty mandatory field,
  THE SYSTEM SHALL block the submission, indicate the missing field and preserve the
  entered data.

- **REQ-TICK-003** — When a ticket is successfully registered, THE SYSTEM SHALL assign
  a unique identifier, the initial state "Abierto", and a creation timestamp.
  _Cumple: POL-PE-REGISTRO-008 (registro trazable) · PRIN-SEC-001._

- **REQ-TICK-004** — The system SHALL persist tickets and their state-change history
  using parameterized queries / ORM and SHALL NOT concatenate user input into queries.
  _Cumple: PRIN-SEC-001 (CWE-89)._

- **REQ-TICK-005** — The system SHALL display tickets ordered by latest activity, the
  most recent first, exposing at least identifier, subject, priority and state.

- **REQ-TICK-006** — When the user applies a filter by state and/or category,
  THE SYSTEM SHALL restrict the list to only matching tickets.

- **REQ-TICK-007** — The system SHALL allow an authorized support agent to change a
  ticket's state across the lifecycle (Abierto → En Proceso → Resuelto → Cerrado),
  recording each transition with timestamp and responsible user.
  _Cumple: POL-PE-SEG-006 (logs de accesos conservados ≥ 2 años) · PRIN-OBS-001._

- **REQ-TICK-008** — When a ticket transitions to "Resuelto", THE SYSTEM SHALL require a
  resolution note and SHALL persist it as part of the ticket history.

- **REQ-TICK-009** — When a ticket has no state update for more than the configured
  stalling threshold (default 7 days), THE SYSTEM SHALL flag it as "Estancado" without
  auto-closing it.

- **REQ-TICK-010** — The system SHALL store requester personal data (name, contact)
  encrypted at rest and in transit, and SHALL log access to ticket records keeping
  those logs for at least 2 years.
  _Cumple: POL-PE-SEG-006 (Ley 29733 Art. 9, 16) · PRIN-SEC-002._

- **REQ-TICK-011** — When a new ticket datastore containing personal data is created,
  THE SYSTEM SHALL block production go-live until its registration in the RNPDP is
  recorded.
  _Cumple: POL-PE-REGISTRO-008 (Ley 29733 Art. 34)._

### Key Entities *(include if feature involves data)*

- **Ticket**: unidad de solicitud de soporte. Atributos: identificador único, solicitante
  (referencia), contacto, asunto, descripción, categoría, prioridad, estado, fecha de
  creación, fecha de última actualización.
- **Estado de Ticket**: valor controlado del conjunto {Abierto, En Proceso, Resuelto,
  Cerrado, Estancado}. Solo el equipo de soporte puede avanzar hacia "Cerrado".
- **Histórico de Ticket**: registro de cada cambio de estado con marca temporal y usuario
  responsable; incluye la nota de resolución al cerrar.
- **Solicitante**: identidad del colaborador que abre el ticket; datos mínimos de
  contacto (correo corporativo / extensión). No se capturan datos sensibles en v1.
- **Categoría**: clasificación del ticket (p. ej. Hardware, Red, Software, Acceso);
  lista configurable por el equipo de soporte.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un colaborador puede completar el formulario y registrar un ticket en
  menos de 1 minuto.
- **SC-002**: 95% de los tickets registrados aparecen en la lista consultable en menos
  de 1 segundo desde la perspectiva del usuario.
- **SC-003**: 90% de los solicitantes reciben confirmación visible de su ticket con
  identificador en su primer intento, sin asistencia.
- **SC-004**: 100% de los tickets cerrados contienen nota de resolución y al menos un
  registro de transición de estado trazable por usuario y timestamp.
- **SC-005**: El sistema soporta una cola de hasta 5,000 tickets activos sin
  degradación perceptible al filtrar u ordenar la lista.

## Trazabilidad normativa (EARS↔Policy)

| REQ | Policy Card | Fuente (artículo) | Principio |
|-----|-------------|-------------------|-----------|
| REQ-TICK-001 | POL-PE-MINIM-004 | Ley 29733 Art. 6, 7 | PRIN-PRIV-001 |
| REQ-TICK-003 | POL-PE-REGISTRO-008 | Ley 29733 Art. 34 | PRIN-TRACE-001 |
| REQ-TICK-004 | — | CWE-89 | PRIN-SEC-001 |
| REQ-TICK-007 | POL-PE-SEG-006 | Ley 29733 Art. 9, 16 | PRIN-OBS-001 |
| REQ-TICK-010 | POL-PE-SEG-006 | Ley 29733 Art. 9, 16 | PRIN-SEC-002 |
| REQ-TICK-011 | POL-PE-REGISTRO-008 | Ley 29733 Art. 34 | PRIN-PRIV-001 |

## Assumptions

- Los solicitantes son colaboradores internos con credenciales corporativas; v1 no está
  expuesto al público externo.
- Se reutiliza el directorio de usuarios / autenticación existente de la organización;
  no se desarrolla un nuevo esquema de autenticación en este feature.
- Los datos personales capturados se limitan a nombre, correo corporativo y área; no se
  recogen datos sensibles (salud, biométricos, financieros) en v1.
- v1 cubre apertura, listado, filtrado, cambio de estado y cierre. Funciones avanzadas
  (asignación a técnicos, SLA con tiempos strictos, encuestas de satisfacción, exportes
  reportísticos y notificaciones por correo) quedan fuera de alcance de v1.
- La retención de tickets y logs de acceso cumplirá el mínimo legal de 2 años
  (POL-PE-SEG-006); la purga posterior se define por separado en la política de
  retención TI.
- La inscripción del banco de datos en el RNPDP (POL-PE-REGISTRO-008) debe gestionarse
  con Legal antes del go-live; el feature lo bloquea como CHEQUEO, no lo automatiza.
- Los IDs de tickets siguen un formato legible y secuencial dentro del contexto del
  feature (p. ej. `TICK-00001`), sin particularidades de seguridad criptográfica.
- Se asume conexión a red interna estable; la operación offline queda fuera de alcance
  de v1.
