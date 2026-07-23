# Configuración completa — de local a operativo

Guía paso a paso para conectar el harness a **GitHub Actions + spec-kit + Notion +
Linear + Vertex**. Cada fase es independiente y verificable. Marca `⟶ TÚ` donde
insertas una credencial o haces una acción en un panel web.

> Orden recomendado: A → B → C → D primero (dejan el motor corriendo en PRs).
> Luego E/F (disparadores externos) y G (agentes de código). H/I al final.

---

## Fase A · Prerrequisitos (local, 10 min)

```bash
# 1. GitHub CLI (no está instalado aún)
winget install --id GitHub.cli -e
gh --version

# 2. Autenticar  ⟶ TÚ (abre el navegador)
gh auth login          # GitHub.com > HTTPS > browser

# 3. Verifica el resto (ya presentes)
git --version && python --version && uvx --version && node --version
```

---

## Fase B · Repos en GitHub (multi-repo, 15 min)

Arquitectura: `valtx-governance` (constitución + policies + gates reutilizables) y
un repo por producto `valtx-<producto>`.

```bash
cd "c:/Users/antho/Documents/Anthony/Valtx/valtx-sdd"

# 1. Org ya creada: "valtx-ia-test" (eres owner).
#    Crea los equipos para CODEOWNERS (Fase D)  ⟶ TÚ (web):
#    Org → Teams → New team → "legal"  y  "arquitectura"

# 2. Governance repo = este scaffold
git branch -M main
gh repo create valtx-ia-test/valtx-governance --private --source . --remote origin --push

# 3. Cargar secrets (usa TUS keys)  ⟶ TÚ
gh secret set ANTHROPIC_API_KEY   --repo valtx-ia-test/valtx-governance   # sk-ant-...
gh secret set OPENAI_API_KEY      --repo valtx-ia-test/valtx-governance   # sk-...
gh secret set LINEAR_API_KEY      --repo valtx-ia-test/valtx-governance
gh secret set NOTION_TOKEN        --repo valtx-ia-test/valtx-governance
gh secret set GCP_SA_KEY          --repo valtx-ia-test/valtx-governance < gcp-sa.json  # Vertex
# PAT para que Notion/Linear puedan disparar la CI (repository_dispatch):
gh secret set DISPATCH_PAT        --repo valtx-ia-test/valtx-governance
```

> **Para escala (recomendado):** como eres owner de la org, carga los secrets UNA vez
> a nivel de organización y todos los repos `valtx-ia-test/*` los heredan:
> ```bash
> gh secret set ANTHROPIC_API_KEY --org valtx-ia-test --visibility all
> gh secret set OPENAI_API_KEY    --org valtx-ia-test --visibility all
> gh secret set LINEAR_API_KEY    --org valtx-ia-test --visibility all
> gh secret set NOTION_TOKEN      --org valtx-ia-test --visibility all
> gh secret set DISPATCH_PAT      --org valtx-ia-test --visibility all
> ```
> Así, al crear `valtx-ia-test/valtx-<producto>` no repites nada.

---

## Fase C · spec-kit (10 min)  ← inicio del BRAZO de autoría+implementación

> spec-kit y el agente (Fase G) son **un solo continuo**, no fases sueltas:
> spec-kit **genera** los artefactos (spec → plan → tasks → gherkin) y el agente
> **los implementa**. Vertex (Fase G-bis) le da al agente el *retrieval* de contexto
> y luego indexa los EARS. Orden del brazo: **C → G-bis (Vertex) → G**.

```bash
# Instala spec-kit en el repo (crea .specify/, comandos /speckit.*)
uvx --from git+https://github.com/github/spec-kit specify init --here

# Nuestra constitution.md y policies/ ya viven en .specify/memory/ — spec-kit los respeta.
# Prueba un feature nuevo:
uvx specify run /speckit.specify "check-in por geolocalización"   # genera spec.md
```

---

## Fase D · Branch protection + CODEOWNERS (10 min)  ← el gobierno real

```bash
# 1. CODEOWNERS: el abogado revisa TODA la normativa
cat > .github/CODEOWNERS <<'EOF'
# Gobierno normativo — requiere revisión legal
/.specify/memory/policies/   @valtx-ia-test/legal
/.specify/memory/constitution.md   @valtx-ia-test/arquitectura
EOF
git add .github/CODEOWNERS && git commit -m "add CODEOWNERS" && git push

# 2. Branch protection  ⟶ TÚ (web): Settings → Branches → Add rule para `main` y `dev`
#    - Require status checks:  SDD Orchestrator / gates
#    - Require review from Code Owners
#    - Require branches up to date
```

Con esto: ningún cambio a `policies/` mergea sin el abogado, y ningún PR pasa sin
los 3 gates en verde. **El motor ya está operativo en PRs.**

---

## Fase E · Notion → captura (disparador, 20 min)

Objetivo: crear una página de feature en Notion dispara la CI.

1. **Integración** ⟶ TÚ: https://www.notion.so/my-integrations → New integration
   → copia el token (= `NOTION_TOKEN`). Comparte tu base de datos de "Features" con ella.
2. **Base de datos "Features"**: propiedades `Nombre`, `Prompt` (texto), `Estado`, `Feature ID`.
3. **Relay Notion→GitHub** (Notion no habla `repository_dispatch` nativo). Cloudflare
   Worker mínimo (o Vercel function):

