import json, copy, sys
CELDA = open("/root/dungeon-master-agentic/pruebas/celda_resumen.py").read()

CONC_V2 = r"""## 8. Conclusiones

### Qué se comparó
Tres sistemas sobre el **mismo modelo generador (qwen2.5:7B)**, la misma partida y el mismo juez (detalle en la sección 1):
**Baseline** (LLM con historial), **Agéntico** (ReAct nativo de LangGraph con herramientas y estado en Python) y **Agéntico + RAG + memoria en grafo** (multi-agente con RAG sobre el SRD 5.1 y memoria en grafo con búsqueda local, al estilo de GraphRAG).
**Evaluación:** *hold-out* 2 (26 turnos escritos antes de evaluar), 3 corridas, juez qwen2.5:72b con 3 rúbricas y *logprobs*, RAGAS faithfulness y keywords. La celda 8.1 recalcula todo desde los archivos de las 3 corridas.

### Resultados: calidad y costo (media de 3 corridas)

| | Baseline | Agéntico | Agéntico + RAG + grafo |
|---|---|---|---|
| **Nota final del juez (0–100)** | 69.8 ± 2.3 | 67.0 ± 6.4 | **91.8 ± 2.1** |
| Consistencia · reglas · narrativa | 67 · 74 · 70 | 65 · 75 · 60 | **93 · 95 · 84** |
| Turnos de estado y acciones (16) | 78.4 | 79.0 | **93.9** |
| Turnos de memoria y mapa (6) | 69.9 | 54.6 | **93.5** |
| Turnos de reglas del SRD (4) | 34.9 | 37.3 | **80.9** |
| RAGAS faithfulness: reglas vs SRD | 0.28 | 0.18 | **0.72** |
| RAGAS faithfulness: resumen vs eventos | 0.29 | 0.21 | **0.62** |
| **Costo:** segundos por jugada | 1.13 | **0.60** | 2.24 |
| **Costo:** llamadas al LLM por jugada | **1.0** | 1.3 | 4.4 |
| **Costo:** tokens de entrada / salida por jugada | 5 783 / 210 | 5 984 / 118 | 6 336 / 361 |
| **Costo:** modelos en memoria | 7B (4.7 GB) | 7B (4.7 GB) | 7B + bge-m3 (5.9 GB) |

El juez 72B (47 GB) se usa solo para evaluar, igual para los tres. Tiempo: corridas oficiales; llamadas y tokens: medidos con un contador sobre `ChatOllama` en la misma partida (`runs_holdout2/costos_holdout2.csv`).

### Qué funcionó
1. **Separar los hechos del modelo y anclar cada respuesta a su fuente.** El estado vive en Python y se lee y modifica con herramientas, con validaciones en código; las reglas salen del SRD por **RAG**; la historia y el mapa, de la **memoria en grafo**. Cada componente mejora justo el tipo de pregunta que debe resolver: reglas 37 → **81** (faithfulness 0.18 → **0.72**), memoria 55 → **94**, estado 79 → **94**. La nota total sube de ~70 a **~92**, sin perder narrativa (84).
2. **Un planner con salida estructurada** (Pydantic) en lugar de *tool calling* libre: el código valida cada paso antes de ejecutarlo (una pregunta no mueve al jugador, una compra exige la intención de comprar).
3. **Evaluar con partidas nuevas** escritas antes de mirar resultados y con un juez más grande que el modelo evaluado (72B frente a 7B; correlación 0.74 con un juez 7B, que es ~5 puntos más generoso).

### Qué no funcionó
1. **El agente con herramientas, solo.** No supera al baseline (67.0 frente a 69.8): empata en estado (79 frente a 78) y pierde en memoria (55 frente a 70) aunque conserva el historial completo; no tiene herramientas de memoria del mundo, su historial se llena de llamadas a herramientas y su prompt le exige consultar primero el estado actual (causas probables; no se aisló cuál pesa más). Es inestable (±6.4) y en ~5 de 21 corridas de desarrollo colapsó repitiendo `check_state`.
2. **La primera versión del multi-agente estaba sobreajustada.** En la primera partida nueva (*hold-out* 1) empató con el baseline (70.8 frente a 69.3). Se corrigió y se evaluó en otra partida nueva (este *hold-out* 2).
3. **Errores del propio evaluador** (copia superficial del estado, juez que premiaba no-respuestas, baseline sin la verdad del juego) inflaban o desinflaban notas; se corrigieron antes de reportar cifras.

### Límites del experimento
- **No es una ablación:** el tercer sistema cambia varias cosas a la vez (multi-agente, planner, RAG, grafo). La tabla por tipo de turno muestra **dónde** actúa cada componente; la mejora en reglas sí se puede atribuir al RAG, porque los otros dos sistemas no tienen acceso al SRD.
- La memoria en grafo implementa la **búsqueda local** de GraphRAG (vecindario y rutas), no los resúmenes de comunidades ni la búsqueda global.
- **Costo:** ~2× el tiempo y ~4× las llamadas al LLM del baseline; los tokens de entrada son parecidos porque el baseline arrastra todo el historial en cada llamada.
- Muestra chica: 26 turnos y 3 corridas por sistema; un solo modelo generador (7B) y un juez de la misma familia (Qwen), cruzado con keywords y RAGAS.

**En una frase:** *un LLM solo narra bien pero no lleva la cuenta; las herramientas solas no lo arreglan; separar el estado del modelo y anclar cada respuesta a su fuente (estado → Python y herramientas, reglas → RAG, historia → grafo) sube la nota de ~70 a ~92, por ~2× el tiempo y ~4× las llamadas, y evaluar con partidas nuevas y un juez más grande fue lo que permitió saber qué mejoras eran reales.*

La continuación (diálogo con NPCs, vigilante de coherencia, imágenes) y su evaluación en un tercer *hold-out* están en `proyecto_final_v3_entrega.ipynb`.
"""

