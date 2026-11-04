# ────────────────────────────────────────────────────────────────────────────
# 8.1 Resumen de las 3 corridas (juez qwen2.5:72b) — lee los resultados guardados; no vuelve a jugar
# ────────────────────────────────────────────────────────────────────────────
# Cada corrida guardó juez_por_turno_*.csv (nota 0-100 por turno, sistema y rúbrica) y faithfulness_*.csv (RAGAS).
# Los turnos se agrupan por lo que ponen a prueba, para ver qué componente explica cada mejora:
#   estado y acciones → herramientas + estado externo · memoria y mapa → memoria en grafo · reglas → RAG del SRD
import glob
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

RUNS_DIR, RUNS_TAG = "runs_holdout2", "holdout2"   # hold-out usado para la cifra oficial de esta versión
SISTEMAS = ["Baseline", "Agente v1", "Multi v2"]
NOMBRES = {"Baseline": "Baseline (LLM + historial)", "Agente v1": "Agéntico (ReAct + herramientas)",
           "Multi v2": "Agéntico + RAG + memoria en grafo"}
COLORES = {"Baseline": "#2a78d6", "Agente v1": "#eb6834", "Multi v2": "#1baf7a"}
TIPO = {"srd": "Reglas del SRD\n(→ RAG)", "route": "Memoria y mapa\n(→ grafo)", "relation_memory": "Memoria y mapa\n(→ grafo)",
        "expansion_memory": "Memoria y mapa\n(→ grafo)", "event_memory": "Memoria y mapa\n(→ grafo)",
        "connection_check": "Memoria y mapa\n(→ grafo)"}
ORDEN_TIPOS = ["Estado y acciones\n(→ herramientas)", "Memoria y mapa\n(→ grafo)", "Reglas del SRD\n(→ RAG)", "Total"]

J = pd.concat([pd.read_csv(f).assign(corrida=i) for i, f in
               enumerate(sorted(glob.glob(f"{RUNS_DIR}/juez_por_turno_{RUNS_TAG}*.csv")), 1)])
J = J[J.juez == "72B"].copy()
J["tipo"] = J.field.map(TIPO).fillna("Estado y acciones\n(→ herramientas)")
n_corridas = J.corrida.nunique()

# 1) Nota final y rúbricas: media ± desviación entre corridas
por_corrida = J.groupby(["corrida", "sistema"])[["consistencia", "reglas", "narrativa", "final"]].mean()
resumen = por_corrida.groupby("sistema").agg(["mean", "std"]).round(1).loc[SISTEMAS].rename(index=NOMBRES)
print(f"Nota del juez 72B (0-100), media ± desviación de {n_corridas} corridas — {RUNS_DIR}")
display(resumen)

# 2) Por tipo de turno
tipos = (J.groupby(["tipo", "corrida", "sistema"]).final.mean().groupby(["tipo", "sistema"]).mean()
         .unstack()[SISTEMAS])
tipos.loc["Total"] = por_corrida.final.groupby("sistema").mean()[SISTEMAS]
tipos = tipos.loc[ORDEN_TIPOS]
n_turnos = J.groupby("tipo").turno.nunique()
print("\nNota por tipo de turno (turnos por tipo: " +
      ", ".join(f"{t.splitlines()[0].lower()} {n_turnos[t]}" for t in ORDEN_TIPOS[:-1]) + ")")
display(tipos.round(1).rename(columns=NOMBRES, index=lambda t: t.replace("\n", " ")))

# 3) RAGAS faithfulness: ¿la respuesta está respaldada por el texto oficial (SRD) / por los eventos reales?
F = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{RUNS_DIR}/faithfulness_{RUNS_TAG}*.csv")))
faith = pd.DataFrame({"reglas (vs SRD)": F[F.field == "srd"].groupby("sistema").faithfulness.mean(),
                      "resumen (vs eventos)": F[F.field == "event_memory"].groupby("sistema").faithfulness.mean()})
