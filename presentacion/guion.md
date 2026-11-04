# Guion — presentación final NLP (5 min + 3 min de preguntas)

Deck: https://claude.ai/artifact/RchWioug6wRbWxAJCuuYBx (cada diapositiva tiene este texto en sus notas).
Tiempo hablado ≈ 4:50 para 13 diapositivas (a ~140 palabras por minuto): ensáyalo con cronómetro. Ordenado según la rúbrica: 1 = problema y solución, 2 = evaluación, 3 = conclusiones.

| # | Diapositiva | Criterio | Tiempo | Acumulado |
|---|---|---|---|---|
| 1 | Un Dungeon Master que no pierde la cuenta | 1 | 0:10 | 0:10 |
| 2 | Un LLM solo narra bien, pero no lleva la cuenta | 1 | 0:15 | 0:25 |
| 3 | Un mundo, las reglas oficiales y partidas de prueba | 1 | 0:20 | 0:45 |
| 4 | Tres sistemas, el mismo modelo: qwen2.5 7B | 1 | 0:20 | 1:05 |
| 5 | Un LLM con todo el historial | 1 | 0:15 | 1:20 |
| 6 | ReAct nativo de LangGraph con estado externo | 1 | 0:20 | 1:40 |
| 7 | La propuesta: el grafo de LangGraph | 1 | 0:30 | 2:10 |
| 8 | RAG de las reglas y memoria en grafo | 1 | 0:20 | 2:30 |
| 9 | La misma medida y el mismo costo para los tres | 2 | 0:25 | 2:55 |
| 10 | +22 puntos, a cambio de ~2× tiempo y ~4× llamadas | 2 | 0:30 | 3:25 |
| 11 | ¿De dónde sale la mejora? | 2 | 0:25 | 3:50 |
| 12 | Más funciones, una prueba más dura | 2 | 0:25 | 4:15 |
| 13 | Separar los hechos del modelo es lo que funciona | 3 | 0:35 | 4:50 |

## 1 · Un Dungeon Master que no pierde la cuenta (10 s)
Buenas. Mi proyecto es un Dungeon Master de D&D hecho con LLMs, en el tema de Agentic RAG y multi-agente. Comparo una línea base con dos sistemas agénticos sobre el mismo modelo.

## 2 · Un LLM solo narra bien, pero no lleva la cuenta (15 s)
El problema. A la línea base, qwen 7B con historial, la califica un juez LLM de 72B de 0 a 100. Narra bien, 70, pero inventa reglas, 35, y ante un movimiento imposible responde «sí, has llegado al bosque»: 16.

## 3 · Un mundo, las reglas oficiales y partidas de prueba (20 s)
Los datos: el mundo del juego, con cinco lugares y cuatro personajes; las reglas oficiales del SRD, 1 285 documentos, que son el corpus del RAG; y partidas de 26 turnos con la respuesta esperada, escritas antes de evaluar.

## 4 · Tres sistemas, el mismo modelo: qwen2.5 7B (20 s)
Tres sistemas con el mismo modelo, qwen 7B: la línea base con prompting, un agente ReAct de LangGraph con herramientas, y la propuesta, multi-agente con RAG y memoria en grafo.

## 5 · Un LLM con todo el historial (15 s)
La línea base: un LLM con el mundo y las reglas en el system prompt y todo el historial. Una llamada por jugada; el estado lo tiene que recordar el modelo.

## 6 · ReAct nativo de LangGraph con estado externo (20 s)
El agente: el ReAct nativo de LangGraph. El LLM llama herramientas, el ToolNode las ejecuta, y el estado vive en Python. No tiene RAG ni memoria del mundo, y a veces se queda en un bucle.

## 7 · La propuesta: el grafo de LangGraph (30 s)
La propuesta, el grafo real de LangGraph. Si el jugador explora, el WorldBuilder crea contenido y el CoherenceChecker lo valida. Luego el ciclo ReAct en verde: un planner con salida estructurada elige la acción y el código la ejecuta. Al final se narra. Los nodos punteados se agregaron en la v3.

## 8 · RAG de las reglas y memoria en grafo (20 s)
Sus dos memorias externas: el RAG sobre el SRD, con la consulta reescrita al término oficial y búsqueda híbrida, y un grafo del mundo y de los hechos de la partida, con búsqueda local al estilo de GraphRAG.

## 9 · La misma medida y el mismo costo para los tres (25 s)
Los tres se miden igual: un juez de 72B con tres rúbricas y nota por logprobs, validado contra un juez más chico; más RAGAS y keywords; y el costo. Siempre en una partida nueva y con tres corridas, porque la primera partida nueva dio un empate: mi primera versión estaba sobreajustada.

