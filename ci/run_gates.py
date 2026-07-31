#!/usr/bin/env python3
"""
Orquestador local de gates SDD — reproduce lo que hará GitHub Actions.
Corre los 5 gates sobre un feature y devuelve exit!=0 si alguno bloquea.

Gates:
  1. Vigencia normativa (policy_freshness)      — 0 tokens LLM
  2. Consistencia normativa (check_policy_citations) — policies citadas = aprobadas por el router
  3. Trazabilidad / alucinaciones (check_traceability)
  4. Cobertura EARS↔Gherkin (coverage_graph)
  5. Ejecución real de escenarios Gherkin (check_scenarios, pytest-bdd)
  6. Unicidad global de REQ (check_req_uniqueness) — global, corre una vez, no por feature

Uso:  python ci/run_gates.py FEAT-042-geo-checkin
"""
import sys, os, subprocess

ROOT = os.path.join(os.path.dirname(__file__), "..")
PY = sys.executable
try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"


def run(title, args):
    print("\n" + "═" * 70 + f"\n▶ {title}\n" + "═" * 70)
    r = subprocess.run([PY] + args, cwd=ROOT)
    return r.returncode


def main(feat):
    spec = f"specs/{feat}/spec.md"
    fdir = f"specs/{feat}"
    results = {}
    results["Vigencia normativa (Capa 0)"] = run(
        "GATE 1 · Vigencia normativa — 0 tokens LLM", ["ci/policy_freshness.py"])
    results["Unicidad global de REQ"] = run(
        "GATE 6 · Unicidad global de REQ — global, no por feature", ["ci/check_req_uniqueness.py"])
    results["Consistencia normativa (Capa 0)"] = run(
        "GATE 2 · Consistencia normativa — policies citadas = aprobadas por router",
        ["ci/check_policy_citations.py", spec])
    print("\n" + "═" * 70 + "\n▶ Contexto selectivo (no bloquea; mide ahorro de tokens)\n" + "═" * 70)
    subprocess.run([PY, "ci/context_bundler.py", spec], cwd=ROOT)
    results["Trazabilidad / alucinaciones"] = run(
        "GATE 3 · Trazabilidad — orphan-REQ (traceSDD)", ["ci/check_traceability.py", spec, "src/"])
    results["Cobertura EARS↔Gherkin"] = run(
        "GATE 4 · Cobertura EARS↔Gherkin 100%", ["ci/coverage_graph.py", spec, fdir])
    results["Ejecución de escenarios (pytest-bdd)"] = run(
        "GATE 5 · Ejecución real de escenarios Gherkin", ["ci/check_scenarios.py", spec, fdir])

    print("\n" + "█" * 70 + "\n RESUMEN DE GATES\n" + "█" * 70)
    blocked = 0
    for k, v in results.items():
        state = "PASS ✓" if v == 0 else "BLOCK ✗"
        blocked += (v != 0)
        print(f"   {state:9} {k}")
    print("█" * 70)
    if blocked:
        print(f" MERGE BLOQUEADO — {blocked} gate(s) en rojo. Corrige y reintenta.\n")
        return 1
    print(" TODOS LOS GATES EN VERDE — apto para PR/merge.\n")
    return 0


if __name__ == "__main__":
    feat = sys.argv[1] if len(sys.argv) > 1 else "FEAT-042-geo-checkin"
    sys.exit(main(feat))
