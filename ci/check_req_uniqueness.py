#!/usr/bin/env python3
"""
Gate 6 — unicidad global de IDs de REQ.

A diferencia de los gates 2-5, este NO recibe un feature: recorre TODOS los
specs/**/spec.md de una sola pasada, porque el invariante que protege es
global, no por feature. Y ya está asumido como cierto en todo el tooling
existente sin que nada lo garantice:

  - check_traceability.py:all_declared_reqs() une los REQ de TODOS los specs
    para construir el universo de huérfanos (un REQ es válido si existe en
    CUALQUIER spec del repo).
  - check_traceability.py:scan_code() y notify-merge.yml recorren src/ ENTERO
    para contar citas de REQ — no filtran por feature.

Si dos features declaran el MISMO REQ-XXX-### (o comparten PREFIJO, aunque
la numeración todavía no choque), esas cuentas globales se contaminan: un
REQ ajeno ya implementado hace que `implemented_any` se dispare en un spec
en draft que nunca escribió una línea de código (bloqueo con diagnóstico
falso "implementación parcial"), y el HITS/TOTAL de notify-merge.yml cuenta
REQ que no son de ese feature, clasificando mal la etapa del merge.

Dos invariantes, ambos bloquean:

  1. ID DUPLICADO: el mismo REQ-XXX-### aparece en el spec de dos features
     distintos. Es la colisión dura — ambas citas apuntan al mismo REQ, no
     hay forma de saber a cuál pertenece una implementación.

  2. PREFIJO COMPARTIDO: dos features distintos usan el mismo prefijo de
     área (la parte XXX de REQ-XXX-###), aunque hoy los números no choquen
     (REQ-EXP-001 vs REQ-EXP-003). El prefijo es el namespace del feature;
     compartirlo es una colisión de ID en cuanto la numeración se solape,
     no un caso hipotético — es cuestión de tiempo.

Uso: python ci/check_req_uniqueness.py   (sin argumentos — recorre specs/ entero)
"""
import sys, os, re, glob
from collections import defaultdict

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.join(os.path.dirname(__file__), "..")
REQ = re.compile(r"REQ-([A-Z]+)-(\d+)")


def feature_reqs():
    """{feature_name: set(REQ-XXX-###)} por cada specs/*/spec.md."""
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "specs", "*", "spec.md"))):
        feature = os.path.basename(os.path.dirname(p))
        text = open(p, encoding="utf-8").read()
        reqs = {f"REQ-{area}-{num}" for area, num in REQ.findall(text)}
        if reqs:
            out[feature] = reqs
    return out


def main():
    by_feature = feature_reqs()

    # ID -> features que lo declaran
    id_owners = defaultdict(set)
    # prefijo -> features que lo usan
    prefix_owners = defaultdict(set)
    for feature, reqs in by_feature.items():
        for req in reqs:
            id_owners[req].add(feature)
            prefix = req.rsplit("-", 1)[0]  # "REQ-EXP-001" -> "REQ-EXP"
            prefix_owners[prefix].add(feature)

    print(f"\n=== Gate de unicidad global de REQ ({len(by_feature)} feature(s) con specs, "
          f"{len(id_owners)} REQ únicos) ===")

    rc = 0

    dup_ids = {req: feats for req, feats in id_owners.items() if len(feats) > 1}
    if dup_ids:
        rc = 1
        print(f"  ✗ {len(dup_ids)} ID(s) DUPLICADO(S) entre features distintos:")
        for req, feats in sorted(dup_ids.items()):
            print(f"       {req}  <- declarado en: {', '.join(sorted(feats))}")

    shared_prefixes = {p: feats for p, feats in prefix_owners.items() if len(feats) > 1}
    if shared_prefixes:
        rc = 1
        print(f"  ✗ {len(shared_prefixes)} PREFIJO(S) COMPARTIDO(S) entre features distintos "
              f"(misma área, numeración va a chocar):")
        for prefix, feats in sorted(shared_prefixes.items()):
            print(f"       {prefix}-###  <- usado por: {', '.join(sorted(feats))}")

    if rc == 0:
        print("  ✓ todos los REQ y prefijos son únicos por feature.")
    else:
        print("  RESULTADO: BLOQUEADO — resolvé la colisión de arriba (renombra el REQ/prefijo "
              "en el feature más nuevo) antes de mergear.")

    return rc


if __name__ == "__main__":
    sys.exit(main())