## 10 · +22 puntos, a cambio de ~2× tiempo y ~4× llamadas (30 s)
Resultados con la misma medida: baseline 70, agéntico 67 y la propuesta 92; RAGAS en reglas sube de 0.18 a 0.72. El costo: unas dos veces el tiempo y cuatro veces las llamadas del baseline, con tokens parecidos.

## 11 · ¿De dónde sale la mejora? (25 s)
Por tipo de pregunta: en reglas, 35 y 37 contra 81 con RAG. En memoria, el agéntico saca menos que el baseline y el grafo llega a 93. En estado, las herramientas solas empatan; con el planner, 94.

## 12 · Más funciones, una prueba más dura (25 s)
La v3 suma diálogo, vigilante, combate oficial e imágenes. En el tercer hold-out gana por menos, 81.9 contra 78.2, y la partida nueva destapó errores de memoria que corregí después. Probé sus piezas por separado: el clasificador llega a 96 %, y verificar inventos pide el modelo de 72B.

## 13 · Separar los hechos del modelo es lo que funciona (35 s)
Qué funcionó: anclar cada respuesta a su fuente, estado en Python, reglas por RAG e historia en el grafo, de 70 a 92; y medir con partidas nuevas. Qué no: el agente solo, mi primera versión sobreajustada y la v3, que gana poco y es lenta. Límites: no es una ablación, solo búsqueda local de GraphRAG y una muestra chica. Gracias, ¿preguntas?

---

## Preguntas probables (3 min) — respuestas cortas

**¿Por qué no hiciste una ablación (sin RAG, sin grafo)?**
Por tiempo: cada evaluación son ~30 min por corrida y 3 corridas. La mejora en reglas sí es atribuible al RAG (los otros dos no tienen acceso al SRD). Para el grafo la evidencia es por tipo de turno, no aislada; lo dejo como trabajo futuro.

**¿Es GraphRAG de verdad?**
Implementa la parte de búsqueda local: grafo de entidades y relaciones (el registro del mundo + tripletas que extrae un "cronista" de lo que dicen los personajes), vecindario de las entidades de la pregunta y caminos más cortos. No tiene los resúmenes de comunidades ni la búsqueda global del GraphRAG de Microsoft.

**¿El juez no está sesgado si es la misma familia de modelos?**
Es más grande (72B frente a 7B), usa rúbricas con ejemplos y nota por logprobs. Comparado con un juez 7B la correlación fue 0.74 y el 7B era ~5 puntos más generoso. Además se cruza con métricas que no son un LLM opinando: keywords y RAGAS faithfulness contra el texto oficial.

**¿Por qué el agente ReAct sale peor que el baseline?**
Dos razones medidas: en memoria saca menos (55 frente a 70) aunque tiene el historial completo: no tiene herramientas de memoria del mundo, su historial se llena de llamadas a herramientas y su prompt le exige consultar primero el estado actual (causas probables, no aisladas); y es inestable (±6.4), colapsa repitiendo la misma herramienta en algunas corridas.

**¿Cuánto procesamiento usa?**
El sistema evaluado usa qwen2.5 7B (4.7 GB, cuantizado a 4 bits con Ollama); corre en un portátil. La GPU grande (una NVIDIA H200 de 141 GB, de un servidor compartido) se necesita sobre todo para el juez 72B (47 GB). Pico de uso ~60–70 GB. El multi-agente tarda 8–11 s por jugada frente a ~1 s del baseline.

**¿Cómo evitaste el sobreajuste?**
Cada versión se evaluó en una partida nueva escrita antes de mirar resultados (hold-out 1, 2 y 3). El primer hold-out mostró que mis mejoras estaban sobreajustadas (70.8 frente a 69.3). Y lo que corregí después del hold-out 3 no lo reporto como cifra oficial.

**¿Qué técnicas del curso usaste?**
Prompting y system prompts (S1), LLM-as-judge con logprobs (S2), LangChain y herramientas (S3), LangGraph y ReAct (S3–4), RAG y RAGAS faithfulness (S3), salida estructurada con Pydantic.

**¿Qué harías con más tiempo?**
La ablación (sin RAG, sin grafo), un modelo generador más grande, cargar las condiciones del SRD y reducir la latencia.

---

## Preguntas sobre el código y las decisiones (apunta a celdas y funciones del entregable)

