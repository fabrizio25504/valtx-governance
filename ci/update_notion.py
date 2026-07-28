#!/usr/bin/env python3
"""
Write-back a Notion — cierra el lazo de feedback del flujo SDD hacia Producto/Legal.

Al terminar el ciclo (gates + merge), actualiza la fila del feature en la DB "Features":
  - Estado (status): "En curso" | "Listo" | "Bloqueado"
  - Cumplimiento (text): qué policies cumplió + veredicto de gates + link al PR

La audiencia de Notion no es ingeniería: es quien pregunta "¿esto cumple la Ley 29733?".
Por eso lo que se escribe es TRAZABILIDAD NORMATIVA, no estado de build.

Auth: NOTION_TOKEN (integración interna, formato ntn_...) en env.
DB por env NOTION_DB o el default de Valtx.

Uso:
  python ci/update_notion.py --feature FEAT-044-data-export --status listo --pr-url URL
  python ci/update_notion.py --feature FEAT-044-data-export --status bloqueado --gate trazabilidad --pr-url URL
"""
import os, re, sys, json, argparse, pathlib
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DB_ID = os.environ.get("NOTION_DB", "")
API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# Estos nombres de opción deben EXISTIR en la propiedad select "Estado" de Notion.
STATUS_MAP = {
    "en_curso": "En curso",
    "listo": "Completado",
    "bloqueado": "Bloqueado",
}


def feature_id(feature):
    """Extrae 'FEAT-044' de 'FEAT-044-data-export' o de 'feature/FEAT-044-...-<runid>'."""
    m = re.search(r"(FEAT-\d+)", feature)
    return m.group(1) if m else feature


def read_spec_meta(feature):
    """Lee policies[] y titulo del front-matter de specs/<feature>/spec.md (best-effort)."""
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


def find_page(fid):
    """Busca la página cuyo 'Feature ID' == fid. Devuelve page_id o None."""
    body = {
        "filter": {"property": "Feature ID", "rich_text": {"equals": fid}},
        "page_size": 1,
    }
    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=HEADERS, json=body, timeout=30)
    r.raise_for_status()
    res = r.json().get("results", [])
    return res[0]["id"] if res else None


def compliance_text(status_key, policies, gate, pr_url):
    verdict = {
        "listo": "gates ✅ (vigencia · trazabilidad · cobertura) · mergeado",
        "en_curso": "en implementación / revisión humana",
        "bloqueado": f"❌ bloqueado por gate: {gate or 'desconocido'}",
    }[status_key]
    pols = ", ".join(policies) if policies else "sin policies declaradas"
    parts = [f"Cumple: {pols}", verdict]
    if pr_url:
        parts.append(f"PR: {pr_url}")
    return " · ".join(parts)


def update_page(page_id, status_name, text):
    props = {
        "Estado": {"select": {"name": status_name}},
        "Notas": {"rich_text": [{"text": {"content": text[:1900]}}]},
    }
    r = requests.patch(f"{API}/pages/{page_id}", headers=HEADERS, json={"properties": props}, timeout=30)
    if r.status_code >= 400:
        print(f"[notion] error {r.status_code}: {r.text}", file=sys.stderr)
    r.raise_for_status()


def create_page(fid, nombre, status_name, text):
    """Crea la fila si el feature nació por CLI/dispatch y aún no existe en Notion."""
    props = {
        "Feature": {"title": [{"text": {"content": nombre or fid}}]},
        "Feature ID": {"rich_text": [{"text": {"content": fid}}]},
        "Estado": {"select": {"name": status_name}},
        "Notas": {"rich_text": [{"text": {"content": text[:1900]}}]},
    }
    body = {"parent": {"database_id": DB_ID}, "properties": props}
    r = requests.post(f"{API}/pages", headers=HEADERS, json=body, timeout=30)
    if r.status_code >= 400:
        print(f"[notion] error {r.status_code}: {r.text}", file=sys.stderr)
    r.raise_for_status()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", required=True)
    ap.add_argument("--status", required=True, choices=list(STATUS_MAP))
    ap.add_argument("--gate", default="")
    ap.add_argument("--pr-url", default="")
    args = ap.parse_args()

    if not NOTION_TOKEN:
        print("[notion] NOTION_TOKEN vacío — se omite write-back (no rompe la CI).")
        return 0
    if not DB_ID:
        print("[notion] NOTION_DB vacío — se omite write-back (no rompe la CI).")
        return 0

    fid = feature_id(args.feature)
    policies, titulo = read_spec_meta(args.feature)
    status_name = STATUS_MAP[args.status]
    text = compliance_text(args.status, policies, args.gate, args.pr_url)

    page_id = find_page(fid)
    if page_id:
        update_page(page_id, status_name, text)
        print(f"[notion] {fid} → Estado='{status_name}' (fila actualizada) · {text}")
    else:
        create_page(fid, titulo, status_name, text)
        print(f"[notion] {fid} → Estado='{status_name}' (fila creada) · {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
