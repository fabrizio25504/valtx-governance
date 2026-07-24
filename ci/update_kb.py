#!/usr/bin/env python3
"""
Indexado del KB (Vertex AI Search) — nodo "Update Knowledge Base".

Tras el merge, sube los specs/EARS nuevos al bucket y dispara la reimportación
INCREMENTAL al data store, para que features futuros los recuperen (retrieval).

Auth: GCP_SA_KEY (JSON) o ADC. Config por env (defaults de Valtx):
  SDD_GCP_PROJECT, SDD_DS_ID, SDD_DS_LOCATION, SDD_KB_BUCKET.

Uso: python ci/update_kb.py specs/FEAT-042-geo-checkin
"""
import os, sys, json
import requests
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
from google.cloud import storage

PROJECT = os.environ.get("SDD_GCP_PROJECT", "ocrtesting-413503")
DS_ID = os.environ.get("SDD_DS_ID", "valtx-sdd-kb")
LOCATION = os.environ.get("SDD_DS_LOCATION", "global")
BUCKET = os.environ.get("SDD_KB_BUCKET", "valtx-sdd-kb")
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def get_credentials():
    raw = os.environ.get("GCP_SA_KEY")
    if raw:
        creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    else:
        creds, _ = google.auth.default(scopes=SCOPES)
    creds.refresh(google.auth.transport.requests.Request())
    return creds


def upload(path, creds):
    client = storage.Client(project=PROJECT, credentials=creds)
    bkt = client.bucket(BUCKET)
    n = 0
    for root, _, files in os.walk(path):
        for f in files:
            local = os.path.join(root, f)
            blob = bkt.blob(local.replace("\\", "/"))
            blob.upload_from_filename(local)
            n += 1
    return n


def reimport(token):
    url = (f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}"
           f"/collections/default_collection/dataStores/{DS_ID}/branches/0/documents:import")
    body = {"gcsSource": {"inputUris": [f"gs://{BUCKET}/**"], "dataSchema": "content"},
            "reconciliationMode": "INCREMENTAL"}
    r = requests.post(url, json=body, timeout=30, headers={
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": PROJECT,
        "Content-Type": "application/json",
    })
    r.raise_for_status()
    return r.json()


def main():
    if len(sys.argv) < 2:
        print("uso: update_kb.py <ruta a indexar>"); sys.exit(2)
    path = sys.argv[1]
    creds = get_credentials()
    n = upload(path, creds)
    op = reimport(creds.token)
    print(f"[update_kb] {n} archivo(s) de '{path}' subidos; reimport INCREMENTAL: {op.get('name','?')}")


if __name__ == "__main__":
    main()
