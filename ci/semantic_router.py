#!/usr/bin/env python3
"""
Router semántico (Capa 0, envoltorio) — agrega un pase LLM sobre el router determinista
de policy_router.py para cubrir lo que el matching léxico no ve (sinónimos, homógrafos).

No reemplaza al determinista: es un sistema de cumplimiento normativo y "el modelo no lo
consideró relevante" no es reconstruible ante una auditoría. Contrato (unión, nunca resta):
  - lo que dispara el determinista va sí o sí, nunca se quita.
  - lo que agrega el modelo se marca `origen: semantico` con su razón.
  - lo que el modelo cree que sobra se reporta como advertencia — la policy NO se quita.
  - un id que el modelo inventa (no está en el catálogo) se descarta en silencio.

Si el modelo falla por lo que sea (sin key, HTTP, JSON inválido, timeout) la salida sigue
siendo válida —es el piso determinista— pero se marca `modo: DEGRADADO` en el JSON, el
markdown y stderr: no sumamos una quinta instancia de degradación silenciosa a las que ya
tiene el repo (gather_context `|| true`, update_notion `if not TOKEN: return 0`, el falso
verde de Gate 5, las métricas tiradas por .gitignore).

Uso:
  python ci/semantic_router.py --prompt "..." --json-out capa0.json   # md a stdout + JSON a archivo
  python ci/semantic_router.py --prompt "..." --format tags
  SDD_ROUTER_SEMANTIC=0 python ci/semantic_router.py --prompt "..."   # fuerza determinista puro (A/B)
  python ci/semantic_router.py --eval [--json-out ...]                # A/B determinista vs híbrido
"""
import sys, os, glob, json, argparse, re
import requests

sys.path.insert(0, os.path.dirname(__file__))
import policy_router as pr

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

BASE = os.environ.get("SDD_ROUTER_BASE", "https://integrate.api.nvidia.com/v1")
MODEL = os.environ.get("SDD_ROUTER_MODEL", "z-ai/glm-5.2")
API_KEY = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")

EVAL_CASES = [
    ("falso_negativo_registro", "se registra a los inscritos"),
    ("falso_negativo_logging_FEAT-052", "logs de acceso"),
    ("falso_positivo_politica", "política de retención"),
]


def _compact_catalog(cards):
    return [{"id": c["id"], "titulo": c.get("titulo", ""),
             "enforcement": c.get("enforcement"), "requisito": c.get("requisito", "").strip()}
            for c in cards]


def _strip_fences(s):
    s = s.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", s, re.S)
    return m.group(1).strip() if m else s


