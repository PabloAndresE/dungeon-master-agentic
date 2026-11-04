"""Costo por sistema: llamadas al LLM, tokens y tiempo por jugada, sobre la secuencia hold-out de cada versión.
Uso: NB=<notebook> python medir_costos.py <SECUENCIA> <salida.csv>   (sin juez; imágenes apagadas)"""
import sys, time, json, contextlib, io, os
exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
exec(compile("".join(next(c for c in nb["cells"] if c.get("id") == "test-seq-v2")["source"]), "seq", "exec"), g)
from langchain_ollama import ChatOllama, OllamaEmbeddings
import pandas as pd

REG = {"llm": [], "emb": 0}
_gen = ChatOllama._generate
def _contar(self, *a, **k):
    r = _gen(self, *a, **k)
    um = getattr(r.generations[0].message, "usage_metadata", None) or {}
    REG["llm"].append((self.model, um.get("input_tokens", 0), um.get("output_tokens", 0)))
    return r
ChatOllama._generate = _contar
for nombre in ("embed_query", "embed_documents"):
    f = getattr(OllamaEmbeddings, nombre)
    def envoltura(self, *a, _f=f, **k):
        REG["emb"] += 1
        return _f(self, *a, **k)
    setattr(OllamaEmbeddings, nombre, envoltura)

seq = g[sys.argv[1]]
sistemas = {"Baseline": lambda: g["BaselineDM"](g["llm"]), "Agente v1": lambda: g["AgentDMv1"](g["app_v1"]),
            "Multi": lambda: g["MultiAgentDM"](g["app_v2"])}
filas = []
for nombre, crear in sistemas.items():
    g["reset_game"](); dm = crear()
    REG["llm"].clear(); REG["emb"] = 0
    t0 = time.time(); jugadas = 0
    for accion, pregunta, *_ in seq:
        with contextlib.redirect_stdout(io.StringIO()):
            dm.play(accion); dm.play(pregunta)
        jugadas += 2
    dt = time.time() - t0
    m7 = [x for x in REG["llm"] if "72b" not in x[0]]; m72 = [x for x in REG["llm"] if "72b" in x[0]]
    filas.append(dict(sistema=nombre, jugadas=jugadas, seg_por_jugada=round(dt / jugadas, 2),
                      llamadas_7b_por_jugada=round(len(m7) / jugadas, 2), llamadas_72b_por_jugada=round(len(m72) / jugadas, 2),
                      tokens_entrada_por_jugada=round(sum(x[1] for x in REG["llm"]) / jugadas),
                      tokens_salida_por_jugada=round(sum(x[2] for x in REG["llm"]) / jugadas),
                      embeddings_por_jugada=round(REG["emb"] / jugadas, 2)))
    print(filas[-1], flush=True)
pd.DataFrame(filas).to_csv(sys.argv[2], index=False)
print("guardado", sys.argv[2])
