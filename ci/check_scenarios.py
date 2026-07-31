#!/usr/bin/env python3
"""
Gate 5 — ejecución real de los escenarios Gherkin (pytest-bdd).

Los gates 1-4 verifican CITAS y ESTRUCTURA (policies citadas, REQ trazados,
cobertura EARS<->Gherkin), pero ninguno EJECUTA el .feature. Este código pasaba
los 4 gates en verde:

    def store_location(user_id, lat, lon):
        # REQ-GEO-002 · POL-PE-UBIC-003
        pass

Gate 5 corre pytest-bdd sobre <feature_dir>/steps/ y clasifica cada escenario en
PASSED / FAILED / UNDEFINED / COLLECTION_ERROR, vía el reporte JUnit XML
(builtin de pytest, sin dependencia extra):

  - UNDEFINED: step sin step definition — no es un AssertionError normal;
    pytest-bdd lo reporta como `pytest_bdd.exceptions.StepDefinitionNotFoundError`.
  - COLLECTION_ERROR: steps/ no se pudo IMPORTAR o PARSEAR (import roto —
    p.ej. `from src.modulo import f` cuando src/ todavía no existe en un PR de
    spec —, o error de sintaxis). pytest lo marca con `<error message="collection
    failure">` y `classname=""`, distinto de un `<failure>` de escenario. NO se
    ejecutó ni un solo escenario, así que NUNCA es el rojo sano del TDD en modo
    SPEC: sin esta distinción, un import roto (el caso normal antes de que
    exista implementación) clasificaba como "0 escenarios FALLARON" y el gate
    pasaba en verde sin haber corrido nada.

Ambos casos hay que distinguirlos de un assert real para dar un veredicto
correcto en modo SPEC (ver más abajo).

Dos modos, según `estado:` del front-matter del spec (mismo DRAFT_STATES que
check_traceability.py):

  SPEC (draft/borrador/...): el código todavía no existe -> los escenarios
    TIENEN que fallar. BLOQUEA si hay COLLECTION_ERROR, UNDEFINED, si se
    recolectaron 0 escenarios, o si ALGÚN escenario PASA (sin implementación,
    un escenario en verde es un test que no verifica nada — el clásico
    `assert True`. Es el único momento del ciclo en que se puede comprobar que
    un test ES CAPAZ de fallar; no "corregir" esta regla sin entender por qué
    existe).

  CODE (cualquier otro estado): BLOQUEA si falla algún escenario, si hay
    COLLECTION_ERROR, UNDEFINED, o si se recolectaron 0 escenarios.

Features listados en .specify/memory/legacy_features.txt están exentos de este
gate (advierte y sale 0) — siguen pasando por los gates 1-4. Ese archivo vive
en .specify/memory/ a propósito: es el directorio que el agente tiene PROHIBIDO
tocar (regla del --message de agent-implement.yml), así que la exención es
una decisión humana registrada, no algo de lo que un agente pueda auto-eximirse.

Uso: python ci/check_scenarios.py specs/FEAT-042-geo-checkin/spec.md specs/FEAT-042-geo-checkin/
"""
import sys, os, re, subprocess, tempfile
import xml.etree.ElementTree as ET

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.join(os.path.dirname(__file__), "..")
LEGACY_FILE = os.path.join(ROOT, ".specify", "memory", "legacy_features.txt")

sys.path.insert(0, os.path.dirname(__file__))
from check_traceability import DRAFT_STATES, spec_estado  # mismo criterio spec-first que Gate 3

UNDEFINED_MARK = "StepDefinitionNotFoundError"
# Marcas del traceback que delatan un COLLECTION_ERROR originado en el .feature
# (Gherkin inválido) y no en steps/ (import roto, sintaxis Python). pytest-bdd
# suele rematar este traceback con "Multiple features are not allowed in a
# single feature file" — un mensaje engañoso (no hay dos Features en el
# archivo; el parser simplemente no reconoció NINGUNA línea, típicamente por
# la palabra clave equivocada bajo `# language: es`) que manda a buscar en el
# lugar equivocado si no se distingue esta causa.
FEATURE_PARSE_MARKERS = ("FeatureError", "CompositeParserException", "GherkinParser")


