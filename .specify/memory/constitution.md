# Constitución Valtx — Principios de Ingeniería (machine-readable)

> Versión: 1.0.0 · Owner: cto@valtx.pe · Última revisión: 2026-07-01
> Cada principio es citable por su `id`. El bundler inyecta SOLO los 3–5 principios
> relevantes al feature (selección por `applies_when`), no toda la constitución.
> Evidencia: selección relevante ~96% cumplimiento vs ~78% con constitución completa
> (Constitutional SDD, Marri 2026).

<!-- PRINCIPLE
id: PRIN-SEC-001
enforcement: MUST
cwe: CWE-89
applies_when: [db, sql, query, persistencia]
constraint: Toda consulta a base de datos DEBE usar sentencias parametrizadas o un ORM; prohibida la concatenación de strings con input del usuario.
pattern: "cursor.execute(sql, params)  # nunca f-strings con input"
rationale: Previene inyección SQL (CWE-89), vector #1 de exfiltración de datos.
-->

<!-- PRINCIPLE
id: PRIN-SEC-002
enforcement: MUST
cwe: CWE-522
applies_when: [auth, credenciales, secretos, token, password]
constraint: Ningún secreto, credencial o token puede estar hardcodeado en el código o en logs; deben leerse de un secret manager o variables de entorno.
pattern: "os.environ['X'] / secret-manager; nunca literales en el repo"
rationale: Evita fuga de credenciales (CWE-522) y facilita rotación.
-->

<!-- PRINCIPLE
id: PRIN-PRIV-001
enforcement: MUST
cwe: CWE-359
applies_when: [ubicacion, geolocalizacion, gps, pii, biometria, salud, menores]
constraint: Toda captura de datos personales DEBE estar precedida por una base legal válida (consentimiento explícito registrado u otra base del art. correspondiente) verificable en tiempo de ejecución, y DEBE citar la Policy Card aplicable.
pattern: "if not consent.is_valid(user, scope): abort()  # REQ + POL citados"
rationale: Cumplimiento de privacidad por diseño; enlaza con la Capa 0 de Gobierno Normativo.
-->

<!-- PRINCIPLE
id: PRIN-OBS-001
enforcement: SHOULD
applies_when: [servicio, api, endpoint, agente]
constraint: Todo endpoint o llamada a LLM DEBERÍA emitir una métrica de latencia, costo/tokens y resultado para observabilidad.
pattern: "with meter(feature, model): ..."
rationale: Habilita la mejora de Observabilidad de tokens/costo del flujo.
-->

<!-- PRINCIPLE
id: PRIN-TRACE-001
enforcement: MUST
applies_when: ['*']
constraint: Toda línea de código no trivial DEBE ser trazable a un REQ mediante una cita en comentario (`# REQ-XXX-NNN`). El código que cite un REQ inexistente se considera alucinación y BLOQUEA el merge.
pattern: "# REQ-GEO-001  (la cita habilita el orphan-check O(1))"
rationale: Detección automática de alucinaciones 86–88%, 0% FPR (traceSDD, Panda 2026). Los tests solos NO detectan alucinaciones.
-->

<!-- PRINCIPLE
id: PRIN-ARCH-001
enforcement: SHOULD
applies_when: [modulo, integracion, contrato, api]
constraint: Los contratos entre módulos DEBERÍAN definirse antes de la implementación (API-first) y no romperse sin versionar.
pattern: "contract-first; cambios breaking => nueva versión"
rationale: Reduce ciclos de integración (hasta -75% API-first).
-->
