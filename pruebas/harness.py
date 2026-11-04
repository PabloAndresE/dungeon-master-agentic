"""Carga la v3 hasta wrapper-v2 (sin la demo final) para pruebas rápidas."""
import json, contextlib, io, os, sys
os.environ.setdefault("IMAGENES", "0"); os.environ.setdefault("HF_HUB_OFFLINE", "1")
NB = os.environ.get("NB", "/root/dungeon-master-agentic/proyecto_final_v3.ipynb")
os.chdir("/root/dungeon-master-agentic")
nb = json.load(open(NB)); g = {"__name__": "__main__"}
for c in nb["cells"]:
    if c["cell_type"] != "code": continue
    s = "".join(c["source"]).replace("http://localhost:11434", "http://127.0.0.1:11500")
    if c.get("id") == "wrapper-v2": s = s[:s.rindex("resp = dm_v2.play(")]
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(s, c.get("id"), "exec", flags=0x2000), g)
    if c.get("id") == "wrapper-v2": break