def call_model(prompt, matched, cards):
    """Llama al LLM. Puede lanzar cualquier excepción — el caller decide DEGRADADO."""
    if not API_KEY:
        raise RuntimeError("sin API key (NVIDIA_API_KEY / OPENAI_API_KEY)")
    elegido = [c["id"] for c, _ in matched]
    sys_msg = (
        "Sos un clasificador de aplicabilidad normativa. Te doy un catálogo compacto de "
        "Policy Cards de protección de datos peruana y un texto de feature. Devolvé SOLO "
        "JSON puro (sin markdown, sin texto alrededor) con esta forma exacta: "
        '{"aplica": [{"id": "...", "razon": "..."}], "dudosas": [{"id": "...", "razon": "..."}]}. '
        "'aplica' son cards que el análisis léxico NO detectó pero claramente aplican por "
        "significado. 'dudosas' son cards que el análisis léxico SÍ eligió pero creés que "
        "no debería aplicar (falso positivo por homógrafo, etc.)."
    )
    user_msg = json.dumps({
        "catalogo": _compact_catalog(cards),
        "texto_feature": prompt,
        "ya_elegidas_por_lexico": elegido,
    }, ensure_ascii=False)
    r = requests.post(
        f"{BASE}/chat/completions",
        json={
            "model": MODEL,
            "temperature": 0,
            "max_tokens": 900,
            "messages": [{"role": "system", "content": sys_msg},
                         {"role": "user", "content": user_msg}],
        },
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(_strip_fences(content))
    except json.JSONDecodeError as e:
        # GLM-5.2 tiene sangrado documentado de caracteres chinos en texto español — un
        # carácter suelto rompe json.loads. Sin el fragmento crudo, esto se ve idéntico
        # a un modelo que devolvió prosa en vez de JSON.
        raise RuntimeError(f"JSON inválido del modelo ({e}): {content[:300]!r}") from e


def route_hybrid(prompt):
    """Devuelve el dict de estructura completa (modo/policies/tags/detalle/advertencias/error_semantico)."""
    cards = pr.load_cards()
    matched = pr.route(prompt)
    by_id = {c["id"]: c for c in cards}
    det_ids = {c["id"] for c, _ in matched}
    matched_ids = set(det_ids)

    detalle = [{"id": c["id"], "origen": "determinista", "enforcement": c.get("enforcement"),
                "triggers_hit": hits, "principio": c.get("mapea_principio")}
               for c, hits in matched]
    policies = [c["id"] for c, _ in matched]
    tags = pr.as_tags(matched)
    advertencias = []
    error_semantico = None

    semantic_enabled = os.environ.get("SDD_ROUTER_SEMANTIC", "1") != "0"
    if semantic_enabled:
        try:
            resp = call_model(prompt, matched, cards)
            for item in resp.get("aplica", []):
                cid = item.get("id")
                c = by_id.get(cid)
                if not c or cid in matched_ids:
                    continue  # id inexistente (alucinación) o ya cubierto por el determinista
                # las policies agregadas por el modelo no aportan tags — `tags` sigue
                # significando "lo que matcheó literalmente" y el puente mapea_principio
                # (que va por `policies`, no por `tags`) sigue funcionando.
                detalle.append({"id": cid, "origen": "semantico", "enforcement": c.get("enforcement"),
                                 "razon": item.get("razon", ""), "principio": c.get("mapea_principio")})
                policies.append(cid)
                matched_ids.add(cid)
            for item in resp.get("dudosas", []):
                cid = item.get("id")
                # contra det_ids, no matched_ids: "dudosa" significa "el DETERMINISTA
                # eligió esto y creo que se equivocó" — si el modelo la propuso él mismo
                # vía `aplica` no es una objeción al determinista, es contradecirse solo.
                if cid in det_ids and by_id.get(cid):
                    advertencias.append({"id": cid, "razon": item.get("razon", ""),
                                          "nota": "se MANTIENE, revisar a mano"})
        except Exception as e:
            error_semantico = str(e)
            print(f"[semantic_router] DEGRADADO — pase semántico falló: {e}", file=sys.stderr)

    if not semantic_enabled:
        modo = "DETERMINISTA"
    elif error_semantico:
        modo = "DEGRADADO"
    else:
        modo = "HIBRIDO"

    return {"modo": modo, "policies": policies, "tags": tags, "detalle": detalle,
            "advertencias": advertencias, "error_semantico": error_semantico}


def as_md(prompt, result):
    detalle, modo = result["detalle"], result["modo"]
    lines = [f"# CAPA 0 · Normas aplicables (modo: {modo})\n"]
    if modo == "DEGRADADO":
        lines.append("**AVISO — pase semántico degradado**: esta selección viene SOLO del "
                      "router determinista (matching léxico por triggers). Tiene falsos "
                      f"negativos conocidos (ver tabla de casos en semantic_router.py). "
                      f"Motivo: {result['error_semantico']}\n")
    if not detalle:
        lines.append("Ninguna Policy Card disparó ni fue agregada por análisis semántico. "
                      "AÚN ASÍ, revisa manualmente: la ausencia de match no garantiza que no aplique norma.")
        return "\n".join(lines)
    lines.append("Cita SOLO estas Policy Cards en el spec (cada REQ debe referenciar la suya):\n")
    cards_by_id = {c["id"]: c for c in pr.load_cards()}
    for d in detalle:
        c = cards_by_id.get(d["id"], {})
        lines.append(f"## {d['id']} · {c.get('titulo','')} ({d.get('enforcement')})")
        if d["origen"] == "determinista":
            lines.append(f"- Disparó por: {', '.join(d['triggers_hit'])}")
        else:
            lines.append(f"- Agregada por análisis semántico — razón: {d.get('razon','')}")
        lines.append(f"- Requisito: {c.get('requisito','').strip()}")
        lines.append(f"- Fuente: {c.get('fuente','')}")
        lines.append(f"- Principio: {d.get('principio','—')}")
        lines.append(f"- EARS-semilla: {c.get('patron_ears','').strip()}\n")
    if result["advertencias"]:
        lines.append("## Advertencias del pase semántico (NO se quitó nada, revisar a mano)\n")
        for a in result["advertencias"]:
            lines.append(f"- {a['id']}: {a['razon']} — {a['nota']}")
    return "\n".join(lines)


def run_eval():
    print("# A/B determinista vs híbrido\n")
    print("# el cuerpo del spec.md NO es el prompt original que generó el feature, así que")
    print("# las filas de features viejos no reproducen lo registrado en su día — sirve")
    print("# para el A/B de hoy, no como reconstrucción histórica.\n")
    cases = list(EVAL_CASES)
    spec_glob = os.path.join(pr.ROOT, "specs", "*", "spec.md")
    spec_paths = sorted(glob.glob(spec_glob))
    if not spec_paths:
        print(f"⚠ AVISO: 0 specs encontrados en {os.path.abspath(spec_glob)} — la tabla de "
              f"abajo SOLO tiene los {len(EVAL_CASES)} casos hardcodeados, está incompleta.\n")
    for spec_path in spec_paths:
        feat = os.path.basename(os.path.dirname(spec_path))
        body = open(spec_path, encoding="utf-8").read()
        body = re.sub(r"^---.*?---\s*\n", "", body, flags=re.S)  # sin front-matter
        words = body.split()[:120]
        cases.append((feat, " ".join(words)))

    changed = 0
    for name, prompt in cases:
        result = route_hybrid(prompt)
        det = [d["id"] for d in result["detalle"] if d["origen"] == "determinista"]
        sem = [d["id"] for d in result["detalle"] if d["origen"] == "semantico"]
        warn = [a["id"] for a in result["advertencias"]]
        did_change = bool(sem or warn)
        changed += did_change
        print(f"## {name} [{result['modo']}]")
        print(f"  determinista: {det or '(ninguna)'}")
        print(f"  + semántico:  {sem or '(nada agregado)'}")
        print(f"  advertencias: {warn or '(ninguna)'}")
        print()
    print(f"Total: {len(cases)} casos, el pase semántico cambió algo en {changed}.")


def _selftest():
    """python ci/semantic_router.py --selftest — smoke test de las 4 reglas del contrato."""
    global call_model
    cards = pr.load_cards()
    real_ids = [c["id"] for c in cards]
    assert len(real_ids) >= 2, "necesito al menos 2 policy cards reales para el selftest"
    det_id, other_id = real_ids[0], real_ids[1]
    det_card = next(c for c in cards if c["id"] == det_id)
    det_trigger = det_card["triggers"][0]

    original = call_model
    try:
        call_model = lambda prompt, matched, cards: {
            "aplica": [{"id": other_id, "razon": "agregada por el mock"},
                       {"id": "POL-NO-EXISTE-999", "razon": "alucinación"}],
            "dudosas": [{"id": det_id, "razon": "el modelo cree que sobra"}],
        }
        result = route_hybrid(det_trigger)
        assert det_id in result["policies"], "no resta: la del determinista debe seguir"
        assert other_id in result["policies"], "agrega: la card nueva del modelo debe entrar"
        assert any(d["id"] == other_id and d["origen"] == "semantico" for d in result["detalle"])
        assert "POL-NO-EXISTE-999" not in result["policies"], "descarta IDs inexistentes en silencio"
        assert any(a["id"] == det_id for a in result["advertencias"]), "advierte sin borrar"
        assert det_id in result["policies"], "la advertencia NO debe haber quitado la policy"
        assert result["modo"] == "HIBRIDO"

        call_model = lambda prompt, matched, cards: (_ for _ in ()).throw(RuntimeError("boom"))
        result2 = route_hybrid(det_trigger)
        assert result2["modo"] == "DEGRADADO"
        assert det_id in result2["policies"], "degradado no debe perder el piso determinista"

        # Fix 5: el modelo propone la MISMA card en 'aplica' y 'dudosas'. No es una
        # objeción al determinista (que nunca la eligió) — es el modelo contradiciéndose
        # solo, y no debe generar advertencia.
        call_model = lambda prompt, matched, cards: {
            "aplica": [{"id": other_id, "razon": "agregada por el mock"}],
            "dudosas": [{"id": other_id, "razon": "el mock se contradice"}],
        }
        result3 = route_hybrid(det_trigger)
        assert other_id in result3["policies"], "sigue agregándose por 'aplica'"
        assert not any(a["id"] == other_id for a in result3["advertencias"]), \
            "no debe advertir sobre una card que el propio modelo agregó (no la eligió el determinista)"
    finally:
        call_model = original
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt")
    ap.add_argument("--format", choices=["md", "tags", "json"], default="md")
    ap.add_argument("--json-out")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        _selftest()
        return

    if args.eval:
        run_eval()
        return

    if not args.prompt:
        print("--prompt es requerido salvo con --eval", file=sys.stderr)
        sys.exit(2)

    result = route_hybrid(args.prompt)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    if args.format == "tags":
        print(", ".join(result["tags"]))
    elif args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(as_md(args.prompt, result))

    if result["modo"] == "DEGRADADO":
        print(f"[semantic_router] modo DEGRADADO — {result['error_semantico']}", file=sys.stderr)


if __name__ == "__main__":
    main()
