# Guía del equipo — Framework SDD de Valtx (flujo completo, paso a paso)

> Esta guía permite que **cualquier miembro del equipo** replique el proceso completo:
> desde una idea en lenguaje natural hasta código mergeado, cumpliendo la normativa
> (Ley 29733 de Protección de Datos del Perú) y con el costo medido. No omite ningún paso.
>
> Si algo falla, salta al final: **§12 Troubleshooting** cubre los errores reales que ya encontramos.

---

## Índice
1. [Qué es este sistema (panorama)](#1-qué-es-este-sistema-panorama)
2. [Arquitectura y el ciclo de vida de un feature](#2-arquitectura-y-el-ciclo-de-vida-de-un-feature)
3. [Requisitos previos (qué instalar / qué cuentas)](#3-requisitos-previos)
4. [Estructura del repositorio](#4-estructura-del-repositorio)
5. [Puesta en marcha local (clonar y correr los gates)](#5-puesta-en-marcha-local)
6. [El ciclo de un feature — paso a paso](#6-el-ciclo-de-un-feature-paso-a-paso)
7. [Las entradas automáticas (Notion / Linear vía Pipedream)](#7-las-entradas-automáticas)
8. [Los 4 gates en detalle](#8-los-4-gates-en-detalle)
9. [La Capa 0 · Gobierno Normativo](#9-la-capa-0--gobierno-normativo)
10. [Tokens y costo (el detalle completo)](#10-tokens-y-costo)
11. [Configuración inicial del repo (solo el admin, una vez)](#11-configuración-inicial-del-repo)
12. [Troubleshooting (errores reales y su fix)](#12-troubleshooting)
13. [Glosario](#13-glosario)

---

## 1. Qué es este sistema (panorama)

Es un framework de **Spec-Driven Development (SDD)**: el código no se escribe "a mano y luego se documenta", sino que **nace de una especificación** que a su vez cumple una **constitución** y una capa de **normativa legal**. Un agente de IA implementa; una batería de **gates automáticos** impide que entre código que no sea trazable a un requisito, o que cite una ley que no aplica.

La cadena canónica es:

```
Constitución  →  Capa 0 (normativa)  →  Feature + EARS  →  Gherkin  →  Código  →  Actualiza KB
```

Tres ideas que lo hacen distinto:
- **Capa 0 · Gobierno Normativo**: antes de escribir un feature, un router determinista decide qué leyes aplican (ej. geolocalización → consentimiento) y el spec debe citarlas. 0 tokens de LLM.
- **Agente agnóstico al LLM**: el que implementa es `aider`; cambias de modelo (gpt-4o-mini, gpt-4o, Claude…) con un flag. La gobernanza no depende del modelo.
- **Los gates son la garantía, no el prompt**: aunque el agente alucine, los gates bloquean. Ya lo comprobamos (un agente barato metió citas legales falsas y el gate las cazó).

El diagrama de referencia vive en la raíz del proyecto: `Flujo_SDD_Estandard.svg` / `Flujo SDD Valtx.png`.

---

## 2. Arquitectura y el ciclo de vida de un feature

```
   IDEA / PROMPT
        │
        │  (entra por Notion, Linear o CLI)
        ▼
┌───────────────────────┐
│  agent-specify.yml    │  ← Capa 0 router decide policies aplicables
│  (redacta el spec)    │    aider escribe spec.md + .feature (EARS + Gherkin)
└───────────┬───────────┘
            │  abre PR "spec: FEAT-xxx"
            ▼
      REVISIÓN HUMANA  ──► merge del spec
            │
            │  (Linear label "implement" o CLI)
            ▼
┌───────────────────────┐
│  agent-implement.yml  │  ← retrieval de contexto (Vertex AI Search)
│  (implementa código)  │    aider escribe src/*.py citando cada REQ
└───────────┬───────────┘    token_meter mide el costo real
            │  abre PR "feat: FEAT-xxx" + comentario de costo
            ▼
┌───────────────────────┐
│  sdd-orchestrator.yml │  ← LOS 4 GATES corren sobre el PR
│  (gates de gobernanza)│
└───────────┬───────────┘
            │  verde
            ▼
      REVISIÓN HUMANA  ──► merge a main
            │
            ▼
┌───────────────────────┐   ┌───────────────────────┐
│  notify-merge.yml     │   │  write-back en cada    │
│  Notion=Listo         │   │  gate: Bloqueado/Todo  │
│  Linear=Done          │   │  o En curso/In Review  │
└───────────────────────┘   └───────────────────────┘
```

**El flujo es automático salvo las revisiones humanas** (aprobar el spec, aprobar la implementación). Eso es por diseño: el humano decide *qué* se construye y *qué leyes cumple*; el agente hace el trabajo mecánico; los gates garantizan la disciplina.

**Workflows** (en `.github/workflows/`):
| Workflow | Se dispara con | Hace |
|---|---|---|
| `agent-specify.yml` | Notion (`notion-feature`) o manual | prompt → `spec.md` + `.feature` → PR |
| `agent-implement.yml` | Linear (`linear-task`) o manual | spec → `src/*.py` → PR + costo |
| `sdd-orchestrator.yml` | cada Pull Request | corre los 4 gates |
| `notify-merge.yml` | push a `main` | marca Notion=Listo / Linear=Done |

---

## 3. Requisitos previos

### 3.1 Herramientas locales (cada miembro las instala una vez)
- **Git** — https://git-scm.com
- **Python 3.11+** — https://python.org (marca "Add to PATH")
- **GitHub CLI (`gh`)** — https://cli.github.com → luego `gh auth login`
- **(opcional) uv/uvx** para spec-kit — `pip install uv`
- **aider** (solo si vas a correr el agente local; en CI se instala solo) — `pip install aider-chat`

### 3.2 Cuentas / accesos
| Servicio | ¿Para qué? | ¿Personal o compartido? |
|---|---|---|
| GitHub (org `valtx-ia-test`, repo `valtx-governance`) | el repo y la CI | acceso al repo: el admin te invita |
| OpenAI API key | el agente (aider) implementa/redacta | **compartida** (secret del repo) |
| Notion | entrada de features + estado | **compartida** (integración + token) |
| Linear | tareas de ingeniería + estado | **compartida** (API key) |
| Pipedream | relays entrantes (Notion/Linear → CI) | **compartida** (una cuenta del equipo) |
| Google Cloud (Vertex AI Search) | retrieval del KB | **compartida** (service account) |

> **Importante — llaves:** las API keys son como contraseñas. **Nunca** las pegues en un chat, PR, issue o Slack. Van solo en **secrets de GitHub** o **env vars de Pipedream**. Si una se expone, se **rota de inmediato** (regenerar y reemplazar). Ya nos pasó una vez; el proveedor puede deshabilitar la cuenta si detecta una key filtrada.

Todos los secrets ya están cargados en el repo (§11). Como miembro del equipo **no necesitas** las keys para el flujo normal: la CI las usa por ti. Solo las necesitas si vas a correr el agente **en tu máquina**.

---

## 4. Estructura del repositorio

```
valtx-sdd/
├─ .specify/
│  ├─ memory/
│  │  ├─ constitution.md          # principios (PRIN-*) legibles por máquina
│  │  └─ policies/                # 9 Policy Cards (POL-PE-*) de la Ley 29733
│  │     ├─ POL-PE-CONSENT-001.yaml ... POL-PE-BRECHA-009.yaml
│  │     └─ build_policies_peru.py  # genera las cards desde la ley
│  ├─ templates/                  # spec-template.md, plan-template.md, ...
│  └─ scripts/                    # helpers de spec-kit
├─ ci/                            # los scripts de gates y agente (el corazón)
│  ├─ run_gates.py                # corre los 4 gates LOCAL (== CI)
│  ├─ policy_freshness.py         # GATE 1: vigencia normativa
│  ├─ check_policy_citations.py   # GATE 2: consistencia normativa
│  ├─ check_traceability.py       # GATE 3: trazabilidad / alucinaciones
│  ├─ coverage_graph.py           # GATE 4: cobertura EARS↔Gherkin
│  ├─ policy_router.py            # Capa 0: clasifica un prompt → policies
│  ├─ context_bundler.py          # Capa 0: contexto selectivo (ahorro tokens)
│  ├─ gather_context.py           # retrieval del KB (Vertex AI Search)
│  ├─ update_kb.py                # indexa el KB en Vertex
│  ├─ update_notion.py            # write-back a Notion
│  ├─ sync_linear.py              # write-back a Linear
│  └─ token_meter.py              # mide tokens/costo real del agente
├─ specs/                         # un folder por feature
│  └─ FEAT-044-data-export/
│     ├─ spec.md                  # front-matter + REQ (EARS) + normas
│     ├─ data-export.feature      # Gherkin: un @REQ por escenario
│     └─ src/ (o /src global)     # implementación citando # REQ-...
├─ src/                           # código implementado (citando REQ)
├─ cost/
│  └─ cost_model.py               # techo mensual por escala → xlsx
├─ metrics/
│  └─ token_usage.jsonl           # consumo real acumulado (lo llena la CI)
├─ .github/workflows/             # los 4 workflows
├─ requirements.txt
├─ SETUP.md                       # config de infraestructura (referencia admin)
└─ GUIA_EQUIPO.md                 # ESTE documento
```

---

## 5. Puesta en marcha local

```bash
# 1. Clonar
gh repo clone valtx-ia-test/valtx-governance
cd valtx-governance          # (o la carpeta valtx-sdd según cómo esté)

# 2. Dependencias
pip install -r requirements.txt

# 3. Correr los 4 gates sobre un feature existente (no necesita ninguna key)
python ci/run_gates.py FEAT-044-data-export
```

Deberías ver los 4 gates en **PASS ✓** y `TODOS LOS GATES EN VERDE`. Con eso confirmas que tu entorno está listo. **Corre siempre esto antes de subir cualquier cambio a un feature** — es el mismo chequeo que hará la CI, así evitas PRs en rojo.

> En Windows, si ves errores de acentos (`cp1252`), los scripts ya fuerzan UTF-8; si aún falla, exporta `PYTHONUTF8=1` y `PYTHONIOENCODING=utf-8`.

---

## 6. El ciclo de un feature — paso a paso

Hay **tres formas de entrar** al flujo. Empieza por la manual (CLI) para entenderlo; las automáticas (§7) hacen lo mismo por debajo.

### PASO 1 — Generar el spec desde un prompt

El agente convierte tu idea en `spec.md` + `.feature`, citando **solo** las leyes que la Capa 0 determine aplicables.

**Opción A — Manual (CLI):**
```bash
gh workflow run agent-specify.yml --repo valtx-ia-test/valtx-governance \
  -f feature=FEAT-050 \
  -f prompt="App que envía notificaciones push cuando el usuario está cerca de una tienda, usando su ubicación GPS." \
  -f title="Notificaciones por proximidad" \
  -f model=gpt-4o-mini
```

**Opción B — Desde Notion:** crea una fila en la DB *Features* con `Feature ID = FEAT-050`, `Nombre`, y el `Prompt`. Pipedream la detecta (polling cada 15 min) y dispara lo mismo (§7).

Qué pasa por debajo:
1. **Router Capa 0** (`policy_router.py`) escanea el prompt → detecta triggers (`ubicacion`, `gps`) → selecciona `POL-PE-UBIC-003`. Determinista, **0 tokens LLM**.
2. **aider** redacta `specs/FEAT-050-<slug>/spec.md` (con REQ en EARS citando la policy, `estado: draft`) + su `.feature` (un `@REQ` por escenario).
3. Abre un PR **`spec: FEAT-050 (borrador · agente)`** para tu revisión.

Ver el run y lo generado:
```bash
gh run list --repo valtx-ia-test/valtx-governance --limit 3
gh pr list --repo valtx-ia-test/valtx-governance --limit 3
git fetch origin
git show origin/spec/FEAT-050-<RUNID>:specs/FEAT-050-<slug>/spec.md
```

### PASO 2 — Revisar y aprobar el spec

**Este es un punto de control humano.** Revisa el PR del spec:
- ¿Los REQ (EARS) capturan bien lo que quieres?
- ¿Cita las policies correctas? (si es un feature sin datos personales, `policies: []` y sin citas legales — eso es correcto, no un error).
- ¿El `.feature` cubre cada REQ?

Corrige lo que haga falta (editando el PR) y **mergéalo**. Al mergear, `notify-merge.yml` marca el estado en Notion/Linear.

### PASO 3 — Implementar el código

Con el spec ya en `main`, el agente lo implementa.

**Opción A — Manual (CLI):**
```bash
gh workflow run agent-implement.yml --repo valtx-ia-test/valtx-governance \
  -f feature=FEAT-050 -f model=gpt-4o-mini
```
> Puedes pasar solo `FEAT-050`: el workflow resuelve la carpeta real (`FEAT-050-<slug>`).

**Opción B — Desde Linear:** ponle a un issue (cuyo título empiece con `FEAT-050`) el label **`implement`**. Pipedream lo detecta y dispara (§7).

Qué pasa por debajo:
1. **Retrieval** (`gather_context.py`): trae del KB (Vertex AI Search) contexto relevante.
2. **aider** escribe `src/…py`, citando `# REQ-XXX-###` en cada bloque no trivial.
3. **`token_meter`** mide el **costo real** del run.
4. Abre un PR **`feat: FEAT-050`** con un **comentario de costo** (💸 tokens y USD).

### PASO 4 — Los gates (automático)

El PR de implementación dispara `sdd-orchestrator.yml` → **los 4 gates** (§8). Revisa:
```bash
gh pr checks feature/FEAT-050-<RUNID> --repo valtx-ia-test/valtx-governance
```
- **Verde** → el código es trazable, no alucina, cumple la normativa citada, cobertura 100%.
- **Rojo** → el gate te dice exactamente qué falló (REQ inventado, policy no aprobada, cobertura incompleta…). El agente falló; el framework lo cazó. El write-back marca Notion=**Bloqueado** / Linear=**Todo** con el gate que falló.

### PASO 5 — Revisar y mergear

**Segundo punto de control humano.** Aunque los gates estén verdes, revisa la calidad del código (los gates validan trazabilidad y normativa, **no** estilo ni arquitectura). Aprueba y mergea:
```bash
gh pr merge feature/FEAT-050-<RUNID> --repo valtx-ia-test/valtx-governance --squash --delete-branch
```

### PASO 6 — Feedback automático

Al mergear, `notify-merge.yml` marca:
- **Notion**: Estado = *Listo* + columna *Cumplimiento* (qué policies cumplió + link).
- **Linear**: issue = *Done* + comentario de cumplimiento.

Fin del ciclo. Desde una idea hasta código en `main`, con la ley citada y el costo medido.

---

## 7. Las entradas automáticas

Estas hacen que **crear una tarjeta dispare la CI sin usar la terminal**. Ya están montadas en **Pipedream** (una cuenta del equipo). Como usuario solo necesitas:

### Entrada por Notion (→ genera spec)
1. En la DB **Features** de Notion, crea una fila: `Feature ID`, `Nombre`, `Prompt`.
2. Pipedream (workflow *"New Page in Data Source"*) la detecta — **polling cada 15 min** — y hace un `repository_dispatch` tipo `notion-feature`.
3. Se dispara `agent-specify.yml`. El estado vuelve a la misma fila.

### Entrada por Linear (→ implementa)
1. A un issue cuyo título empiece con `FEAT-###` (que **ya tenga spec**), ponle el label **`implement`**.
2. Pipedream (workflow *Schedule + code step*, polling cada 15 min) consulta Linear, deduplica (Data Store) y dispara `linear-task`.
3. Se dispara `agent-implement.yml`. El estado vuelve al issue.

> **Por qué polling y no webhook en Linear:** el trigger nativo de Linear en Pipedream requiere scope `admin` que su OAuth no pide. Se resolvió con un polling que usa la API key (full access). Detalle en §11.7.
>
> **Sin bucles:** el label `implement` lo pone un humano; el write-back **no** lo pone → nunca se auto-dispara.

Cómo verificar que un relay funcionó:
```bash
gh run list --repo valtx-ia-test/valtx-governance --limit 3
# busca un run con EVENT = repository_dispatch
```

---

## 8. Los 4 gates en detalle

Corren en `sdd-orchestrator.yml` sobre cada PR, y local con `python ci/run_gates.py <FEAT>`. **Todos deben pasar para mergear.**

### GATE 1 · Vigencia normativa — `policy_freshness.py`
Verifica que cada Policy Card siga vigente (`vigencia_hasta` vs. hoy) y que su hash no cambió sin revisión. **0 tokens LLM.** Si una card `MUST` venció → bloquea (hay que revisar la ley con legal).

### GATE 2 · Consistencia normativa — `check_policy_citations.py`
Caza **alucinaciones de policy** en el spec:
- **Bloquea** si el spec cita un `POL-xxx` que no existe como Policy Card real.
- **Bloquea** si el cuerpo cita una policy que **no está** en el `policies:` del front-matter (lo que el router aprobó). → Esto es lo que atrapó al agente que inventó "cumple POL-PE-CONSENT-001" en un feature de mockups.
- **Advierte** si declaras una policy que ningún REQ usa.

### GATE 3 · Trazabilidad / alucinaciones — `check_traceability.py`
Detección de alucinaciones por diferencia de conjuntos sobre las citas `REQ-XXX-###`:
- **ORPHAN** (bloquea siempre): REQ citado en el código que **no existe** en ningún spec → alucinación.
- **SIN IMPLEMENTAR**: REQ del spec que el código nunca cita.
  - Si el feature ya tiene algo de código (implementación parcial) → **bloquea**.
  - Si no tiene nada de código y está en `draft` (spec-first) → **solo advierte**.
- **UNCITED** (advierte): línea de código no trivial sin un REQ cercano.

### GATE 4 · Cobertura EARS↔Gherkin — `coverage_graph.py`
Grafo bipartito REQ ↔ escenario (networkx). Exige **100%**: cada REQ del spec debe tener al menos un `@REQ-...` en el `.feature`. Bloquea si falta cobertura.

**Regla de oro para pasar los 4:** corre `python ci/run_gates.py <FEAT>` antes de subir. Si está verde local, estará verde en CI.

---

## 9. La Capa 0 · Gobierno Normativo

Es la capa previa que evalúa la normativa **antes** de construir. Piezas:

- **Policy Cards** (`.specify/memory/policies/*.yaml`): cada una destila un requisito legal (id, `enforcement` MUST/SHOULD/MAY, `triggers`, `requisito`, `fuente` con artículo, `patron_ears`, `vigencia_hasta`, `owner`). Hoy pobladas con la **Ley 29733 del Perú** + reglamento DS 016-2024-JUS. Cuando existan los procedimientos internos de Valtx, se agregan como cards nuevas.
- **Router** (`policy_router.py`): dado un prompt, escanea `triggers` y decide qué cards aplican. Determinista, **0 tokens LLM**. Su límite: matchea lo literal; la revisión humana cierra brechas semánticas, y puedes **enriquecer los `triggers`** de cada card con el tiempo.
- **Contexto selectivo** (`context_bundler.py`): en vez de meter toda la ley al prompt del agente, mete solo las 3–5 cards relevantes. Es la palanca #1 de costo y de calidad.

Probar el router con cualquier idea:
```bash
python ci/policy_router.py --prompt "app que guarda el DNI y la huella del usuario"
python ci/policy_router.py --prompt "..." --format tags     # tags para el front-matter
python ci/policy_router.py --prompt "..." --format json      # estructurado
```

---

## 10. Tokens y costo

Dos números que conviene no confundir:

### Techo estimado — `cost/cost_model.py`
Modela el **costo mensual de máxima complejidad** por escala (para la conversación de recursos con la GG). Genera `Valtx_SDD_Modelo_Costo.xlsx`.
```bash
python cost/cost_model.py
```
Órdenes de magnitud del techo (features/mes → USD/mes, con modelos caros): 20→~$1,094 · 50→~$1,997 · 150→~$5,082 · 500→~$15,934 · 1500→~$46,947. La fase de **código** es ~93% del costo por feature.

### Piso medido — `ci/token_meter.py`
Mide el **costo real** de cada run del agente (aider reporta tokens y USD exactos vía LiteLLM). En cada PR del agente verás:
- Un **comentario** `💸 Costo del agente · FEAT-xxx/stage · modelo · in/out tok · $USD`.
- Un **job summary** con la tabla de costo.
- Una línea en `metrics/token_usage.jsonl` (viaja en el PR → se **acumula** en el repo).

Consolidar el consumo real acumulado:
```bash
git pull
python ci/token_meter.py --report
```
Salida: costo por stage, por feature, total y **promedio por feature**. Ese es el dato duro para calibrar el modelo y sustentar recursos: *"el techo es X; el piso real medido es $0.00Z por feature con gpt-4o-mini; aquí está cada run."*

En el JSONL, `cost_source` distingue `aider` (medido) de `estimado` (calculado por tabla de precios cuando el proveedor no reporta costo).

Precios por modelo (USD/1M tokens, in/out) en `token_meter.py`: gpt-4o-mini 0.15/0.60 · gpt-4o 2.50/10 · claude-3-5-sonnet 3/15 · haiku 0.80/4 · opus 15/75.

---

## 11. Configuración inicial del repo

> Esto **ya está hecho**. Documentado para reproducir el sistema en otro repo/producto, o para entender de dónde salen los accesos. Solo lo hace el **admin del repo**.

### 11.1 Repo y rama
```bash
gh repo create valtx-ia-test/valtx-governance --private
# default branch = main; borrar master si quedó
```
Branch protection en `main`: requerir el check **`gates`** (Settings → Branches → Add rule). Cuando haya equipo, activar además **code-owner review**.

### 11.2 Secrets del repo (Settings → Secrets → Actions)
Cárgalos con el método de archivo para no exponerlos en consola:
```bash
notepad key.txt           # pega el valor, guarda
gh secret set NOMBRE --repo valtx-ia-test/valtx-governance < key.txt
Remove-Item key.txt
```
Secrets necesarios:
| Secret | Qué es | Para |
|---|---|---|
| `OPENAI_API_KEY` | key de OpenAI | agente (aider) |
| `ANTHROPIC_API_KEY` | key de Anthropic (opcional) | agente con Claude |
| `NOTION_TOKEN` | token de integración interna (`ntn_...`) | write-back Notion |
| `LINEAR_API_KEY` | personal API key (`lin_api_...`, full access) | write-back Linear |
| `GCP_SA_KEY` | JSON de service account | Vertex AI Search |
| `DISPATCH_PAT` | PAT fine-grained con **Contents R/W + Pull requests R/W** | el agente abre PRs |

> **Ojo con `DISPATCH_PAT`:** debe tener permiso **Pull requests: Read and write** (no solo Contents). Sin eso, el agente sube la rama pero falla al crear el PR (`Resource not accessible by personal access token`). Se usa este PAT y **no** el `GITHUB_TOKEN` del bot porque la org bloquea que Actions cree PRs.

### 11.3 Notion
1. Crea una **integración interna** (notion.so → My integrations o Connections) → copia el token `ntn_...`.
2. Crea la DB **Features** con columnas: `Nombre` (title), `Feature ID` (text), `Prompt` (text), `Estado` (status con opciones *Sin empezar / En curso / Listo / Bloqueado*), `Cumplimiento` (text).
3. Comparte la DB con la integración (Connections → tu integración).

### 11.4 Linear
1. Settings → Security & access → **Personal API keys** → New (full access) → `lin_api_...`.
2. Crea la etiqueta **`implement`** (Issues → Labels).
3. Estados del team ya vienen (Todo / In Progress / In Review / Done…).

### 11.5 Vertex AI Search (GCP)
1. Proyecto GCP con billing. **Tope de gasto**: crea un *budget* (ej. $20) en Billing → Budgets & alerts.
2. Data store de Vertex AI Search (Discovery Engine): `valtx-sdd-kb`, location `global`.
3. Service account con rol `roles/aiplatform.user` (y acceso al data store) → descarga el JSON → cárgalo como secret `GCP_SA_KEY`.
4. Prueba: `python ci/gather_context.py --feature FEAT-044-data-export --top 5`.

### 11.6 Pipedream — relay de Notion (entrada → spec)
1. New Workflow → Trigger **Notion → "New Page in Data Source"** → conecta Notion → Data Source = **Features**.
2. Env var (Settings → Environment Variables): `GITHUB_DISPATCH_PAT` = tu PAT.
3. Step **HTTP → Send any HTTP Request**:
   - `POST https://api.github.com/repos/valtx-ia-test/valtx-governance/dispatches`
   - Headers: `Authorization: Bearer {{process.env.GITHUB_DISPATCH_PAT}}`, `Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28`, `User-Agent: pipedream-valtx`
   - Body:
     ```json
     {"event_type":"notion-feature","client_payload":{
       "feature":"{{steps.trigger.event.properties["Feature ID"].rich_text[0].plain_text}}",
       "prompt":"{{steps.trigger.event.properties["Prompt"].rich_text[0].plain_text}}"}}
     ```
4. Deploy. (El `User-Agent` es obligatorio o GitHub da 403.)

### 11.7 Pipedream — relay de Linear (label → implementación)
El trigger nativo de Linear necesita scope `admin` (webhooks) que la OAuth de Pipedream no otorga. Se usa **polling**:
1. New Workflow → Trigger **Schedule** (cada 15 min).
2. Env var: `LINEAR_API_KEY` (`lin_api_...`).
3. Step **Run Node.js code** que: consulta GraphQL por issues con label `implement`, deduplica con un **Data Store**, y hace `POST` al `dispatches` con `event_type: linear-task` y `feature = issue.title`. (El código completo está en `SETUP.md` / historial; el label real es `implement`, sub-etiqueta del grupo `sdd`.)
4. Deploy.

### 11.8 Habilitar que el agente abra PRs
La org bloquea que Actions cree PRs y la casilla suele estar gris. **Solución usada:** el workflow crea el PR con `secrets.DISPATCH_PAT` (identidad de usuario), no con el `GITHUB_TOKEN`. Con eso no dependes de la casilla de la org. (Alternativa: org → Settings → Actions → *Allow GitHub Actions to create and approve pull requests*, si tienes permiso de owner.)

---

## 12. Troubleshooting

Errores reales que ya encontramos y cómo se resuelven:

| Síntoma | Causa | Fix |
|---|---|---|
| `UnicodeEncodeError` / acentos rotos en consola (Windows) | consola cp1252 | los scripts fuerzan UTF-8; si persiste: `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`. En Notion/Linear los datos quedan bien; solo se ve feo en PowerShell. |
| `gh secret set … HTTP 404` | el repo no existía o nombre mal | crea el repo primero; usa `owner/repo` correcto. |
| `GitHub Actions is not permitted to create or approve pull requests` | restricción de la org al `GITHUB_TOKEN` | el workflow abre el PR con `DISPATCH_PAT` (ya configurado). |
| `Resource not accessible by personal access token (createPullRequest)` | el PAT no tiene permiso de PRs | edita el PAT fine-grained → **Pull requests: Read and write**. |
| `pull request create failed: … not permitted` desde el bot | usaste `GITHUB_TOKEN` | usa `GH_TOKEN: ${{ secrets.DISPATCH_PAT }}` en el step. |
| Linear: `Invalid role: admin required … webhooks` | OAuth de Pipedream sin scope admin | usa el relay por **polling** (§11.7), no el trigger nativo. |
| Pipedream Notion: `feature` sale vacío / `[object Object]` | mapeo del campo mal | usa la ruta `properties["Feature ID"].rich_text[0].plain_text`; revisa el preview. |
| Pipedream: HTTP 401 a GitHub | PAT vacío o env var sin resolver | valida el token con `curl -H "Authorization: Bearer $PAT" https://api.github.com/user`; revisa el nombre exacto de la env var. |
| Pipedream: HTTP 403 a GitHub | falta header `User-Agent` | agrégalo. |
| Router: "Nada nuevo con label" pero etiquetaste | el label real es `implement` (sub-label del grupo `sdd`), no `sdd:implement` | usa el nombre real de la sub-etiqueta. |
| Gate 3 bloquea un spec sin código | el feature no está en `draft` o ya tiene código parcial | pon `estado: draft` mientras no haya código; al implementar, cita **todos** los REQ. |
| Gate 2 bloquea "CITA NO APROBADA" | el spec cita una policy que el router no aprobó | quita la cita, o agrega la policy al `policies:` del front-matter **solo si de verdad aplica**. |
| El agente falla al instante con error del proveedor | la cuenta de OpenAI/Anthropic sin saldo o deshabilitada | recarga saldo / revisa el estado de la org del proveedor. |
| Vertex `400 Bad Request` en search | body con `extractiveContentSpec` (requiere edición Enterprise) | ya removido; usa solo `snippetSpec`. |
| `git push` rechazado (`fetch first`) | mergeaste un PR en GitHub, tu local está atrás | `git pull --rebase origin main` y reintenta. |

---

## 13. Glosario

- **SDD (Spec-Driven Development):** el código nace de una especificación trazable, no al revés.
- **EARS:** sintaxis de requisitos (`WHEN/WHERE/IF … THE SYSTEM SHALL …`). Cada uno con id `REQ-<AREA>-###`.
- **Gherkin / `.feature`:** escenarios de comportamiento (`Dado/Cuando/Entonces`), cada uno etiquetado `@REQ-...`.
- **Capa 0 · Gobierno Normativo:** capa previa que decide qué leyes aplican y las inyecta al spec.
- **Policy Card:** una ley/procedimiento destilado a YAML accionable (`POL-PE-...`).
- **Gate:** chequeo automático que bloquea el merge si no se cumple. Hay 4.
- **Router (Capa 0):** clasificador determinista prompt → policies. 0 tokens LLM.
- **Constitución:** principios de arquitectura/seguridad (`PRIN-*`) que el sistema respeta.
- **Agente agnóstico:** `aider` implementa/redacta; el modelo se cambia con un flag.
- **KB / retrieval:** base de conocimiento en Vertex AI Search que alimenta al agente antes de codear.
- **Techo vs. piso:** costo máximo estimado (`cost_model.py`) vs. costo real medido (`token_meter.py`).
- **Write-back:** el estado del feature vuelve a Notion (Producto/Legal) y Linear (Ingeniería).

---

*Última actualización: 2026-07. Mantén esta guía viva: si el flujo cambia, actualízala en el mismo PR.*