```js
// worker.js — recibe webhook de Notion Automation y dispara la CI
export default {
  async fetch(req, env) {
    const p = await req.json();
    await fetch("https://api.github.com/repos/valtx-ia-test/valtx-governance/dispatches", {
      method: "POST",
      headers: { Authorization: `token ${env.DISPATCH_PAT}`,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "valtx-relay" },
      body: JSON.stringify({ event_type: "notion-feature",
        client_payload: { feature: p.feature_id, prompt: p.prompt } }),
    });
    return new Response("ok");
  }
}
```

4. **Notion Automation** ⟶ TÚ: en la DB, "When Estado = Listo → Send webhook" a la URL del Worker.

---

## Fase F · Linear → ejecución (disparador, 15 min)

```bash
# Linear webhook  ⟶ TÚ (web): Settings → API → Webhooks → New
#   URL: la del mismo relay (o un endpoint /linear)
#   Trigger: Issues (status change)
```

El relay mapea el evento a `event_type: "linear-task"` con el issue id. El workflow
`sdd-orchestrator.yml` ya escucha ambos `repository_dispatch` types.

---

## Fase G · Agentes de código en Actions (30 min)

Añade al workflow (o un workflow aparte `agent-implement.yml`) el runner del agente:

```yaml
  implement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Code (implementa las tasks del feature)
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # el prompt referencia el bundle selectivo (context_bundler) + tasks.md
      - name: Vertex AI Search (retrieval de contexto)
        env: { GOOGLE_APPLICATION_CREDENTIALS_JSON: ${{ secrets.GCP_SA_KEY }} }
        run: python ci/gather_context.py   # (pendiente: tu wrapper de retrieval)
```

Tiering de modelos (palanca de costo del modelo `cost/cost_model.py`):
- Refinamiento/routing → **Haiku**
- Spec/Plan/Tasks/Gherkin/Review → **Sonnet**
- Code dev (fase dominante) → **Opus** (techo) o **Sonnet** (piso, −79% LLM/feature)

---

## Fase G-bis · Vertex AI Search — retrieval + KB (30–45 min)

Vertex aparece **2 veces** en el flujo: (a) el agente **consulta** contexto antes de
codear ("Gather Context for Tasks"); (b) al mergear, los EARS/specs se **indexan** para
features futuros ("Update Knowledge Base").

```bash
# 1. Proyecto GCP + habilitar APIs  ⟶ TÚ
gcloud config set project valtx-sdd
gcloud services enable discoveryengine.googleapis.com aiplatform.googleapis.com

# 2. Data Store + Search App  ⟶ TÚ (consola: Vertex AI Agent Builder → Search)
#    - Tipo: Unstructured (docs) o Cloud Storage.
#    - Ingesta inicial: sube tus repos/docs a un bucket GCS y apúntalo como fuente.
gsutil mb gs://valtx-sdd-kb
gsutil -m cp -r specs .specify src gs://valtx-sdd-kb/   # semilla del KB

# 3. Service Account con acceso a Discovery Engine  ⟶ TÚ
gcloud iam service-accounts create sdd-retrieval
gcloud projects add-iam-policy-binding valtx-sdd \
  --member="serviceAccount:sdd-retrieval@valtx-sdd.iam.gserviceaccount.com" \
  --role="roles/discoveryengine.editor"
gcloud iam service-accounts keys create gcp-sa.json \
  --iam-account=sdd-retrieval@valtx-sdd.iam.gserviceaccount.com

# 4. Cárgala como secret
gh secret set GCP_SA_KEY --repo valtx-ia-test/valtx-governance --body (Get-Content gcp-sa.json -Raw)
```

Wiring en la CI (dos scripts que se conectan a los nodos del diagrama):
- `ci/gather_context.py` → *retrieval*: consulta el Data Store con las tasks y devuelve
  los pasajes relevantes al prompt del agente (nodo "Gather Context for Tasks").
- `ci/update_kb.py` → *indexado*: tras el merge, sube los EARS/specs nuevos al Data Store
  (nodo "Update Knowledge Base").

> Estos dos scripts están pendientes de crear (los armamos al llegar a esta fase, ya con
> tu Data Store real y su ID). El `DATA_STORE_ID` va como variable de repo.

---

## Fase H · Observabilidad de tokens (10 min)

El runner del agente alimenta `ci/token_meter.py` con el `usage` real que devuelve
cada API, y se agrega en `metrics/token_usage.jsonl`. Un job semanal suma costo por
feature/modelo → valida el modelo de `cost/cost_model.py` con datos reales.

---

## Fase I · Validación end-to-end (checklist)

- [ ] Crear página en Notion (Estado=Listo) → aparece run en Actions.
- [ ] El run corre GATE 1/2/3; si algo bloquea, no hay merge.
- [ ] spec-kit genera spec/plan/tasks; el agente abre PR en rama `feature/...`.
- [ ] Cambiar una `policy` sin el abogado → PR bloqueado por CODEOWNERS.
- [ ] `metrics/token_usage.jsonl` registra el costo del run.

Cuando esto pasa de punta a punta, el framework está **operativo**. Desde ahí,
mueve el tiering Opus→Sonnet para bajar del techo al piso de costo.
