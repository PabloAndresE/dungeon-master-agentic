"""v3 — errores del hold-out 3 (diálogo vs memoria, referencia a lo descubierto, preguntas que mueven, reglas mal traducidas)."""
import json, ast

PATH = "proyecto_final_v3.ipynb"
nb = json.load(open(PATH))
cells = {c.get("id"): c for c in nb["cells"]}


def get(cid):
    return "".join(cells[cid]["source"])


def put(cid, s):
    c = cells[cid]
    c["source"] = s.splitlines(keepends=True)
    if c["cell_type"] == "code":
        c["outputs"], c["execution_count"] = [], None


def rep(cid, old, new):
    s = get(cid)
    assert s.count(old) == 1, (cid, old[:80], s.count(old))
    put(cid, s.replace(old, new))


