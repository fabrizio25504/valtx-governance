---
id: FEAT-044
titulo: Exportación de datos personales (portabilidad)
tags: [exportar_datos, portabilidad, pii, dsar]
policies: [POL-PE-ARCO-005]
owner: producto@valtx.pe
estado: draft
---

# FEAT-044 · Exportación de datos personales (portabilidad)

## Contexto
El titular puede solicitar una copia de sus datos personales en formato estructurado
(derecho de portabilidad). La Capa 0 activó `POL-PE-ARCO-005`.

## Requisitos (EARS) — cada uno cita la norma que cumple

- **REQ-EXP-001** — WHEN el usuario solicita exportar sus datos,
  THE SYSTEM SHALL generar un archivo estructurado (JSON) con sus datos personales.
  _Cumple: POL-PE-ARCO-005 (Ley 29733 Art. 19; portabilidad)._

- **REQ-EXP-002** — THE SYSTEM SHALL atender la solicitud de exportación en un
  máximo de 10 días.
  _Cumple: POL-PE-ARCO-005 (plazo legal de respuesta)._

## Normas cumplidas (trazable)
| REQ | Policy Card | Fuente (artículo) |
|-----|-------------|-------------------|
| REQ-EXP-001 | POL-PE-ARCO-005 | Ley 29733 Art. 19 |
| REQ-EXP-002 | POL-PE-ARCO-005 | Ley 29733 Art. 19-20 |

## Nota para el agente
Crear `src/data_export.py`. No hay código aún — este feature es la entrada del agente.
