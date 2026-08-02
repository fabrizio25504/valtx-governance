#!/usr/bin/env python3
"""
Observabilidad de tokens/costo — datos REALES por feature/stage del agente.

aider (vía LiteLLM) ya calcula tokens y costo exactos y los imprime al final de cada
run. Este script:
  1. Parsea ese output (--aider-log) o toma cifras manuales (--in/--out).
  2. Estima/usa el costo en USD (precios por modelo; usa el costo de aider si viene).
  3. Persiste una línea en metrics/token_usage.jsonl (viaja en el PR del agente).
  4. Emite un resumen al PR (--summary-out cost_comment.md) y al job summary.

Alimenta el modelo de costo (cost/cost_model.py) con consumo real, no estimado — el
dato que la GG necesita para dimensionar recursos.

Uso:
  python ci/token_meter.py --feature FEAT-044 --stage implement --model gpt-4o-mini --aider-log aider.out
  python ci/token_meter.py --feature FEAT-044 --stage bundle --model haiku --in 390 --out 0
"""
import sys, os, re, json, argparse

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

# USD por 1M tokens (in, out). Match por substring del nombre de modelo (primero el más específico).
PRICES = [
    ("gpt-4o-mini",         (0.15,  0.60)),
    ("gpt-4o",              (2.50, 10.00)),
    ("o1-mini",             (1.10,  4.40)),
    ("claude-3-5-haiku",    (0.80,  4.00)),
    ("claude-3-5-sonnet",   (3.00, 15.00)),
    ("haiku",               (0.80,  4.00)),
    ("sonnet",              (3.00, 15.00)),
    ("opus",               (15.00, 75.00)),
    ("gpt",                 (0.50,  1.50)),  # fallback OpenAI genérico
    ("glm",                 (0.0,   0.0)),   # NVIDIA NIM tier gratis: $0 real, no "modelo faltante"
]
LOG = os.path.join(os.path.dirname(__file__), "..", "metrics", "token_usage.jsonl")


def price_of(model):
    m = (model or "").lower()
    for key, pr in PRICES:
        if key in m:
            return pr
    return (0.0, 0.0)


def cost_from_tokens(model, tin, tout):
    pi, po = price_of(model)
    return round(tin / 1e6 * pi + tout / 1e6 * po, 6)


def _num(s, suf):
    v = float(s.replace(",", ""))
    return int(v * (1e3 if suf.lower() == "k" else 1e6 if suf.lower() == "m" else 1))


def parse_aider(text):
    """Extrae (tokens_in, tokens_out, cost_session|None) del output de aider."""
    tin = tout = 0
    cost = None
    mt = re.search(r"Tokens:\s*([\d.,]+)\s*([kKmM]?)\s*sent,\s*([\d.,]+)\s*([kKmM]?)\s*received", text)
    if mt:
        tin = _num(mt.group(1), mt.group(2))
        tout = _num(mt.group(3), mt.group(4))
    mc = re.search(r"\$([\d.]+)\s*session", text)          # costo de sesión que reporta aider
    if not mc:
        mc = re.search(r"Cost:\s*\$([\d.]+)", text)
    if mc:
        cost = round(float(mc.group(1)), 6)
    return tin, tout, cost


def emit_step_summary(rec):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"### 💸 Costo del agente — {rec['feature']} / {rec['stage']}\n\n")
        f.write(f"| Modelo | Tokens in | Tokens out | USD |\n|---|---:|---:|---:|\n")
        f.write(f"| `{rec['model']}` | {rec['in']:,} | {rec['out']:,} | **${rec['usd']:.4f}** |\n")


