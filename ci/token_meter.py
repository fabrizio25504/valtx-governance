#!/usr/bin/env python3
"""
Observabilidad de tokens/costo (mejora del flujo). Stub para el harness local:
registra el consumo de cada instancia del pipeline en un JSONL y estima costo por
tier de modelo. En producción, el runner del agente lo alimenta con el usage real
que devuelve la API.

Uso:  python ci/token_meter.py --feature FEAT-042 --stage bundle --model haiku --in 390 --out 0
"""
import sys, os, json, argparse

# USD por 1M tokens (aprox., ajustar a tarifas vigentes). in/out.
PRICES = {
    "haiku":  (0.80, 4.00),
    "sonnet": (3.00, 15.00),
    "opus":   (15.00, 75.00),
}
LOG = os.path.join(os.path.dirname(__file__), "..", "metrics", "token_usage.jsonl")


def cost(model, tin, tout):
    pi, po = PRICES.get(model, (0, 0))
    return round(tin / 1e6 * pi + tout / 1e6 * po, 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--in", dest="tin", type=int, default=0)
    ap.add_argument("--out", dest="tout", type=int, default=0)
    a = ap.parse_args()
    c = cost(a.model, a.tin, a.tout)
    rec = {"feature": a.feature, "stage": a.stage, "model": a.model,
           "in": a.tin, "out": a.tout, "usd": c}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[token_meter] {a.feature}/{a.stage} {a.model} in={a.tin} out={a.tout} -> USD {c}")


if __name__ == "__main__":
    main()
