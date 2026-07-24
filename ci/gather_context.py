#!/usr/bin/env python3
"""
Retrieval del KB (Vertex AI Search / Discovery Engine) — nodo "Gather Context for Tasks".

Consulta el data store y devuelve los pasajes relevantes para alimentar al agente
ANTES de codear. Es la mitad "retrieval" de Vertex en el flujo.

Auth: service account desde GCP_SA_KEY (JSON en env, como en CI) o Application Default
Credentials (Cloud Shell / `gcloud auth`). Config por env (con defaults de Valtx):
  SDD_GCP_PROJECT, SDD_DS_ID, SDD_DS_LOCATION.

Uso:
  python ci/gather_context.py "consentimiento de geolocalización"
  python ci/gather_context.py --feature FEAT-042-geo-checkin   # deriva la query del spec
"""
import os, sys, json, argparse
import requests
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

PROJECT = os.environ.get("SDD_GCP_PROJECT", "ocrtesting-413503")
DS_ID = os.environ.get("SDD_DS_ID", "valtx-sdd-kb")
LOCATION = os.environ.get("SDD_DS_LOCATION", "global")
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def get_credentials():
    raw = os.environ.get("GCP_SA_KEY")
    if raw:  # CI: la key viene como JSON en el secret
        info = json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:    # Cloud Shell / local con gcloud: Application Default Credentials
        creds, _ = google.auth.default(scopes=SCOPES)
    creds.refresh(google.auth.transport.requests.Request())
    return creds


def search(query, top=5):
    token = get_credentials().token
    url = (f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}"
           f"/collections/default_collection/dataStores/{DS_ID}"
           f"/servingConfigs/default_search:search")
    body = {
        "query": query,
        "pageSize": top,
        "contentSearchSpec": {"snippetSpec": {"returnSnippet": True}},
    }
    r = requests.post(url, json=body, timeout=30, headers={
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": PROJECT,
        "Content-Type": "application/json",
    })
    if not r.ok:  # surface el mensaje real de Discovery Engine
        print(f"HTTP {r.status_code} en {url}\n{r.text}", file=sys.stderr)
        r.raise_for_status()
    return r.json()


def derive_query(feature):
    p = os.path.join("specs", feature, "spec.md")
    if os.path.exists(p):
        return " ".join(open(p, encoding="utf-8").read().split()[:60])
    return feature


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?")
    ap.add_argument("--feature")
    ap.add_argument("--top", type=int, default=5)
    a = ap.parse_args()
    q = a.query or (derive_query(a.feature) if a.feature else None)
    if not q:
        print("uso: gather_context.py <query> | --feature <FEAT>"); sys.exit(2)

    res = search(q, a.top)
    results = res.get("results", [])
    print(f"# Contexto recuperado del KB (query: {q[:60]}…) — {len(results)} resultado(s)\n")
    for i, item in enumerate(results, 1):
        d = item.get("document", {}).get("derivedStructData", {})
        link = d.get("link") or item.get("document", {}).get("name", "?")
        snips = d.get("snippets", [])
        snippet = snips[0].get("snippet", "").strip() if snips else ""
        print(f"[{i}] {link}\n    {snippet}\n")
    if not results:
        print("(sin resultados — ¿terminó la indexación? puede tardar unos minutos tras el import)")


if __name__ == "__main__":
    main()