def feature_files(feature_dir):
    return sorted(f for f in os.listdir(feature_dir) if f.endswith(".feature"))


def legacy_features():
    if not os.path.isfile(LEGACY_FILE):
        return set()
    out = set()
    for line in open(LEGACY_FILE, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def run_pytest(steps_dir):
    """Corre pytest sobre steps_dir con reporte JUnit. Devuelve (returncode, stdout, junit_path|None).

    `python -m pytest` antepone el cwd del proceso a sys.path — de eso depende que
    `from src.modulo import f` resuelva dentro de steps/. Antes esto era un supuesto
    implícito (que quien invoque este script esté parado en la raíz del repo); acá
    se fija `cwd=ROOT` explícitamente para que la resolución del import no dependa
    de dónde esté parado el llamador (run_gates.py, sdd-orchestrator.yml, o a mano)."""
    if not os.path.isdir(steps_dir):
        return None, "", None
    steps_dir_abs = os.path.abspath(steps_dir)
    fd, junit_path = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", steps_dir_abs, "--junitxml", junit_path, "-q"],
        capture_output=True, text=True,
        cwd=ROOT,
    )
    return r.returncode, r.stdout + r.stderr, junit_path


def classify(junit_path):
    """Lee el JUnit XML y devuelve lista de (nombre, estado, detalle) por escenario.
    estado en {PASSED, FAILED, UNDEFINED, COLLECTION_ERROR}."""
    if not junit_path or not os.path.isfile(junit_path):
        return []
    root = ET.parse(junit_path).getroot()
    out = []
    for tc in root.iter("testcase"):
        name = f"{tc.get('classname','')}::{tc.get('name','')}"
        node = tc.find("failure")
        err_node = tc.find("error")
        if node is None and err_node is None:
            out.append((name, "PASSED", ""))
            continue
        # pytest marca los fallos de COLECCIÓN (import roto, error de sintaxis en
        # steps/) con <error message="collection failure"> y classname="" — nunca
        # se ejecutó ni un solo escenario, así que NO es el rojo sano del TDD; hay
        # que distinguirlo de un <failure> real (assert) o de un UNDEFINED (step
        # sin step definition), que sí implican que pytest-bdd corrió el escenario.
        if err_node is not None and (err_node.get("message") == "collection failure" or tc.get("classname") == ""):
            out.append((name, "COLLECTION_ERROR", (err_node.text or "").strip()))
            continue
        node = node if node is not None else err_node
        msg = node.get("message", "") or (node.text or "")
        if UNDEFINED_MARK in msg:
            out.append((name, "UNDEFINED", msg.splitlines()[0] if msg else "step sin definir"))
        else:
            out.append((name, "FAILED", msg.splitlines()[0] if msg else "falló"))
    return out


