#!/usr/bin/env python3
"""
Gate de consistencia normativa (Capa 0) — caza ALUCINACIONES DE POLICY en el spec.

El gate de trazabilidad detecta REQ inventados en el CÓDIGO. Este detecta el equivalente
en la capa normativa: un spec que cita una ley/Policy Card que el router NO aprobó o que
NO existe. Es el hueco por el que un agente barato metió "cumple POL-PE-CONSENT-001" en un
feature de mockups que no toca datos personales.

Reglas (bloquean el merge):
  1. INEXISTENTE : POL-xxx citado en el spec que no corresponde a ninguna Policy Card real.
  2. NO APROBADA : POL-xxx citado en el CUERPO que no está en el front-matter `policies:`
                   (el front-matter lo fija el router determinista de Capa 0).
Advierte (no bloquea):
  3. DECLARADA SIN USAR : policy en el front-matter que ningún REQ del cuerpo cita.

Uso: python ci/check_policy_citations.py specs/FEAT-045-app-de-mockups/spec.md
"""
import sys, os, re, glob
import yaml

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

POL = re.compile(r"POL-[A-Z]+-[A-Z]*-?\d+")
ROOT = os.path.join(os.path.dirname(__file__), "..")
POLICIES_DIR = os.path.join(ROOT, ".specify", "memory", "policies")


def real_policy_ids():
    ids = set()
    for p in glob.glob(os.path.join(POLICIES_DIR, "*.yaml")):
        c = yaml.safe_load(open(p, encoding="utf-8"))
        if c and c.get("id"):
            ids.add(c["id"])
    return ids


def split_frontmatter(spec_path):
    txt = open(spec_path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m:
        return {}, txt
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def main(spec_path):
    fm, body = split_frontmatter(spec_path)
    approved = set(fm.get("policies") or [])         # aprobadas por el router (front-matter)
    real = real_policy_ids()
    cited_body = set(POL.findall(body))              # policies citadas en el cuerpo (REQ, tablas)

    nonexistent = (cited_body | approved) - real     # ids que no existen como Policy Card
    unapproved = cited_body - approved               # citadas en cuerpo pero no aprobadas por router
    declared_unused = approved - cited_body          # aprobadas pero ningún REQ las usa

    print(f"\n=== Gate de consistencia normativa ({os.path.basename(os.path.dirname(spec_path))}: "
          f"front-matter {len(approved)} | cuerpo cita {len(cited_body)}) ===")
    rc = 0
    if nonexistent:
        rc = 1
        print(f"  ✗ POLICY INEXISTENTE — {len(nonexistent)} id(s) que no son Policy Card real:")
        for p in sorted(nonexistent):
            print(f"       {p}   <- inventada; bloquea merge")
    if unapproved:
        rc = 1
        print(f"  ✗ CITA NO APROBADA — {len(unapproved)} policy citada en el spec que el router NO seleccionó:")
        for p in sorted(unapproved):
            print(f"       {p}   <- el router no la activó para este feature; alucinación normativa")
    if declared_unused:
        print(f"  ⚠ DECLARADA SIN USAR — {len(declared_unused)} policy en front-matter que ningún REQ cita:")
        for p in sorted(declared_unused):
            print(f"       {p}")
    if rc == 0 and not declared_unused:
        n = len(approved)
        print(f"  ✓ consistencia normativa: {n} policy aprobada(s) y todas citadas correctamente."
              if n else "  ✓ feature sin normativa aplicable y sin citas de policy (correcto).")
    elif rc == 0:
        print("  ✓ sin alucinaciones normativas (solo advertencia de policy no usada).")
    return rc


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: check_policy_citations.py <spec.md>"); sys.exit(2)
    sys.exit(main(sys.argv[1]))
