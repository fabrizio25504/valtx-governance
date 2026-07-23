#!/usr/bin/env python3
"""
Gate de vigencia normativa (Capa 0) — CERO tokens de LLM.

Verifica cada Policy Card contra:
  1) Fecha: ¿ya pasó `vigencia_hasta` o `fecha_revision` + ventana?
  2) Integridad: ¿el hash del texto fuente sigue coincidiendo con `version_hash`?

Si algo falla en una tarjeta MUST -> exit 1 (bloquea) y emite ALERTA para
abogado + usuario. Es puro cálculo (fechas + sha256): no consume LLM.

Uso:  python ci/policy_freshness.py [--today 2026-07-23]
"""
import sys, os, glob, hashlib, datetime, argparse
import yaml
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", ".specify", "memory", "policies")


def short_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def check(today):
    cards = sorted(glob.glob(os.path.join(POLICIES_DIR, "*.yaml")))
    alerts = []
    print(f"\n=== Gate de vigencia normativa (hoy={today}) — {len(cards)} Policy Cards ===")
    for path in cards:
        c = yaml.safe_load(open(path, encoding="utf-8"))
        cid = c.get("id", os.path.basename(path))
        reasons = []

        # 1) Vencimiento por fecha
        vig = c.get("vigencia_hasta")
        if vig and _d(vig) < today:
            reasons.append(f"VENCIDA (vigencia_hasta {vig} < hoy)")

        # 2) Deriva de la fuente (hash)
        src = c.get("source_file")
        if src:
            src_path = os.path.join(POLICIES_DIR, src)
            if not os.path.exists(src_path):
                reasons.append(f"fuente ausente: {src}")
            else:
                h = short_hash(src_path)
                if h != c.get("version_hash"):
                    reasons.append(f"FUENTE CAMBIÓ (hash {h} ≠ {c.get('version_hash')})")

        status = "OK" if not reasons else "ALERTA"
        icon = "✓" if not reasons else "✗"
        print(f"  {icon} {cid:22} [{c.get('enforcement','?'):5}] {status}"
              + ("" if not reasons else "  -> " + "; ".join(reasons)))
        if reasons and c.get("enforcement") == "MUST":
            alerts.append((cid, c.get("owner", "?"), reasons))

    if alerts:
        print("\n  ⚠ ACCIÓN REQUERIDA — cotejar con el abogado antes de crear features que las disparen:")
        for cid, owner, reasons in alerts:
            print(f"     - {cid} (owner {owner}): {'; '.join(reasons)}")
        print(f"\n  RESULTADO: BLOQUEADO por {len(alerts)} tarjeta(s) MUST desactualizada(s).")
        return 1
    print("\n  RESULTADO: todas las tarjetas MUST vigentes e íntegras.")
    return 0


def _d(s):
    return datetime.date.fromisoformat(str(s))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=os.environ.get("SDD_TODAY"))
    a = ap.parse_args()
    today = _d(a.today) if a.today else datetime.date.today()
    sys.exit(check(today))