CONC_V3 = r"""## 8. Conclusiones

### Qué agrega la v3
Sobre el sistema **agéntico + RAG + memoria en grafo** de la v2: clasificador de intención con salida estructurada (patrón MRKL), DialogueAgent con fichas de personaje y anclaje por cita, pistas especulativas en el grafo, vigilante de coherencia (72B), combate con estadísticas del SRD, compras, momento del día e imágenes con SDXL-Turbo.

### Resultados en el hold-out 3 (secuencia nueva, 3 corridas, juez 72B; versión congelada `proyecto_final_v3_evaluado.ipynb`)

| | Baseline | Agéntico | Agéntico + RAG + grafo (v3) |
|---|---|---|---|
| **Nota final** | 78.2 ± 3.6 | 73.0 ± 0.4 | **81.9 ± 1.9** |
| Consistencia · reglas · narrativa | 77 · 83 · 75 | 71 · 79 · 69 | **82 · 86 · 75** |
| Turnos de estado y acciones (18) | 79.6 | 78.5 | **91.8** |
| Turnos de memoria y mapa (6) | **86.0** | 69.0 | 61.5 |
| Turnos de reglas del SRD (2) | 42.2 | 35.4 | **54.2** |
| RAGAS faithfulness: reglas vs SRD | 0.09 | 0.22 | **0.30** |
| Keywords (de 26) | 20.7 | 19.7 | **24.3** |
| **Costo:** segundos por jugada | 1.11 | **0.59** | 9.43 |
| **Costo:** llamadas al LLM por jugada | **1.0** | 1.3 | 8.7 (3.3 al 72B) |
| **Costo:** tokens de entrada / salida por jugada | 5 699 / 207 | 5 354 / 122 | 10 438 / 612 |
| **Costo:** modelos en memoria | 7B (4.7 GB) | 7B (4.7 GB) | 7B + bge-m3 + 72B (~53 GB; +~10 GB con imágenes) |

El juez 72B, que solo evalúa, no se cuenta. Llamadas y tokens medidos con imágenes apagadas (`runs_v3_holdout3/costos_v3h.csv`).

### Qué funcionó y qué no
1. **La tendencia de la v2 se repite, pero con un margen menor:** el sistema con RAG y grafo vuelve a ser el mejor (81.9) y el más estable, y el agente solo vuelve a quedar por debajo del baseline. El margen sobre el baseline baja de +22 (v2, hold-out 2) a **+3.7**: el baseline sacó más en esta secuencia (78 frente a 70) y la v3 perdió puntos en memoria.
2. **El hold-out encontró errores que el desarrollo no había visto.** La caída en memoria (61.5) y en reglas se explica por tres fallos: preguntas como "¿quién me afiló la espada?" se respondían con la última frase de Goruk (3 de 3 corridas); "entro en lo que haya encontrado" no resolvía a qué lugar (2 de 3); y la regla de caídas del SRD se respondía mal (2 de 3), porque el documento "The Environment" mezclaba varios temas. Las cifras de esta tabla se reportan **sin corregir**.
3. **Corrección después del hold-out (sin cifra oficial).** Los errores se arreglaron después de evaluar, y luego se hicieron pruebas exploratorias (~100 jugadas con frases nuevas) que encontraron más casos. El principio de todos los arreglos fue el mismo de la conclusión 3 de la v2: **lo que tiene una respuesta exacta lo escribe el código** (estado, compras, combate desde las tiradas, rutas con `shortest_path`, compras y lugares descubiertos desde el registro del mundo). El narrador queda para la ambientación. En reglas: *chunking* por subsección del SRD, cita literal verificada antes de traducir y **abstención** si no hay cita. Con eso la secuencia hold-out 3 responde bien sus 26 turnos en una corrida de verificación, pero esa cifra **no es limpia** (ya conocíamos la secuencia) y no reemplaza a la de la tabla.
4. **Verificar requiere un modelo más grande que generar.** Medido en este proyecto: vigilante de coherencia 72B 6/6 errores sin falsos positivos frente a 7B 5/6 con uno; detector de preguntas de seguimiento 72B 19/20 frente a 7B 8-10/20. El clasificador de intención con el 7B (96 %) sí superó a las reglas con regex (80 %).

### Qué no funcionó
- **La memoria en el hold-out 3** (61.5, por debajo del baseline) por los tres errores de la conclusión 2.
- **El margen sobre el baseline** se achicó a +3.7, con desviaciones que casi se tocan.
- **El costo creció mucho:** ~8.5× el tiempo y ~9× las llamadas del baseline, y el vigilante necesita el 72B en memoria. Para un juego interactivo, 9 s por jugada es lento.

### Límites
- Igual que en la v2, el sistema completo no es una ablación de cada componente.
- La narración libre todavía puede contradecirse (el vigilante no atrapa todo) y los NPCs a veces adornan lo que saben.
- El SRD 5.1 cargado no incluye las condiciones (envenenado, aturdido…).

El detalle de cada error encontrado y su arreglo está en `v3_errores.md`; las pruebas exploratorias, en `pruebas/`.
"""

