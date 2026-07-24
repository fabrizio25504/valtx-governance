#!/usr/bin/env python3
"""
Router de aplicabilidad normativa (Capa 0) — clasifica un PROMPT en texto libre.

Es el nodo "Clasifica datos → Router de aplicabilidad" del flujo: dado el prompt de
un feature (antes de que exista spec), escanea los `triggers` de cada Policy Card y
determina qué normas aplican. 100% determinista, 0 tokens LLM. Su salida alimenta al
agente que redacta el spec, para que cite SOLO las policies pertinentes (3–5), no todo
el corpus (palanca de costo y de calidad).

Uso:
  python ci/policy_router.py --prompt "app que levanta la ubicación del usuario"
  python ci/policy_router.py --prompt "..." --format tags   # tags para el front-matter
  python ci/policy_router.py --prompt "..." --format json    # estructurado
"""
import sys, os, glob, re, json, argparse, unicodedata
import yaml

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.join(os.path.dirname(__file__), "..")
POLICIES_DIR = os.path.join(ROOT, ".specify", "memory", "policies")


def norm(s):
    """minúsculas, sin acentos, separadores no alfanuméricos -> espacio."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def load_cards():
    cards = []
    for p in sorted(glob.glob(os.path.join(POLICIES_DIR, "*.yaml"))):
        c = yaml.safe_load(open(p, encoding="utf-8"))
        cards.append(c)
    return cards


def route(prompt):
    text = " " + norm(prompt) + " "
    matched = []
    for c in load_cards():
        hits = []
        for t in c.get("triggers", []):
            tn = norm(t)
            if not tn:
                continue
            # coincidencia por palabra/frase completa (evita falsos positivos por substring)
            if re.search(r"(?<![a-z0-9])" + re.escape(tn) + r"(?![a-z0-9])", text):
                hits.append(t)
        if hits:
            matched.append((c, sorted(set(hits))))
    # MUST primero, luego por # de triggers que dispararon
    order = {"MUST": 0, "SHOULD": 1, "MAY": 2}
    matched.sort(key=lambda m: (order.get(m[0].get("enforcement"), 9), -len(m[1])))
    return matched


def as_tags(matched):
    tags = []
    for _, hits in matched:
        tags += hits
    # dedup preservando orden
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t); out.append(t)
    return out


def as_md(prompt, matched):
    if not matched:
        return ("# CAPA 0 · Router de aplicabilidad\n\n"
                "Ninguna Policy Card disparó por triggers para este prompt. "
                "AÚN ASÍ, revisa manualmente: la ausencia de match no garantiza que no aplique norma.")
    lines = ["# CAPA 0 · Normas aplicables a este feature (router determinista)\n",
             "Cita SOLO estas Policy Cards en el spec (cada REQ debe referenciar la suya):\n"]
    for c, hits in matched:
        lines.append(f"## {c['id']} · {c.get('titulo','')} ({c.get('enforcement')})")
        lines.append(f"- Disparó por: {', '.join(hits)}")
        lines.append(f"- Requisito: {c.get('requisito','').strip()}")
        lines.append(f"- Fuente: {c.get('fuente','')}")
        lines.append(f"- Principio: {c.get('mapea_principio','—')}")
        lines.append(f"- EARS-semilla: {c.get('patron_ears','').strip()}\n")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--format", choices=["md", "tags", "json"], default="md")
    args = ap.parse_args()

    matched = route(args.prompt)
    if args.format == "tags":
        print(", ".join(as_tags(matched)))
    elif args.format == "json":
        print(json.dumps({
            "policies": [c["id"] for c, _ in matched],
            "tags": as_tags(matched),
            "detail": [{"id": c["id"], "enforcement": c.get("enforcement"),
                        "triggers_hit": h, "principio": c.get("mapea_principio")}
                       for c, h in matched],
        }, ensure_ascii=False, indent=2))
    else:
        print(as_md(args.prompt, matched))


if __name__ == "__main__":
    main()