Entregable principal: `proyecto_final_v2_entrega.ipynb` (cifra oficial, hold-out 2). La v3 está en `proyecto_final_v3_entrega.ipynb` (versión congelada que se evaluó en el hold-out 3); los arreglos posteriores están en `proyecto_final_v3.ipynb`, sin cifra oficial.

**¿Dónde está el ciclo ReAct y por qué no usaste el agente nativo para el sistema final?**
Celda `graph-v2`: `pensar_node` (el planner elige UN paso con salida estructurada, el modelo Pydantic `Paso`) → `actuar_node` (el código ejecuta la herramienta) → vuelve a `pensar`; `narrar_node` al final. El agente nativo (celda `wrapper-v2`: `v1_agent_node` + `ToolNode`) es el "Agente v1". Lo cambié porque con *tool calling* libre el 7B colapsaba en bucles de `check_state` y no podía imponer reglas como "una pregunta nunca mueve al jugador"; con salida estructurada el código valida cada paso antes de ejecutarlo.

**¿Cómo se calcula la nota del juez?**
Celda `judge-v2`: cliente OpenAI apuntando a Ollama (`/v1`), `logprobs=True`, `top_logprobs=10`, `max_tokens=1`; el system prompt pide un solo dígito 0–4. Se toman las probabilidades de los tokens "0"…"4", se normalizan, y la nota es el valor esperado × 25 (0–100 continuo). Tres rúbricas (consistencia, reglas, narrativa) con ejemplos; la nota final es su promedio ponderado: consistencia 0.5, reglas 0.3, narrativa 0.2 (`RUBRICAS`). Es el patrón de la Semana 2, Clase 3.

**¿Cómo funciona el RAG?**
Celda `srd-v2`: `reescribir_consulta` traduce la pregunta al nombre oficial en inglés ("oso pardo" → "Brown Bear"); `buscar_srd` primero busca coincidencia exacta de nombre y, si no hay, similitud coseno con bge-m3 en Chroma (top-3). El planner lo usa con la acción `reglas`.

**¿Cómo funciona la memoria en grafo?**
Celda `grafo-v2`: `sync_graph` arma un grafo networkx desde el registro del mundo (lugares, NPCs, objetos, `conecta_con`, `esta_en`) más las tripletas narrativas; `graph_context` toma como semillas las entidades nombradas (por nombre o por embedding), devuelve su vecindario a un salto como texto y, si la pregunta pide una ruta, `shortest_path`. `update_chronicle` (celda `wrapper-v2`): cuando una jugada sale de la ventana de 3, un "cronista" con salida estructurada extrae tripletas (sujeto, relación, objeto) y se agregan al grafo.

**¿Por qué temperaturas distintas?**
WorldBuilder 0.9 (crear contenido variado), CoherenceChecker 0.1 (validar de forma estable), planner 0.3, narrador 0.4 (menos adorno que 0.7), baseline y agente 0.7 (el valor por defecto con el que se compararon). En la v3, clasificador 0 y diálogo 0.2.

**¿Por qué el juez es de la misma familia (Qwen)?**
Para usar logprobs locales con Ollama y que sea reproducible sin APIs pagas. Para limitar el sesgo: es mucho más grande que el evaluado, usa rúbricas con ejemplos, lo comparé con otro juez (r = 0.74) y lo cruzo con medidas que no son un LLM opinando (keywords y RAGAS contra el texto oficial).

**¿Cuánto cuesta cada opción?** — ver la sección 8.1 del notebook (tiempo, llamadas, tokens, memoria).

**¿Qué no funcionó?**
El agente ReAct nativo (empata o pierde contra el baseline y es inestable); la primera versión del multi-agente (sobreajustada: empató en el hold-out 1); las reglas por regex para clasificar intención (80 % frente a 96 % con el LLM); un vigilante de 7B (se le escapan inventos); y en la v3, la memoria (61.5 en el hold-out 3) por tres errores que la partida nueva destapó.

**¿Cómo mediste RAGAS faithfulness si el baseline y el agente no usan RAG?**
No uso el contexto que recupera cada sistema, sino una referencia fija e igual para los tres (`contexto_faithfulness`, celda del juez): en los turnos de reglas, el documento oficial del SRD que responde la pregunta (`SRD_GOLD`); en el resumen, los eventos reales de la partida. RAGAS divide la respuesta en afirmaciones y cuenta cuántas respalda ese texto. Es más bien *groundedness* frente a una referencia que la faithfulness clásica de RAG, y no mide la calidad de la recuperación (context precision o recall).
