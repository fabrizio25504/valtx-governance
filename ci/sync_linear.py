#!/usr/bin/env python3
"""
Write-back a Linear — feedback del flujo SDD hacia Ingeniería (GraphQL API).

Espejo de ci/update_notion.py, pero para el team de ingeniería en Linear:
  - mueve el issue del feature al estado que refleja el avance
  - deja un COMENTARIO con el cumplimiento normativo (policies + veredicto + PR)

Mapa de estados (team ANT):
  en_curso  -> In Review  (started)   : PR con gates verdes, esperando revisión/merge
  listo     -> Done       (completed) : mergeado a main
  bloqueado -> Todo       (unstarted) : devuelto a dev + comentario con el gate que falló

Encuentra el issue cuyo título contiene FEAT-### (upsert: si no existe, lo crea).

Auth: LINEAR_API_KEY (personal API key, formato lin_api_...) en env.
Team/estados por env (con defaults de Valtx): LINEAR_TEAM, LINEAR_STATE_*.

Uso:
  python ci/sync_linear.py --feature FEAT-044-data-export --status listo --pr-url URL
  python ci/sync_linear.py --feature FEAT-044-data-export --status bloqueado --gate trazabilidad
"""
import os, re, sys, json, argparse, pathlib
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

LINEAR_API_KEY = os.environ.get("LINEAR_API_KEY", "")
TEAM_ID = os.environ.get("LINEAR_TEAM", "f3f833f2-085c-452d-b2bf-e5323f08a569")
API = "https://api.linear.app/graphql"
HEADERS = {"Authorization": LINEAR_API_KEY, "Content-Type": "application/json"}

# IDs de workflow states del team (override por env si cambian).
STATE_MAP = {
    "en_curso": os.environ.get("LINEAR_STATE_INREVIEW", "9b97c6b0-867f-483a-b7b2-ac7b47308e1e"),
    "listo": os.environ.get("LINEAR_STATE_DONE", "3090eca8-0acd-4a19-b506-5605f80e15d8"),
    "bloqueado": os.environ.get("LINEAR_STATE_TODO", "0ba7d576-1918-41f7-8e64-a385318a3d83"),
}


def gql(query, variables=None):
    r = requests.post(API, headers=HEADERS, json={"query": query, "variables": variables or {}}, timeout=30)
    if r.status_code >= 400:
        print(f"[linear] HTTP {r.status_code}: {r.text}", file=sys.stderr)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        print(f"[linear] GraphQL errors: {json.dumps(data['errors'])}", file=sys.stderr)
        raise SystemExit(1)
    return data["data"]


def feature_id(feature):
    """Extrae 'FEAT-044' de 'FEAT-044-data-export' o 'feature/FEAT-044-...-<runid>'."""
    m = re.search(r"(FEAT-\d+)", feature)
    return m.group(1) if m else feature


def read_spec_meta(feature):
    """policies[] y titulo del front-matter de specs/<feature>/spec.md (best-effort)."""
    root = pathlib.Path(__file__).resolve().parent.parent
    spec = root / "specs" / feature / "spec.md"
    policies, titulo = [], ""
    if not spec.exists():
        return policies, titulo
    txt = spec.read_text(encoding="utf-8")
    fm = txt.split("---", 2)
    body = fm[1] if len(fm) >= 3 else txt
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("policies:"):
            policies = re.findall(r"POL-[A-Z0-9-]+", s)
        elif s.startswith("titulo:"):
            titulo = s.split(":", 1)[1].strip()
    return policies, titulo


def find_issue(fid):
    """Issue del team cuyo título contiene el FEAT-###. Devuelve id o None."""
    q = """
    query($team: ID!, $q: String!) {
      issues(filter: { team: { id: { eq: $team } }, title: { contains: $q } }, first: 1) {
        nodes { id identifier title }
      }
    }"""
    nodes = gql(q, {"team": TEAM_ID, "q": fid})["issues"]["nodes"]
    return nodes[0]["id"] if nodes else None


def create_issue(fid, titulo, state_id):
    q = """
    mutation($input: IssueCreateInput!) {
      issueCreate(input: $input) { success issue { id identifier } }
    }"""
    title = f"{fid} · {titulo}" if titulo else fid
    inp = {"teamId": TEAM_ID, "title": title, "stateId": state_id}
    res = gql(q, {"input": inp})["issueCreate"]
    return res["issue"]["id"]


def set_state(issue_id, state_id):
    q = """
    mutation($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) { success }
    }"""
    gql(q, {"id": issue_id, "input": {"stateId": state_id}})


def add_comment(issue_id, body):
    q = """
    mutation($input: CommentCreateInput!) {
      commentCreate(input: $input) { success }
    }"""
    gql(q, {"input": {"issueId": issue_id, "body": body}})


def compliance_text(status_key, policies, gate, pr_url):
    verdict = {
        "listo": "✅ gates verdes (vigencia · trazabilidad · cobertura) — mergeado a main",
        "en_curso": "🟡 gates verdes — en revisión humana / pendiente de merge",
        "bloqueado": f"❌ bloqueado por gate: **{gate or 'desconocido'}** — devuelto a Todo",
    }[status_key]
    pols = ", ".join(policies) if policies else "sin policies declaradas"
    parts = [f"**SDD**: {verdict}", f"Cumple: {pols}"]
    if pr_url:
        parts.append(f"[PR / commit]({pr_url})")
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", required=True)
    ap.add_argument("--status", required=True, choices=list(STATE_MAP))
    ap.add_argument("--gate", default="")
    ap.add_argument("--pr-url", default="")
    args = ap.parse_args()

    if not LINEAR_API_KEY:
        print("[linear] LINEAR_API_KEY vacío — se omite write-back (no rompe la CI).")
        return 0

    fid = feature_id(args.feature)
    policies, titulo = read_spec_meta(args.feature)
    state_id = STATE_MAP[args.status]
    text = compliance_text(args.status, policies, args.gate, args.pr_url)

    issue_id = find_issue(fid)
    if issue_id:
        set_state(issue_id, state_id)
        action = "issue actualizado"
    else:
        issue_id = create_issue(fid, titulo, state_id)
        action = "issue creado"
    add_comment(issue_id, text)
    print(f"[linear] {fid} → '{args.status}' ({action}) + comentario de cumplimiento.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
