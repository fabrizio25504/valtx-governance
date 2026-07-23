#!/usr/bin/env python3
"""
Ensamblador de contexto selectivo (Capa 0 + Constitución).

En vez de meter TODA la constitución y TODO el corpus legal al prompt, selecciona
solo los 3–5 principios y Policy Cards cuyos `applies_when`/`triggers` intersecan
los `tags` del feature. Es la palanca #1 de costo y de calidad:
  selección relevante ~96% cumplimiento vs ~78% con constitución completa
  (Constitutional SDD, Marri 2026).

Imprime el bundle y una estimación de tokens (naïve vs selectivo) para dimensionar
el ahorro. Uso:  python ci/context_bundler.py specs/FEAT-042-geo-checkin/spec.md
"""
import sys, os, glob, re
import yaml
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.join(os.path.dirname(__file__), "..")
CONSTITUTION = os.path.join(ROOT, ".specify", "memory", "constitution.md")
POLICIES_DIR = os.path.join(ROOT, ".specify", "memory", "policies")

TOK = lambda s: max(1, len(s) // 4)  # estimación grosera: ~4 chars/token


def parse_frontmatter(spec_path):
    txt = open(spec_path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", txt, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def parse_principles():
    txt = open(CONSTITUTION, encoding="utf-8").read()
    out = []
    for block in re.findall(r"<!--\s*PRINCIPLE\s*(.*?)-->", txt, re.S):
        d = yaml.safe_load(block)
        d["_raw"] = block.strip()
        # applies_when puede venir como lista o ['*']
        aw = d.get("applies_when", [])
        d["applies_when"] = aw if isinstance(aw, list) else [aw]
        out.append(d)
    return out


def load_cards():
    cards = []
    for p in sorted(glob.glob(os.path.join(POLICIES_DIR, "*.yaml"))):
        c = yaml.safe_load(open(p, encoding="utf-8"))
        c["_path"] = p
        cards.append(c)
    return cards


def select(tags, principles, cards):
    tset = {t.lower() for t in tags}
    sel_p = [p for p in principles
             if "*" in p["applies_when"] or tset & {a.lower() for a in p["applies_when"]}]
    sel_c = [c for c in cards if tset & {t.lower() for t in c.get("triggers", [])}]
    return sel_p, sel_c


def build_bundle(tags):
    principles = parse_principles()
    cards = load_cards()
    sel_p, sel_c = select(tags, principles, cards)

    lines = [f"# CONTEXTO SELECTIVO (tags: {', '.join(tags)})\n",
             "## Principios constitucionales aplicables"]
    for p in sel_p:
        lines.append(f"- [{p['id']}] ({p['enforcement']}) {p.get('constraint','')}")
    lines.append("\n## Normativa aplicable (Policy Cards)")
    for c in sel_c:
        lines.append(f"- [{c['id']}] ({c['enforcement']}) {c.get('requisito','').strip()}"
                     f"\n    Fuente: {c.get('fuente','')} · EARS-semilla: {c.get('patron_ears','').strip()}")
    bundle = "\n".join(lines)

    # Estimación de ahorro
    full = (open(CONSTITUTION, encoding='utf-8').read()
            + "".join(open(c['_path'], encoding='utf-8').read() for c in cards))
    print(bundle)
    print("\n" + "=" * 64)
    print(f"Principios: {len(sel_p)}/{len(principles)} seleccionados | "
          f"Policy Cards: {len(sel_c)}/{len(cards)} seleccionadas")
    print(f"Tokens ~ bundle selectivo: {TOK(bundle):>6}   |   corpus completo: {TOK(full):>6}   "
          f"|   ahorro: {100 - 100*TOK(bundle)//max(1,TOK(full))}%")
    return bundle


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: context_bundler.py <spec.md>"); sys.exit(2)
    fm = parse_frontmatter(sys.argv[1])
    tags = fm.get("tags") or fm.get("triggers") or []
    if not tags:
        print("⚠ el feature no declara `tags:` en el front-matter."); sys.exit(2)
    build_bundle(tags)
