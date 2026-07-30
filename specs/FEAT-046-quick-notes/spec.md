---
id: FEAT-046
tags: [notas, contenido-usuario]
policies: []
---

# Feature Specification: Sistema de Notas Rápidas

**Feature Branch**: `046-quick-notes`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Redacta un spec.md corto para un sistema de notas rápidas, en formato EARS con REQ-IDs"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear nota rápida (Priority: P1)

Como usuario, quiero crear una nota con título y contenido de texto en una sola acción para capturar información sin fricción.

**Why this priority**: Es el valor central. Sin captura de notas, no existe producto.

**Independent Test**: Un usuario puede abrir la app, escribir una nota y guardar; la nota queda visible en la lista. Entrega valor immediamente.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene la app abierta, **When** escribe texto y pulsa guardar, **Then** la nota aparece en la lista con marca de tiempo.
2. **Given** que el campo de título está vacío, **When** el usuario guarda, **Then** el sistema usa las primeras palabras del contenido como título autogenerado.

---

### User Story 2 - Listar y buscar notas (Priority: P2)

Como usuario, quiero ver todas mis notas ordenadas por recencia y filtrarlas por texto para encontrar una nota específica.

**Why this priority**: Sin descubrimiento, las notas capturadas pierden utilidad.

**Independent Test**: Con varias notas guardadas, el usuario puede buscar y localizar una por palabra clave.

**Acceptance Scenarios**:

1. **Given** que existen 10 notas, **When** el usuario abre la app, **Then** se muestran las más recientes primero.
2. **Given** que el usuario escribe "reunión" en el buscador, **When** filtra, **Then** solo se muestran las notas que contienen ese término en título o contenido.

---

### User Story 3 - Editar y eliminar notas (Priority: P3)

Como usuario, quiero editar y eliminar notas existentes para mantener mi colección relevante.

**Why this priority**: Refina y mantiene el contenido a largo plazo.

**Independent Test**: El usuario edita una nota y luego la elimina; la lista refleja los cambios.

**Acceptance Scenarios**:

1. **Given** una nota existente, **When** el usuario edita el contenido y guarda, **Then** la versión actualizada reemplaza a la anterior conservando el ID.
2. **Given** una nota existente, **When** el usuario selecciona eliminar y confirma, **Then** la nota desaparece de la lista de forma permanente.

---

### Edge Cases

- ¿Qué sucede cuando el contenido de una nota excede el límite máximo de caracteres? → truncado con advertencia.
- ¿Cómo maneja el sistema una nota duplicada (mismo título y contenido)? → permitida; cada nota tiene ID único.
- ¿Qué pasa al guardar sin conexión? → la nota se persiste localmente y sincroniza al restablecerse la conexión.

## Requirements *(mandatory)*

### Functional Requirements

- **REQ-NOTAS-001**: The system SHALL allow a user to create a note containing a title and a text body.
- **REQ-NOTAS-002**: When the user saves a note without a title, the system SHALL auto-generate a title from the first words of the body.
- **REQ-NOTAS-003**: The system SHALL persist every note with a unique identifier and a creation timestamp.
- **REQ-NOTAS-004**: The system SHALL display notes ordered by last modification time, the most recent first.
- **REQ-NOTAS-005**: When the user enters a search term, the system SHALL filter the list to notes whose title or body contain the term.
- **REQ-NOTAS-006**: The system SHALL allow the user to edit an existing note while preserving its identifier.
- **REQ-NOTAS-007**: When the user requests deletion and confirms the action, the system SHALL permanently remove the note.
- **REQ-NOTAS-008**: The system SHALL limit note body length to 5000 characters and SHALL warn the user when the limit is approached.

### Key Entities *(include if feature involves data)*

- **Nota**: unidad de contenido. Atributos: id único, título (opcional/autogenerado), cuerpo de texto, fecha de creación, fecha de última modificación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create and save a note in under 15 seconds.
- **SC-002**: 95% of searches return matching results in under 500 milliseconds from the user's perspective.
- **SC-003**: 90% of users successfully create, find, and delete a note on first attempt without guidance.
- **SC-004**: The system supports a personal collection of up to 1000 notes without noticeable degradation of the list view.

## Assumptions

- Cada usuario gestiona únicamente su propia colección de notas (sin colaboración multiusuario en v1).
- El usuario dispone de un dispositivo con conexión a internet intermitente; la persistencia local cubre los huecos.
- No se requiere autenticación compleja; v1 asume un único perfil por dispositivo.
- La sincronización entre dispositivos queda fuera del alcance de v1.
- Las notas se almacenan como texto plano; el formato enriquecido queda fuera de alcance de v1.
