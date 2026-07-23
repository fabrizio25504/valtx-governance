#!/usr/bin/env python3
"""
Gate de cobertura EARS <-> Gherkin (grafo bipartito, NetworkX).

Construye un grafo REQ <-> Scenario a partir de:
  - REQ del spec (EARS)
  - tags @REQ-XXX-NNN en los .feature
Falla (exit 1) si algún REQ del spec no tiene al menos un escenario -> gate 100%.

Uso: python ci/coverage_graph.py specs/FEAT-042-geo-checkin/spec.md specs/FEAT-042-geo-checkin/
"""
import sys, os, re, glob
import networkx as nx
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

REQ = re.compile(r"REQ-[A-Z]+-\d+")


def declared_reqs(spec_path):
    return set(REQ.findall(open(spec_path, encoding="utf-8").read()))


def scenarios(feat_dir):
    """Devuelve {scenario_name: set(REQ)} leyendo tags @REQ-... sobre cada Scenario."""
    out = {}
    files = glob.glob(os.path.join(feat_dir, "**", "*.feature"), recursive=True)
    for f in files:
        pending = set()
        for ln in open(f, encoding="utf-8").read().splitlines():
            s = ln.strip()
            if s.startswith("@"):
                pending |= set(REQ.findall(s))
            elif s.lower().startswith(("scenario", "escenario")):
                name = s.split(":", 1)[-1].strip() or f"{os.path.basename(f)}:{len(out)}"
                out[name] = set(pending)
                pending = set()
    return out


def main(spec_path, feat_dir):
    decl = declared_reqs(spec_path)
    scen = scenarios(feat_dir)

    G = nx.Graph()
    for r in decl:
        G.add_node(r, kind="req")
    for name, reqs in scen.items():
        G.add_node(name, kind="scenario")
        for r in reqs:
            G.add_edge(r, name)

    covered = {r for r in decl if G.degree(r) > 0}
    uncovered = decl - covered
    pct = 100 * len(covered) // max(1, len(decl))

    print(f"\n=== Gate de cobertura EARS↔Gherkin ({len(scen)} escenarios, {len(decl)} REQ) ===")
    for r in sorted(decl):
        mark = "✓" if r in covered else "✗"
        links = [n for n in G.neighbors(r)] if r in G else []
        print(f"  {mark} {r}  -> {', '.join(links) if links else 'SIN ESCENARIO'}")
    print(f"  Cobertura: {pct}%")
    if uncovered:
        print(f"  RESULTADO: BLOQUEADO — {len(uncovered)} REQ sin escenario Gherkin.")
        return 1
    print("  RESULTADO: cobertura 100%.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("uso: coverage_graph.py <spec.md> <feature_dir>"); sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
