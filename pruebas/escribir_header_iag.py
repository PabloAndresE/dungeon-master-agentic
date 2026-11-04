"""Reescribe la introducción (problema, datos, sistemas, medida, costo, cómo correr) y la declaración de IAG."""
import json, sys

DATOS = """### Datos
| Fuente | Qué es | Dónde |
|---|---|---|
| **Mundo del juego** | 5 lugares conectados (taberna, plaza, herrería, bosque, cueva), 4 personajes (Goruk, Elena, Bron y un goblin hostil), objetos, precios y reglas de combate. Estado inicial: 20 PG, 15 de oro, espada oxidada y una poción. | {mundo} |
| **Reglas oficiales de D&D 5e** | System Reference Document 5.1 (CC-BY-4.0), del JSON de 5e-bits/5e-database: **1 285 documentos** (334 monstruos, 362 objetos mágicos, 237 de equipo, 319 hechizos, 33 reglas){secciones}. | `data/srd/` (índice Chroma + embeddings bge-m3) |
| **Partidas de evaluación** | Secuencias de 26 turnos; cada turno = acción del jugador + pregunta de verificación + qué se espera (lugar, inventario, PG, regla del SRD…). Una de **desarrollo** y *hold-outs* escritos **antes** de evaluar cada versión. | celda de la secuencia de prueba |
"""

SISTEMAS = """### Sistemas comparados (mismo modelo generador: qwen2.5 7B, cuantizado a 4 bits)
| | Baseline | Agéntico (Agente v1) | Agéntico + RAG + memoria en grafo (Multi) |
|---|---|---|---|
| **Qué es** | Un LLM con system prompt (mundo, reglas, precios) e historial completo | ReAct nativo de LangGraph: nodo `agent` (LLM con *tool calling*) ⇄ `ToolNode` | Grafo de LangGraph con nodos especializados{nodos} |
| **Estado del juego** | Lo "recuerda" el modelo | En Python; 6 herramientas (`check_state`, `move_to`, `pick_up_item`, `use_potion`, `attack_enemy`, `roll_dice`) | En Python; las respuestas exactas (estado, compras, combate, rutas) las arma el código |
| **Reglas** | Las que sepa el modelo | Las que sepa el modelo | **RAG** sobre el SRD: consulta reescrita, búsqueda híbrida, cita verificada |
| **Memoria** | Historial | Historial + resultados de herramientas | **Grafo** (networkx): mundo + hechos narrativos, búsqueda local y `shortest_path` |
"""

MEDIDA = """### Cómo se mide (igual para los tres)
- **Medida principal:** nota 0–100 de un **LLM-as-judge** (qwen2.5 **72B**, más grande que el modelo evaluado) con 3 rúbricas (consistencia, reglas, narrativa), ejemplos *few-shot* y nota continua a partir de los *logprobs* de los dígitos 0–4 (Semana 2).
- **Complementarias:** keywords por turno y **RAGAS faithfulness** (¿la respuesta está respaldada por el SRD o por los eventos reales?).
- **Costo:** tiempo por jugada, llamadas al LLM, tokens y memoria de los modelos (sección 8.1).
- **Repetición:** 3 corridas por sistema; se reporta media ± desviación (sección 8.1).

### Cómo ejecutarlo
Requiere Ollama con `qwen2.5:latest` (7B, 4.7 GB), `qwen2.5:72b` (juez{juez72}, 47 GB) y `bge-m3`; ajustar `OLLAMA_BASE_URL` en la celda de configuración. La secuencia se elige con la variable de entorno `SECUENCIA` (por defecto, **{seq}**, la de la cifra oficial). Una corrida completa (3 sistemas + jueces + RAGAS) tarda ~30 min en una GPU NVIDIA H200. Las salidas de este notebook son de la corrida 1; las 3 corridas están en `{runs}/` y la sección 8.1 las resume.
"""

