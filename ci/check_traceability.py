#!/usr/bin/env python3
"""
Gate de trazabilidad / detección de alucinaciones (traceSDD, Panda 2026).

Los tests NO detectan alucinaciones: el código alucinado pasa los tests igual.
Este gate lo detecta en O(1) por diferencia de conjuntos sobre las citas `REQ-XXX-NNN`:

  - ORPHAN  : REQ citado en el código pero que NO existe en el spec  -> ALUCINACIÓN (bloquea)
  - UNCOVERED: REQ del spec que NUNCA se citó en el código          -> no implementado (bloquea)
  - UNCITED : línea de código no trivial sin ningún REQ cercano      -> ~12% gap (advierte)

Uso: python ci/check_traceability.py specs/FEAT-042-geo-checkin/spec.md src/
"""
import sys, os, re, glob
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

REQ = re.compile(r"REQ-[A-Z]+-\d+")
TRIVIAL = re.compile(r"^\s*(#|\"\"\"|'''|import |from |def |class |else|elif|try|except|finally|@|\)|\}|return\s*$|pass\b)")


def declared_reqs(spec_path):
    return set(REQ.findall(open(spec_path, encoding="utf-8").read()))


def all_declared_reqs():
    """Universo de REQ válidos = unión de TODOS los specs del repo.
    El código puede citar REQ de cualquier feature; solo es alucinación si no
    existe en NINGÚN spec."""
    reqs = set()
    for p in glob.glob(os.path.join("specs", "**", "spec.md"), recursive=True):
        reqs |= set(REQ.findall(open(p, encoding="utf-8").read()))
    return reqs


def scan_code(src):
    files = glob.glob(os.path.join(src, "**", "*.py"), recursive=True) if os.path.isdir(src) else [src]
    cited, uncited = set(), []
    for f in files:
        lines = open(f, encoding="utf-8").read().splitlines()
        # ventana: un REQ citado cubre su bloque hasta la siguiente línea en blanco
        window = set()
        in_doc = False
        for i, ln in enumerate(lines):
            s = ln.strip()
            tq = s.count('"""') + s.count("'''")
            if in_doc:                       # dentro de docstring -> ignorar
                if tq % 2 == 1:
                    in_doc = False
                continue
            if tq % 2 == 1:                  # abre docstring multilínea
                in_doc = True
                continue
            found = set(REQ.findall(ln))
            if found:
                cited |= found
                window |= found
            if not s:
                window = set()
            # línea de código sustantiva sin REQ en su ventana
            if s and not TRIVIAL.match(ln) and not found and not window:
                uncited.append((os.path.basename(f), i + 1, s[:60]))
    return cited, uncited


def main(spec_path, src):
    decl = declared_reqs(spec_path)        # REQ de ESTE feature (para "uncovered")
    universe = all_declared_reqs()         # REQ de TODOS los specs (para "orphan")
    cited, uncited = scan_code(src)
    orphans = cited - universe              # citado en código, inexistente en cualquier spec
    uncovered = decl - cited                # REQ de este feature sin implementar

    print(f"\n=== Gate de trazabilidad (feature: {len(decl)} REQ | universo: {len(universe)} REQ | código cita: {len(cited)} REQ) ===")
    rc = 0
    if orphans:
        rc = 1
        print(f"  ✗ ALUCINACIÓN — {len(orphans)} REQ citado(s) en código que NO existen en el spec:")
        for r in sorted(orphans):
            print(f"       {r}   <- inventado por el agente; bloquea merge")
    if uncovered:
        rc = 1
        print(f"  ✗ SIN IMPLEMENTAR — {len(uncovered)} REQ del spec nunca citado en código:")
        for r in sorted(uncovered):
            print(f"       {r}")
    if uncited:
        print(f"  ⚠ {len(uncited)} línea(s) no trivial(es) sin cita REQ (revisar — ~12% gap):")
        for f, n, t in uncited[:5]:
            print(f"       {f}:{n}  {t}")
    if rc == 0 and not uncited:
        print("  ✓ trazabilidad completa: 0 huérfanos, 0 sin implementar, 0 líneas sin citar.")
    elif rc == 0:
        print("  ✓ sin alucinaciones ni REQ sin implementar (solo advertencias de citas).")
    return rc


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("uso: check_traceability.py <spec.md> <src_dir>"); sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
