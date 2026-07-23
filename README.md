# Valtx SDD Framework — harness de referencia

Implementación ejecutable del flujo Spec-Driven de Valtx, con la **Capa 0 de
Gobierno Normativo** y los gates de calidad derivados de la investigación
(Constitutional SDD, traceSDD, Code→Contract, Prompt→Process).

Este repo es un **monorepo de prueba**: contiene la gobernanza + un producto demo
para poder correr todo en una sola máquina. En producción se separa (ver §6).

> Estado actual: **corre 100% local sin cloud** (git + python). El wiring a
> GitHub Actions / Notion / Linear / spec-kit son los pasos §4–§5 que requieren
> tus credenciales.

---

## 1. Qué hay aquí

```
.specify/memory/
  constitution.md              # principios machine-readable (id·MUST/SHOULD·CWE·pattern)
  policies/                    # Capa 0 — Policy Cards (Ley 29733 PE + DS 016-2024-JUS)
    POL-PE-CONSENT-001.yaml ...  #   9 tarjetas: consentimiento, sensibles, ubicación,
    build_policies_peru.py       #   minimización/retención, ARCO, seguridad, transfronterizo,
                                 #   registro RNPDP, brechas. Generadas por este script (auditable).
cost/
  cost_model.py                # TECHO de costo mensual por escala -> Valtx_SDD_Modelo_Costo.xlsx
ci/
  policy_freshness.py          # GATE 1 · vigencia normativa — 0 tokens LLM
  context_bundler.py           # selección 3–5 principios/cards — palanca de tokens
  check_traceability.py        # GATE 2 · orphan-REQ = detección de alucinaciones
  coverage_graph.py            # GATE 3 · cobertura EARS↔Gherkin 100% (NetworkX)
  token_meter.py               # observabilidad de tokens/costo
  run_gates.py                 # orquestador local (= lo que hará la CI)
specs/FEAT-042-geo-checkin/    # feature demo (spec EARS + Gherkin)
src/geo_checkin.py             # implementación demo (con 2 fallos sembrados)
.github/workflows/             # SDD Orchestrator (PR + repository_dispatch)
```

## 2. Correrlo YA (local, sin cloud)

```bash
pip install -r requirements.txt
SDD_TODAY=2026-07-23 python ci/run_gates.py FEAT-042-geo-checkin
```

Verás (esperado):
- **GATE 1 PASS** — 9 Policy Cards de la Ley 29733 vigentes (para probar el catch,
  pon `vigencia_hasta` en el pasado en cualquier tarjeta → alerta al abogado, 0 tokens).
- **bundler** — 2/6 principios, 6/9 cards por triggers, ~68% menos tokens que el corpus.
- **GATE 2 BLOCK** — `REQ-GEO-009` citado en código pero inexistente en el spec = alucinación (sembrada).
- **GATE 3 PASS** — 3/3 REQ con escenario Gherkin.

### Ponerlo 100% en verde
`src/geo_checkin.py`: elimina `recommend_places`/`_nearby` (la feature alucinada) o
añade `REQ-GEO-004` al spec + su escenario Gherkin. Re-corre → todo verde = apto para PR.

## 3. Los 8 pasos del flujo ↔ dónde viven

| Fase del diagrama | Artefacto/ën este repo | Gate asociado |
|---|---|---|
| Constitution Creation | `.specify/memory/constitution.md` | — |
| **Capa 0 · Gobierno Normativo** | `.specify/memory/policies/*` + `policy_freshness.py` + `context_bundler.py` | GATE 1 |
| Feature + EARS | `specs/<F>/spec.md` (front-matter `tags`, REQ + normas citadas) | — |
| Tech Spec / Tasks | `spec-kit` (`/speckit.plan`, `/speckit.tasks`) | — |
| Gherkin Scenario | `specs/<F>/*.feature` (`@REQ-...`) | GATE 3 (cobertura) |
| Code Development | `src/*` con citas `# REQ-...` | GATE 2 (trazabilidad) |
| Gherkin Development / QA | step definitions + deploy QA | (tests) |
| Update Knowledge Base | KB/Vertex + merge | — |

## 4. Wiring a spec-kit + GitHub Actions (tus pasos)

1. **spec-kit** (genera specify/plan/tasks/gherkin con los slash-commands del flujo):
   ```bash
   uvx --from git+https://github.com/github/spec-kit specify init
   ```
2. **Repo en GitHub** y push:
   ```bash
   gh repo create valtx-<producto> --private --source . --push
   ```
3. **Secrets** (Settings → Secrets → Actions): `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
   `LINEAR_API_KEY`, `NOTION_TOKEN`, `VERTEX_*`. El workflow ya está en
   `.github/workflows/sdd-orchestrator.yml` (corre los 3 gates en cada PR).
4. **Branch protection** en `main`/`dev`: exigir que los checks del SDD Orchestrator
   pasen + `CODEOWNERS` (el abogado como owner de `.specify/memory/policies/`).

## 5. Disparadores Notion / Linear (repository_dispatch)

El flujo arranca en lenguaje natural desde Notion/Linear. Ambos disparan la CI por
webhook → `repository_dispatch`:

```bash
curl -X POST https://api.github.com/repos/valtx/<repo>/dispatches \
  -H "Authorization: token $GH_PAT" \
  -d '{"event_type":"notion-feature","client_payload":{"feature":"FEAT-043","prompt":"..."}}'
```

- **Notion** → capture/KB: un webhook (Automations o un pequeño relay) emite el dispatch
  `notion-feature` al crear una página de feature.
- **Linear** → ejecución: webhook `linear-task` al mover un issue a "In Progress".

El `client_payload.prompt` es el lenguaje natural del humano que una instancia de
refinamiento convierte a spec vía spec-kit.

## 6. Split a producción (multi-repo)

- `valtx-governance` → `constitution.md` maestra + `policies/` + los `ci/*.py`
  reutilizables (publicados como acción/paquete). El abogado es CODEOWNER de `policies/`.
- `valtx-<producto>` → `specs/`, `src/`, y una constitución por repo que hereda de la
  maestra. La CI trae los gates desde governance.

## 7. Pendiente (requiere credenciales/decisiones tuyas)

- [ ] Crear la org/repos en GitHub y cargar secrets.
- [ ] Conectar los webhooks de Notion y Linear.
- [ ] Elegir modelos por fase (tiering Haiku/Sonnet/Opus) y activar `token_meter` con usage real.
- [ ] SAST/secret-scanning (CodeQL) + preview efímero por feature.
- [ ] Poblar `policies/` con la normativa real de Valtx (destilada a Policy Cards).

Estos pasos alimentan el **dimensionamiento de costo/techo** que sigue como
entregable aparte: con `token_meter` midiendo runs reales tendrás el costo por
feature para proyectar el mensual a escala.
