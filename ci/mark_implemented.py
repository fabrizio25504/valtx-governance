#!/usr/bin/env python3
"""
Pone al día `estado:` del front-matter una vez que el código ya está mergeado
a main, para que deje de mentir en modo "draft para siempre".

Por qué acá y no en agent-implement.yml: agent-implement no puede decidir el
estado: de SU PROPIO spec — sería el agente eligiendo con qué criterio se lo
evalúa (Gate 5 y el enforce de check_traceability.py leen ese campo). Este
script lo corre notify-merge.yml, DESPUÉS del merge a main, disparado por el
evento de push en sí — no por el agente — usando el mismo criterio
(HITS==TOTAL: todo REQ del spec citado en src/) que esa misma workflow ya usa
para clasificar el push como "merge de código". Es la extensión natural de
una sincronización post-merge que esa workflow ya hace con Notion/Issues.

Nota: check_scenarios.py (Gate 5) y check_traceability.py (Gate 3) YA no
dependen de que este script haya corrido — ambos derivan su modo/enforce de
`implemented_any` (REQ citado en src/), la misma señal, calculada en caliente
en cada corrida. Este script existe para que `estado:` no quede desincronizado
para siempre de cara a humanos/Notion, y para que el enforce de Gate 3 se
sostenga aunque en el futuro el código se revierta y `implemented_any` vuelva
a dar falso — no para que los gates funcionen (ya funcionan sin él).

Idempotente: si `estado:` ya no es draft-like, no toca el archivo ni lo
reporta como cambiado (exit 0 en ambos casos; el caller decide si commitear
mirando si el archivo cambió).

Uso: python ci/mark_implemented.py specs/FEAT-042-geo-checkin/spec.md
"""
import sys, os, re

sys.path.insert(0, os.path.dirname(__file__))
from check_traceability import DRAFT_STATES

NEW_ESTADO = "implementado"


def mark_implemented(spec_path):
    """Devuelve True si reescribió el archivo (estado: era draft-like)."""
    text = open(spec_path, encoding="utf-8").read()
    m = re.search(r"^estado:\s*(\S+)\s*$", text, re.M)
    if not m:
        print(f"  ⚠ {spec_path}: no se encontró 'estado:' en el front-matter, no se toca.")
        return False
    current = m.group(1)
    if current.lower() not in DRAFT_STATES:
        print(f"  → {spec_path}: estado ya es '{current}' (no draft-like), no se toca.")
        return False
    new_text = text[:m.start(1)] + NEW_ESTADO + text[m.end(1):]
    open(spec_path, "w", encoding="utf-8").write(new_text)
    print(f"  → {spec_path}: estado '{current}' -> '{NEW_ESTADO}'")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: mark_implemented.py <spec.md>"); sys.exit(2)
    mark_implemented(sys.argv[1])
    sys.exit(0)  # nunca bloquea el push; el caller mira si hubo diff para decidir si commitea