def report():
    """Consolida metrics/token_usage.jsonl: por feature, por stage, total y promedio.
    Tokens (in/out) son la métrica principal — comparable entre modelos, incluso
    tier gratis ($0 real). USD es secundario y se muestra igual, pero no reemplaza
    a los tokens: con un modelo sin costo, el total en USD es siempre cero.
    Es el puente hacia cost/cost_model.py — consumo REAL por feature vs. el techo estimado."""
    if not os.path.exists(LOG):
        print("Sin datos aún en metrics/token_usage.jsonl."); return
    rows = [json.loads(l) for l in open(LOG, encoding="utf-8") if l.strip()]

    def _bucket():
        return {"in": 0, "out": 0, "usd": 0.0}

    feats, stages = {}, {}
    tot_in = tot_out = 0
    tot_usd = 0.0
    for r in rows:
        f = feats.setdefault(r["feature"], _bucket())
        s = stages.setdefault(r["stage"], _bucket())
        f["in"] += r["in"]; f["out"] += r["out"]; f["usd"] += r["usd"]
        s["in"] += r["in"]; s["out"] += r["out"]; s["usd"] += r["usd"]
        tot_in += r["in"]; tot_out += r["out"]; tot_usd += r["usd"]

    nfeat = len(feats)
    tot_tok = tot_in + tot_out
    print(f"=== token_meter · consumo REAL ({len(rows)} runs, {nfeat} features) ===\n")

    print("Por stage:")
    for name, b in sorted(stages.items(), key=lambda x: -(x[1]["in"] + x[1]["out"])):
        tok = b["in"] + b["out"]
        pct = f"{100*tok/tot_tok:.0f}%" if tot_tok else "0%"
        print(f"  {name:<12} in {b['in']:>8,}  out {b['out']:>8,}  tok {tok:>9,} ({pct})  ${b['usd']:.4f}")

    print("\nPor feature:")
    for fq, b in sorted(feats.items(), key=lambda x: -(x[1]["in"] + x[1]["out"])):
        tok = b["in"] + b["out"]
        print(f"  {fq:<28} in {b['in']:>8,}  out {b['out']:>8,}  tok {tok:>9,}  ${b['usd']:.4f}")

    print(f"\nTOTAL: in {tot_in:,} / out {tot_out:,} / tok {tot_tok:,}   |   USD ${tot_usd:.4f}")
    print(f"Promedio por feature: {tot_tok/max(1,nfeat):,.0f} tokens   |   ${tot_usd/max(1,nfeat):.4f}")
    print("→ compara este consumo/feature real con el techo de cost/cost_model.py para calibrar.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="consolida el JSONL y sale")
    ap.add_argument("--feature")
    ap.add_argument("--stage")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--in", dest="tin", type=int, default=0)
    ap.add_argument("--out", dest="tout", type=int, default=0)
    ap.add_argument("--aider-log", default="")
    ap.add_argument("--summary-out", default="")
    ap.add_argument("--router-modo", default=None,
                     help="modo del router de Capa 0 (HIBRIDO/DETERMINISTA/DEGRADADO), si aplica a este stage")
    a = ap.parse_args()

    if a.report:
        report(); return
    if not a.feature or not a.stage:
        ap.error("--feature y --stage son obligatorios (o usa --report)")

    tin, tout, cost = a.tin, a.tout, None
    if a.aider_log and os.path.exists(a.aider_log):
        ptin, ptout, pcost = parse_aider(open(a.aider_log, encoding="utf-8", errors="ignore").read())
        tin, tout, cost = ptin or tin, ptout or tout, pcost

    usd = cost if cost is not None else cost_from_tokens(a.model, tin, tout)
    rec = {"feature": a.feature, "stage": a.stage, "model": a.model,
           "in": tin, "out": tout, "usd": round(usd, 6),
           "cost_source": "aider" if cost is not None else "estimado"}
    if a.router_modo:
        # queda en el mismo JSONL que se lee para consumo/costo, así una corrida con
        # el pase semántico degradado (Capa 0) no depende del log de Actions (90 días,
        # no descargable sin permisos de admin) para saber que no fue HIBRIDA.
        rec["router_modo"] = a.router_modo

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    emit_step_summary(rec)
    if a.summary_out:
        with open(a.summary_out, "w", encoding="utf-8") as f:
            f.write(f"💸 **Costo del agente** · `{rec['feature']}`/{rec['stage']} · "
                    f"modelo `{rec['model']}` · in {rec['in']:,} / out {rec['out']:,} tok · "
                    f"**${rec['usd']:.4f}** ({rec['cost_source']})")

    print(f"[token_meter] {rec['feature']}/{rec['stage']} {rec['model']} "
          f"in={tin} out={tout} -> USD {rec['usd']} ({rec['cost_source']})")


if __name__ == "__main__":
    main()