def main(spec_path, feature_dir):
    feature_name = os.path.basename(feature_dir.rstrip("/\\"))

    if feature_name in legacy_features():
        print(f"\n=== Gate de ejecución Gherkin (pytest-bdd) — {feature_name} ===")
        print(f"  ⚠ ADVERTENCIA: '{feature_name}' está en {os.path.relpath(LEGACY_FILE, ROOT)} "
              f"(exento de Gate 5, anterior a su introducción). Sigue pasando por los gates 1-4.")
        return 0

    estado = spec_estado(spec_path)
    mode = "SPEC" if (estado in DRAFT_STATES) else "CODE"
    steps_dir = os.path.join(feature_dir, "steps")

    rc_pytest, output, junit_path = run_pytest(steps_dir)
    scenarios = classify(junit_path)
    if junit_path and os.path.isfile(junit_path):
        os.remove(junit_path)

    print(f"\n=== Gate de ejecución Gherkin — modo {mode} (estado spec: {estado or '—'}, "
          f"{len(scenarios)} escenario(s)) ===")

    if rc_pytest is None:
        print(f"  ✗ no existe {steps_dir}/ — 0 escenarios recolectados.")
    elif not scenarios:
        print(f"  ✗ 0 escenarios recolectados en {steps_dir}/ (pytest exit {rc_pytest}).")
        print(output.strip()[-1500:])

    for name, status, detail in scenarios:
        mark = {"PASSED": "✓", "FAILED": "✗", "UNDEFINED": "✗", "COLLECTION_ERROR": "✗"}[status]
        if status == "COLLECTION_ERROR":
            if any(m in detail for m in FEATURE_PARSE_MARKERS):
                feats = feature_files(feature_dir)
                target = feats[0] if feats else "el .feature"
                print(f"  {mark} {name}  -> {status} ({target} no es Gherkin válido):")
            else:
                print(f"  {mark} {name}  -> {status} (steps/ no se pudo importar/parsear):")
            for ln in detail.splitlines():
                print(f"      {ln}")
        else:
            print(f"  {mark} {name}  -> {status}" + (f": {detail}" if detail else ""))

    collection_errors = [s for s in scenarios if s[1] == "COLLECTION_ERROR"]
    undefined = [s for s in scenarios if s[1] == "UNDEFINED"]
    failed = [s for s in scenarios if s[1] == "FAILED"]
    passed = [s for s in scenarios if s[1] == "PASSED"]

    rc = 0
    if not scenarios:
        rc = 1
    elif collection_errors:
        rc = 1
        feature_parse_errors = [s for s in collection_errors if any(m in s[2] for m in FEATURE_PARSE_MARKERS)]
        if feature_parse_errors:
            feats = feature_files(feature_dir)
            target = feats[0] if feats else "el .feature"
            print(f"  RESULTADO: BLOQUEADO — error de COLECCIÓN: {target} no es Gherkin válido (el parser "
                  f"no pudo leer ninguna línea), así que NO SE EJECUTÓ NINGÚN ESCENARIO. Esto NO es el "
                  f"rojo sano del TDD (modo SPEC) — es un problema en el .feature (p.ej. palabra clave "
                  f"equivocada bajo '# language: es': con ese header la palabra clave es 'Característica:', "
                  f"no 'Feature:'), no en steps/. Si el traceback termina en 'Multiple features are not "
                  f"allowed in a single feature file', ignora esa línea: es un efecto colateral engañoso "
                  f"del parser, no la causa real.")
        else:
            print(f"  RESULTADO: BLOQUEADO — error de COLECCIÓN en steps/: los step definitions no se "
                  f"pudieron importar/parsear, así que NO SE EJECUTÓ NINGÚN ESCENARIO. Esto NO es el rojo "
                  f"sano del TDD (modo SPEC) — es un problema en steps/ (import roto, error de sintaxis) "
                  f"que hay que arreglar antes de que el gate pueda evaluar nada.")
    elif undefined:
        rc = 1
        print(f"  RESULTADO: BLOQUEADO — {len(undefined)} step(s) sin step definition.")
    elif mode == "SPEC":
        if passed:
            rc = 1
            print(f"  RESULTADO: BLOQUEADO — {len(passed)} escenario(s) PASA(N) en modo SPEC (sin "
                  f"implementación, un escenario en verde no verifica nada; ver docstring del gate).")
        else:
            print(f"  RESULTADO: OK — {len(failed)} escenario(s) fallan como se espera "
                  f"(rojo del TDD, todavía no hay implementación).")
    else:  # CODE
        if failed:
            rc = 1
            print(f"  RESULTADO: BLOQUEADO — {len(failed)} escenario(s) fallan.")
        else:
            print(f"  RESULTADO: OK — {len(passed)} escenario(s) pasan.")

    if rc == 1 and not scenarios:
        print("  RESULTADO: BLOQUEADO — 0 escenarios recolectados.")

    return rc


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("uso: check_scenarios.py <spec.md> <feature_dir>"); sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