def aplicar(path, runs_dir, runs_tag, conc, titulo=None):
    nb = json.load(open(path))
    cells = nb["cells"]
    i = next(k for k, c in enumerate(cells) if c.get("id") == "conclusions-v2")
    cells[i]["source"] = conc.splitlines(keepends=True)
    celda = CELDA.replace('RUNS_DIR, RUNS_TAG = "runs_holdout2", "holdout2"', f'RUNS_DIR, RUNS_TAG = "{runs_dir}", "{runs_tag}"')
    if titulo:
        celda = celda.replace('ax.set_title(f"Cada componente mejora el tipo de pregunta que debe resolver — {RUNS_DIR}',
                              f'ax.set_title(f"{titulo} — {{RUNS_DIR}}')
    nueva = {"cell_type": "code", "id": "resumen-corridas", "metadata": {}, "execution_count": None, "outputs": [],
             "source": celda.splitlines(keepends=True)}
    cells[:] = [c for c in cells if c.get("id") != "resumen-corridas"]
    i = next(k for k, c in enumerate(cells) if c.get("id") == "conclusions-v2")
    cells.insert(i, nueva)
    json.dump(nb, open(path, "w"), ensure_ascii=False, indent=1)
    print("ok", path)

V3_TIT = "v3 en el hold-out 3: mejoran estado y reglas; la memoria cae por errores corregidos después"
for p in sys.argv[1:]:
    if "v3" in p:
        aplicar(p, "runs_v3_holdout3", "v3h", CONC_V3, V3_TIT)
    else:
        aplicar(p, "runs_holdout2", "holdout2", CONC_V2)