print("\nRAGAS faithfulness (0-1)")
display(faith.loc[SISTEMAS].round(2).rename(index=NOMBRES))

# 4) Gráfico: barras agrupadas por tipo de turno
fig, ax = plt.subplots(figsize=(10, 4.8))
ancho, x = 0.26, range(len(ORDEN_TIPOS))
for k, s in enumerate(SISTEMAS):
    pos = [i + (k - 1) * (ancho + 0.01) for i in x]
    barras = ax.bar(pos, tipos[s], width=ancho, color=COLORES[s], label=NOMBRES[s], zorder=3)
    for b, v in zip(barras, tipos[s]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}", ha="center", va="bottom", fontsize=9, color="#333")
ax.set_xticks(list(x))
ax.set_xticklabels(ORDEN_TIPOS, fontsize=9)
ax.axvline(len(ORDEN_TIPOS) - 1.5, color="#bbb", lw=1, ls="--", zorder=1)
ax.set_ylim(0, 105)
ax.set_ylabel("Nota del juez (0-100)", color="#555")
ax.set_title(f"Cada componente mejora el tipo de pregunta que debe resolver — {RUNS_DIR} ({n_corridas} corridas, juez 72B)",
             fontsize=10.5, loc="left", color="#222")
ax.grid(axis="y", color="#e6e6e6", zorder=0)
for lado in ("top", "right", "left"):
    ax.spines[lado].set_visible(False)
ax.tick_params(axis="y", colors="#777", length=0)
ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3)
plt.tight_layout()
plt.savefig(f"figuras/comparacion_{RUNS_TAG}.png", dpi=160, bbox_inches="tight")
plt.show()

# 5) Costo de cada opción: tiempo (de las 3 corridas oficiales), llamadas al LLM y tokens (contador sobre ChatOllama en
#    la misma partida, pruebas/medir_costos.py) y memoria de los modelos que usa cada sistema (sin contar el juez)
import json, re, os
tiempos = {}
for f in sorted(glob.glob(f"{RUNS_DIR}/v2_run*.ipynb")):
    celdas = {c.get("id"): c for c in json.load(open(f))["cells"]}
    for cid, s in (("run-baseline-v2", "Baseline"), ("run-v1-v2", "Agente v1"), ("run-v2", "Multi v2")):
        txt = "".join("".join(o.get("text", "")) for o in celdas[cid].get("outputs", []))
        m = re.search(r"Tiempo total: ([\d.]+)s", txt)
        if m:
            tiempos.setdefault(s, []).append(float(m.group(1)) / (2 * len(TEST_SEQUENCE_V2) if "TEST_SEQUENCE_V2" in globals() else 52))
MEMORIA = {"Baseline": "7B (4.7 GB)", "Agente v1": "7B (4.7 GB)",
           "Multi v2": "7B + bge-m3 + 72B vigilante (~53 GB)" if "v3" in RUNS_TAG else "7B + bge-m3 (5.9 GB)"}
costo = pd.DataFrame({"segundos por jugada": {s: round(sum(v) / len(v), 2) for s, v in tiempos.items()},
                      "modelos en memoria": MEMORIA})
archivo_costos = f"{RUNS_DIR}/costos_{RUNS_TAG}.csv"
if os.path.exists(archivo_costos):
    C = pd.read_csv(archivo_costos).set_index("sistema").rename(index={"Multi": "Multi v2"})
    costo["llamadas al LLM por jugada"] = (C.llamadas_7b_por_jugada + C.llamadas_72b_por_jugada).round(2)
    costo["  de ellas al 72B"] = C.llamadas_72b_por_jugada
    costo["tokens de entrada por jugada"] = C.tokens_entrada_por_jugada
    costo["tokens de salida por jugada"] = C.tokens_salida_por_jugada
    costo["embeddings por jugada"] = C.embeddings_por_jugada
print("\nCosto por jugada (el juez 72B, que solo evalúa, no se cuenta)")
display(costo.loc[SISTEMAS].rename(index=NOMBRES))