V2 = """# Dungeon Master con LLMs: baseline, agente y agente con RAG + memoria en grafo

**Proyecto final — NLP (MMIA 6021 4889)** · **Pablo Encalada** · Octubre 2026
**Tema del curso:** RAG / Agentic RAG con LangChain y LangGraph · agentes con herramientas y multi-agente.

---

## 1. Problema, datos y diseño del experimento

### Problema
Un *Dungeon Master* (DM) de D&D no solo narra: también es el árbitro del juego. Tiene que llevar la cuenta del estado (vida, oro, inventario, ubicación), respetar el mapa, aplicar las reglas oficiales y recordar lo que pasó y lo que dijeron los personajes. Un LLM con el historial de la conversación narra bien, pero **no lleva la cuenta**: cuando no recuerda, inventa reglas, cifras y movimientos imposibles.

**Pregunta del proyecto:** ¿cuánto mejora la consistencia (a) un agente con herramientas y estado externo, y (b) un sistema agéntico que además ancla las reglas con **RAG** sobre el SRD y la historia con **memoria en grafo**? ¿Y a qué costo?

""" + DATOS.format(mundo="celda del mundo (`WORLD_INITIAL`)", secciones="") + "\n" + SISTEMAS.format(
    nodos=": `pensar` (planner ReAct con salida estructurada) ⇄ `actuar`, `narrar`, y `world_builder` → `coherence` cuando el jugador explora") + "\n" + MEDIDA.format(
    juez72="", seq="holdout2", runs="runs_holdout2")

V3 = """# Dungeon Master con LLMs — v3: agente con RAG, memoria en grafo, diálogo, vigilante e imágenes

**Proyecto final — NLP (MMIA 6021 4889)** · **Pablo Encalada** · Octubre 2026
**Tema del curso:** RAG / Agentic RAG con LangChain y LangGraph · agentes con herramientas y multi-agente.

---

## 1. Problema, datos y diseño del experimento

### Problema
El mismo de la v2 (`proyecto_final_v2_entrega.ipynb`): un LLM narra bien pero no lleva la cuenta del juego. La v2 mostró que anclar cada respuesta a su fuente (estado → código, reglas → RAG, historia → grafo) sube la nota de ~70 a ~92. La v3 agrega lo que le faltaba a un DM real (conversar con los personajes, combate con estadísticas oficiales, comprar, imágenes) y un **vigilante** que verifica la narración, y se evalúa en una partida nueva (**hold-out 3**).

""" + DATOS.format(mundo="`data/mundo.json` + fichas de personajes `data/personajes/*.md`",
                   secciones="; las reglas largas se indexan además por subsección") + "\n" + SISTEMAS.format(
    nodos=": `clasificar` (intención, Pydantic) → [`world_builder` → `coherence` si explora] → `pensar` ⇄ `actuar` / `dialogo` → `narrar` → `vigilante` (72B; reintenta 1 vez si encuentra un invento) → `imagen` (SDXL-Turbo)") + "\n" + MEDIDA.format(
    juez72=" y vigilante", seq="holdout3", runs="runs_v3_holdout3")

IAG = """## 9. Declaración de uso de IAG

- **Claude Code (Anthropic)** se usó como asistente de programación y de redacción: implementación, evaluación, depuración y apoyo en la redacción de los textos del notebook y la presentación.
- **El estudiante** definió el tema y la pregunta del proyecto, tomó las decisiones de diseño, revisó los resultados y validó y ajustó las conclusiones a partir de su propio análisis.
- **Modelos dentro del sistema:** qwen2.5 7B, qwen2.5 72B (juez{vig}), bge-m3{sdxl}.
"""


def aplicar(path, header, iag):
    nb = json.load(open(path))
    for c in nb["cells"]:
        if c.get("id") == "header-v2":
            c["source"] = header.splitlines(keepends=True)
        if c.get("id") == "iag-v2":
            c["source"] = iag.splitlines(keepends=True)
    json.dump(nb, open(path, "w"), ensure_ascii=False, indent=1)
    print("ok", path)


for p in sys.argv[1:]:
    if "v3" in p:
        aplicar(p, V3, IAG.format(vig=" y vigilante", sdxl=" y SDXL-Turbo"))
    else:
        aplicar(p, V2, IAG.format(vig="", sdxl=""))
