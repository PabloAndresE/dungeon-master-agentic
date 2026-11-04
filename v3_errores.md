# v3 — errores encontrados jugando (proyecto_final_v3.ipynb)

v2 queda congelada como la versión evaluada (proyecto_final_v2_final_congelado.ipynb, hold-out 2).
La v3 corrige errores encontrados jugando con `python3 jugar.py --notebook proyecto_final_v3.ipynb`.

## Error 1 — Los NPCs no conversan: diálogo fijo y el jugador no lo ve  ✅ corregido

**Síntoma.** "Le digo a Goruk que no tomo alcohol, pido agua" → internamente `talk_to` devolvía siempre
"Bienvenido, viajero. Ten cuidado en el bosque."; el narrador no la mostraba (inventaba otra escena).
Al pedirle información importante, Goruk repetía la misma frase.

**Causa.** `talk_to` devolvía el campo `dialogue` fijo del NPC ignorando lo que decía el jugador; ningún
agente hacía hablar al NPC, y nada obligaba al narrador a citar lo dicho.

**Arreglo (DialogueAgent, patrón MRKL).**
- Nodo `dialogo` nuevo: `pensar → (hablar) → dialogo → pensar`. Habla como el NPC (temp 0.7) con su
  perfil (personalidad + conocimientos), su vecindario en el grafo, su historial con el jugador y,
  para Bron, el SRD de equipo. Si no sabe algo, lo admite en personaje.
- Perfiles nuevos: Goruk (sabe del goblin de la cueva), Elena (pociones a 10 de oro, precio fijo),
  Bron (afila por 5; armas/armaduras del SRD). El precio NO viene del SRD (allí la poción vale 50 po).
- Lo dicho queda en el grafo: `NPC —dijo_a_jugador→ jugador (dijo, jugada)` y en el historial del NPC.
- El narrador NO escribe diálogo: el código agrega la frase textual del DialogueAgent y borra frases
  de personajes inventadas por el narrador (en cualquier jugada).
- Fallback: `talk_to` para NPCs hostiles (el goblin no conversa) o si el agente falla.

**Problemas que aparecieron al probarlo (y su arreglo).**
- Goruk repetía literal el ejemplo de abstención del prompt ("De eso no sé nada, viajero") → se quitó
  la frase literal (los few-shot se copian textual en un 7B).
- El planner iniciaba conversaciones solo ("Voy a la plaza" → hablaba con Elena) → `hablar` solo si el
  jugador se dirige a alguien; si lo nombra ("Le pregunto a Goruk…"), el primer paso es `hablar`.
- "Elena la comerciante: …" dentro de su propia respuesta → se quita el prefijo.
- El narrador respondió en CHINO con texto del SRD en contexto (Qwen cambia de idioma) → si aparecen
  caracteres CJK se regenera una vez pidiendo español y se descartan esas líneas.

**Pendiente.** Suite de diálogo (desarrollo, no hold-out): pregunta informativa (Goruk/cueva → goblin),
negociación (Elena/10 monedas → precio fijo), límite de conocimiento (Goruk/dragón → abstención, patrón
"missing" de CRAG); métricas: faithfulness vs perfil+grafo, consistencia entre turnos, tasa de abstención.
Comprar de verdad (oro −10, poción +1) requiere una herramienta de compra.

## Herramienta de compra (`buy_item`)  ✅
Catálogo por comerciante: Elena vende poción de curación (10 de oro); Bron afila la espada (5 de oro:
"espada oxidada" → "espada afilada"). `comprar(objeto)`: verifica presencia del comerciante y oro,
descuenta, agrega al inventario; queda en el grafo `jugador —compro→ objeto (a X por N)`.
Reglas: `comprar` solo con verbo de compra (regatear no es comprar); compra fallida o exitosa se narra
por código (el narrador inventaba compras o escenas).

## Suite de diálogo (desarrollo, no hold-out)  ✅
Goruk/cueva → goblin ✅ · Goruk/dragón → abstención ✅ · Elena/regateo → mantiene 10 ✅ y no vende ✅ ·
compra real ✅ · sin contradicción entre turnos (variable). Faithfulness vs perfil 0.19–0.38 (el NPC
todavía agrega detalles). Para llegar ahí: anclaje por cita (`hecho_usado`) + chequeo léxico del tema;
abstención con prompt mínimo (si ve sus conocimientos, "desvía": "pregúntale a Bron"); historial del NPC
limitado a 2 frases (el 7B copia frases del historial); un gate por embeddings se descartó (no separaba:
0.47 relevante vs 0.45 irrelevante).

## Errores 2, 3, 6 — preguntas de estado respondidas con texto libre  ✅
"¿Todavía tengo la poción?" → "sí" con el inventario sin poción; inventario con objetos inventados;
"Goruk el herrero en la herrería". **Arreglo:** si la acción pregunta por estado (inventario, oro, HP,
ubicación, qué hay aquí), la respuesta factual la arma el CÓDIGO desde `game_state` (incluye sí/no por
objeto mencionado) y el narrador solo agrega UNA frase de ambiente, que se descarta si menciona
personajes, objetos o números.

## Errores 4, 5 — preguntas de reglas sin consultar el SRD / con escena  ✅
"Según las reglas / cómo funciona / qué daño…" → `reglas()` obligatorio en el primer paso; la respuesta
se genera en modo "solo reglas": el LLM ve ÚNICAMENTE el texto oficial (sin escena, memoria ni historial)
y lo traduce en 1-3 oraciones. Seguimientos "¿Y si…?" consultan con la pregunta anterior + la actual.
**Datos:** `build_docs.py` perdía campos del SRD (vulnerabilidades/resistencias/condiciones de monstruos,
daño a dos manos y alcance de armas) → `build_docs_v3.py` → `docs_v3.jsonl` + índice `srd_bge_m3_v3`
(v2 sigue con `docs.jsonl` para ser reproducible). Indexado con reintentos (el runner de Ollama a veces cae).

## Error 8 — anclaje SRD equivocado (viajero amigable = doppelganger)  ✅
La referencia del WorldBuilder no pasaba el filtro de tipo. Ahora un NPC no hostil solo se ancla a
criaturas `humanoid` o `beast` (si no, `commoner`).

## No se corrigen (hallazgos para la presentación)
9 NPCs agregan consejos que no saben · 10 WorldBuilder conservador · 11 CoherenceChecker sin efecto
comprobado · 12 tripletas triviales del cronista · 13 intención mal clasificada sin "¿" · 14 cambio de
idioma (hay reintento) · 15 copia literal de few-shot · 16 lentitud · 17 errores de redacción.

## Sesión jugada por Pablo (14-oct) — errores A-D  ✅
- **A** "pregunto sobre el lugar…" sin nombrar al NPC → no había diálogo y la respuesta quedaba vacía.
  Ahora, si el jugador se dirige a alguien sin nombrarlo y hay un solo NPC presente, es a él.
- **B** "¿qué me respondió?" → el narrador no recordaba. Ahora lo responde el código con la última frase
  literal registrada (`game_state["dialogos"]`).
- **C** Goruk inventaba estados del mundo ("el estofado se ha agotado") o narraba en vez de hablar →
  DialogueAgent a temp 0.2, regla "no inventes cómo están las cosas", reintento si se nombra a sí mismo o
  describe gestos; "lugar/información/relevante" cuentan como pedidos genéricos (comparte lo que sabe).
- **D** "Goruk, un humano" (es enano) → el nodo del NPC en el grafo lleva su personalidad y los NPCs
  presentes siempre entran como semillas del contexto.

## ImageGenerator (SDXL-Turbo)  ✅
Nodo `imagen` después de narrar; disparadores por código (primera visita, combate, creación del WorldBuilder,
primera conversación con un NPC). El 7B traduce la escena a keywords en inglés (temp 0.3; solo cosas
visibles, sin números ni términos de juego, cantidad exacta de personajes — si no, SDXL dibujaba varios
goblins y montañas de oro). 4 pasos, guidance 0, 512×512, ~0.6-0.9 s/imagen en la H200 (12 s la primera,
carga del modelo; 6.7 GB). `images/turno_N_lugar.png`. Apagado por defecto (IMAGENES=1 / jugar.py --imagenes).
Requiere `pip install diffusers accelerate torch transformers`.

## Regresiones encontradas al probar las imágenes  ✅
- "Voy al bosque" (MOVIMIENTO EXITOSO) → "No hay camino directo… sigues en el bosque": el narrador copiaba la
  estructura del ejemplo few-shot de rechazo → verificación determinista: la narración no puede contradecir
  a MoveResult (se quitan las oraciones contradictorias y se antepone "Llegas a X" / "No hay camino…").
- "Voy a la herrería" desde el bosque → el planner tomaba un paso intermedio de la ruta (plaza) → si la
  acción nombra un lugar, `mover` intenta ESE lugar.
- "Ataco al goblin" (sin goblin) → conversación con Elena + ataque inventado: el nombre de un NPC hostil
  contaba como "dirigirse a alguien", y `mover` se permitía en cualquier acción no-pregunta (el planner
  deambulaba) → hostiles excluidos; `mover` solo si la acción nombra un lugar o usa un verbo de movimiento
  (lista general del español); atacar/recoger/curarse fallidos se narran con el mensaje de la herramienta.

## Quién sabe qué: relaciones entre NPCs en el grafo  ✅
**Problema (Pablo):** Goruk nombraba a Elena como si el jugador ya la conociera, sin tener relación con
ella, y recitaba todo su perfil. **Causa:** los conocimientos de los NPCs eran una lista plana escrita a
mano en el código, sin relaciones ni distinción entre lo propio y los rumores, y el DialogueAgent no sabía
qué personas conoce el jugador.
**Arreglo:**
- Contenido de autor fuera del código: `data/mundo.json` (lugares, estado inicial, personajes con
  personalidad, conocimientos `propio`/`rumor` y `relaciones`).
- Grafo: `NPC —conoce→ NPC (relación: detalle)` y `jugador —conoce→ NPC` (al conversar).
- DialogueAgent: solo habla de personas que conoce, desde la relación; presenta a quien el jugador no
  conoce; los rumores como "dicen que…"; máximo 1-2 cosas por respuesta.
- Preguntas en segunda persona ("¿conoces…?", "¿sabes…?") con un único NPC presente van a ese NPC.
- El NPC no se nombra a sí mismo (reintento y, si persiste, se quitan esas oraciones); respaldo si la
  narración queda vacía; el cronista solo acepta tripletas entre entidades existentes.
**Lección:** parte de los errores eran de DATOS (el perfil decía "herrero" pero no "afila armas"), no de código.

## Vigilante de coherencia (todas las respuestas, no solo creaciones)  ✅
`narrar → vigilante → (incoherente) narrar con la corrección (1 vez) → (persiste) quita esas oraciones → imagen`.
Solo revisa la narración libre del LLM (lo que arma el código ya es correcto por construcción; los diálogos
los cuida el DialogueAgent). Diseño en dos pasos, como RAGAS: extraer hechos de juego (sin ambiente) y
verificar CADA uno contra la verdad del juego (estado después de la jugada + observaciones + personajes
presentes con su perfil + grafo), con la EVIDENCIA antes del veredicto (compatible/inventa/contradice).
- 1.ª versión (una llamada, veredicto antes que evidencia, sin nota temporal): marcaba como "contradice"
  afirmaciones correctas ("llegas a la cueva" → "ya está en la cueva") y borraba casi todo.
- Calibración con 12 casos etiquetados (6 correctos, 6 con errores típicos): **72B 6/6 errores, 0/6 falsos
  positivos, ~7.6 s/narración** · **7B 5/6, 1/6 FP, ~1.3 s** → `WATCHER_MODEL` configurable (72B por defecto,
  7B en la Mac). Castigo conservador: no borra más de la mitad del texto.
- Limitación: atrapa la mayoría de las invenciones, no todas (en un combate dejó pasar "recoges un cofre del
  cuerpo del goblin").

## Fichas .md de personajes + RAG por NPC  ✅
`data/personajes/*.md`: encabezado YAML (datos exactos que usa el código: ubicación, hostil, qué vende,
relaciones → grafo) + secciones en prosa (Personalidad, Lo que sabe, Rumores, Opiniones) que se dividen en
fragmentos y se RECUPERAN por similitud (bge-m3) según lo que dice el jugador: el NPC solo ve lo relevante
(no recita toda su ficha). `data/mundo.json` queda con lugares y estado inicial. Los NPCs creados por el
WorldBuilder escriben su propia ficha en `personajes_partida/` (en jugar.py; apagado en evaluación).
- Ajustes al probar: preguntas de opinión ("¿qué opinas…?", "¿qué te parece…?") dirigidas al NPC presente;
  si el NPC repite casi literal algo que ya dijo, se regenera.

## Fichas: SRD y coherencia  ✅ (puntos 2 y 3; el linter de fichas de autor, punto 1, no se hizo)
- **Goblin con stats inventados:** su ficha tenía PG 12 / CA 10 / 1d6 (del v1) y el SRD dice PG 7 / CA 15 /
  1d6+2 → el juego contradecía las reglas que cita el narrador. Ahora las fichas declaran `srd_ref` y toman
  los stats oficiales al cargar (salvo `stats_propios: true`). Nota: el combate solo usa el DAÑO del enemigo
  (acierto con d20 ≥ 10 fijo; un acierto derrota) — CA y PG no afectan la mecánica.
- **Ficha .md escrita antes de validar:** se escribía antes del CoherenceChecker; si rechazaba, quedaba un
  .md huérfano. Ahora se escribe solo si la creación fue aprobada.
- **CoherenceChecker de creaciones evaluaba contra un mundo que ya incluía la creación** y la marcaba como
  duplicada de sí misma ("Jorge el Explorador ya está en la memoria del mundo"). Ahora recibe el mundo SIN lo
  recién creado. Probable causa de que en las evaluaciones nunca rechazara o rechazara al azar.
- **Pendiente (no hecho):** las fichas de autor no se validan entre sí ni estructuralmente (relaciones a NPCs
  inexistentes, precios contradictorios entre fichas).

## Combate con CA y PG del SRD  ✅
Antes: tu ataque acertaba con d20 ≥ 10 fijo y un acierto derrotaba al enemigo (CA y PG ignorados); solo se
usaba el daño del enemigo. Ahora (D&D 5e simplificado): d20 + bonificador vs CA del enemigo (20 natural =
crítico con dados ×2, 1 natural = fallo); los PG del enemigo bajan por golpe; el enemigo ataca con d20 + su
bonificador del SRD (goblin +4) vs tu CA; daño según tu arma (espada oxidada 1d6, afilada 1d8).
Números de autor en `data/mundo.json` → `reglas_combate`. Balance por simulación (2000 peleas vs goblin):
+2/CA 10 → 42% llega a 0 PG; elegido +5/CA 14 (guerrero de nivel 1) → ~4 rondas, ~9 de daño, 13% (9% con
escudo). Llegar a 0 PG antes no tenía consecuencia: ahora "caes inconsciente" y despiertas con 1 PG.
**Impacto en la evaluación:** las secuencias de prueba tienen UN turno de ataque; ahora el goblin casi nunca
cae en un golpe → los turnos que asumían "goblin derrotado" cambian para los 3 sistemas (en el notebook v3
las reglas son las mismas para todos, así que la comparación sigue siendo justa).

## Error 11 — ruteo con regex frágiles → clasificador de intención (MRKL)  ✅
Nodo `clasificar` al inicio del grafo: salida estructurada (Pydantic) con UNA intención por jugada (mover,
explorar, hablar, comprar, atacar, recoger, curarse, pregunta_estado/reglas/memoria/dialogo, otra). Todo el
ruteo que usaba ~40 regex en español la usa ahora (exploración → WorldBuilder, preguntas solo consultan,
movimiento solo si la intención es mover, acciones que cambian el estado solo si coinciden con la intención).
**Medición** (45 frases coloquiales etiquetadas, ninguna del hold-out 2, p.ej. "me voy pa la plaza", "le doy un
espadazo al goblin", "qué llevo encima"): **regex 80% · clasificador 7B 96%** (43/45), 0.12 s/frase. Los 3 errores
de la primera versión NO se agregaron como ejemplos (habría inflado la medida); el ejemplo agregado ("busco a
alguien que no conozca → explorar") es una regla de diseño, no un caso del test.
Fallos que quedan: "¿quién hay por aquí?" → pregunta_dialogo (debía ser estado); "me llevo una poción, aquí
tienes las monedas" → recoger (debía ser comprar).

## Error 7 — WorldBuilder conservador y SRD irrelevante  ✅
- NPC amigable → perfil `commoner` directo, sin buscar en el SRD (es un bestiario: para "alguien interesante en la
  plaza" recuperaba ochre jelly o shrieker). El SRD queda para enemigos y objetos.
- Si el jugador busca a una persona, el WorldBuilder no recibe referencias del bestiario.
- Menos conservador: "si busca algo que no existe, CREA algo"; 4 ejemplos nuevos.
- De paso: los objetos creados se guardan sin artículo ("un vial" → "vial"); si el NPC devuelve vacío, se regenera.

## Error 10 — memoria narrativa vacía → pistas especulativas en el grafo  ✅
El filtro del cronista exigía que ambos extremos de una tripleta existieran: lo que solo existía en la narración
se perdía. Ahora basta UN extremo conocido; el otro se registra como **pista** (`speculative=True`, gris con "?"
en el dibujo del grafo): se puede consultar, pero no ir ni hablar con ella. Lo que dice un NPC se procesa en el
momento (no 3 jugadas después). Si el jugador sigue la pista ("voy al pantano a buscar a la bruja"), el ruteo
pasa por el WorldBuilder, que ve las PISTAS y crea la entidad; la pista queda CONFIRMADA cuando lo creado
contiene su sustantivo principal (en el nombre o la descripción: crear "el pantano" no confirma "la bruja").
Probado: Goruk → "dicen que una bruja vive en el pantano" → pista `bruja_del_pantano` → "voy al pantano…" crea
el pantano y te lleva → "busco a la bruja" crea la NPC (con ficha .md) → pista confirmada.
Ajustes al probar: el chequeo léxico del DialogueAgent bloqueaba "¿rumores raros?" (pedido abierto); el cronista
no capturaba menciones sin nombre propio; pistas basura de preguntas ("¿te interesa…?"); confirmación laxa por
palabras compartidas. Limitación: depende de que el NPC elija mencionar la pista (comparte 1-2 cosas) y de que el
clasificador entienda a quién se habla ("¿has oído algo de una bruja?" sin interlocutor → pregunta_dialogo).
Contenido nuevo (borrador): rumor de la bruja del pantano en goruk.md.

## Sesión de juego 2 de Pablo (14-oct, noche) — 10 errores  ✅ (después de congelar la v3 evaluada)
1. "pido un vaso de agua" → `comprar` → el clasificador distingue PEDIR (hablar) de COMPRAR/PAGAR.
2. "¿qué aventuras me menciona Goruk?" → `pregunta_dialogo` devolvía la frase anterior → presente con el NPC
   presente = hablar; solo el pasado ("¿qué me dijo…?") devuelve la frase registrada. Bug: "goruk?" con el signo
   pegado no se reconocía como el NPC presente (ahora se ignora la puntuación).
3. Sin tiempo → `momento` del día en el estado (mañana → mediodía → tarde → atardecer → noche, cada 6 jugadas),
   en la línea de estado y en las respuestas factuales ("¿qué hora es?" → "Es mañana: …").
4. Imagen con "a single goblin" en la taberna → se quitan del prompt las keywords que nombran personajes o
   criaturas que no están en la escena.
5. SRD irrelevante para el WorldBuilder (clothes, saddle, mirror) → sin referencias previas; el anclaje posterior
   con umbral sigue usando el SRD.
6. (Bron, vive_en, taberna) por "viene cada noche" → ejemplo en el cronista (frecuenta ≠ vive_en) y se rechazan
   tripletas de residencia que contradicen la capa estructural.
7. check_state repetido → `ver_estado`/`curarse`/`recordar` no se repiten en la misma jugada aunque cambie el argumento.
8. El narrador ignoraba el lugar recién creado → si no lo menciona, se agrega la línea del descubrimiento.
9. Tripletas estéticas o que duplican el mapa → filtradas (bañada, brilla, decoración, puede_ir_a, conecta…).
10. Flood de warnings de TensorFlow/CUDA → jugar.py fija TF_CPP_MIN_LOG_LEVEL=3, USE_TF=0.
Verificado jugando (1-5, 10) y con prueba unitaria del cronista (6, 9).

## Hold-out 3 — resultado oficial y errores encontrados (15-oct)  🔧 (post hold-out: no limpian la cifra)
**Cifra oficial (v3 congelada `proyecto_final_v3_evaluado.ipynb`, 3 corridas, juez 72B):** Baseline 78.2±3.6 ·
Agente v1 73.0±0.3 · Multi v3 81.9±1.9. Juez SRD 42/35/54, faithfulness SRD 0.09/0.18/0.30, keywords 20.7/19.7/24.3.
Los arreglos de abajo se hicieron DESPUÉS de mirar el hold-out 3 (respaldo previo: `proyecto_final_v3_pre_fix_h3.ipynb`).
1. "¿Quién me afiló la espada?" y "Cuéntame la aventura completa" → `pregunta_dialogo` → citaba SIEMPRE el último
   diálogo (Goruk y la bruja), 3/3 corridas. Arreglo: `pregunta_dialogo` exige un verbo de decir en pasado
   (dijo, contó, advirtió…); si no, es `pregunta_memoria` (o `hablar` si el NPC está presente). La frase citada es la
   del NPC nombrado o la que comparte el tema; si ninguna corresponde, responde la memoria. Ejemplos nuevos en el
   clasificador. Seguimientos cortos ("¿Cuánto le pagué?", "¿Cuántos son?") heredan `pregunta_memoria`, y una
   pregunta de memoria siempre consulta primero `recordar`.
2. "Entro en lo que haya encontrado" no resolvía a qué lugar (2/3 corridas: abría un cofre inventado) y luego
   "¿Puedo volver a ese sitio?" (clasificada `mover`) SÍ movía al jugador → "Vuelvo al bosque" fallaba desde el
   pasadizo. Arreglo: referencia a lo descubierto ("lo que haya encontrado", "ese sitio", "ahí") → lugar dinámico más
   reciente conectado; verbo de movimiento + esa referencia → `mover`; una pregunta "¿…?" nunca es `mover`; las
   preguntas de memoria reciben las conexiones reales del lugar.
3. Caídas del SRD mal respondidas ("restando 1d6", "mínimo de 1", sin el máximo 20d6). Tres causas:
   a. Recuperación: "The Environment" mezcla caídas, asfixia y visión → su embedding no se parecía a "fall damage"
      (salían Feather Fall y Ring of Feather Falling). → **chunking por subsección**: cada "### …" de las reglas
      se indexa también como documento propio (50 secciones, índice `srd_bge_m3_v3s`, reutiliza los embeddings).
   b. El planner consultaba `reglas("caida")` (una palabra) → la reescritura daba Feather Fall. → con intención
      `pregunta_reglas` la consulta es la pregunta COMPLETA; una sola consulta de reglas por jugada; un seguimiento
      corto ("¿Hay un máximo?") busca y responde con la pregunta anterior.
   c. Generación: el 7B parafraseaba mal. → **anclaje por cita** (como el DialogueAgent): el modelo copia literal
      las oraciones del SRD que responden (salida estructurada), el código verifica que estén en el texto, y solo
      eso se traduce (temp 0, glosario CA/PG/daño contundente); dados que no están en el texto → se corrige; nunca
      una respuesta vacía (si el filtro de idioma la vacía, se reintenta y si no, la cita oficial).
   Prueba (4 repeticiones): caída 1d6/10 pies, máx 20d6 · oso pardo CA 11, PG 34 · garras 2d6+4 · ventaja ·
   aguantar la respiración (1 + mod. CON, mín. 30 s).
4. Seguimientos cortos que no se entienden solos ("¿Hay un máximo?", "¿Cuánto peso aguanta?", "¿Y si es de tres
   cuartos?", "¿Cuáles son?", "¿Cuánto le pagué?") respondían con el estado o buscaban otra cosa en el SRD ("¿Cuáles
   son?" → venenos). Ya pasaba en la corrida oficial ("¿Hay un máximo?" 3/3). Arreglo: `_seguimiento_corto` (≤5
   palabras o "¿Y…?") hereda la intención anterior (memoria o reglas) si el clasificador dijo estado/otra, salvo una
   pregunta de estado explícita ("¿Dónde estoy?", "¿Cuánto oro tengo?"); si el clasificador dice memoria con
   claridad ("¿qué lugares he descubierto?") no se hereda. Una pregunta de memoria nunca entra al modo "solo reglas"
   aunque la jugada anterior haya consultado el SRD (antes "¿Cómo vuelvo a la cueva?" → "no hay información en el
   texto oficial").
Regresiones que aparecieron al arreglar y se corrigieron: "¿Qué me dijo Goruk?" dejó de citar (el "?" pegado al
nombre); forzar `recordar("")` perdía el tema de la consulta (revertido); la lista de conexiones confundía las
preguntas de ruta (ahora solo con "¿puedo volver/ir…?"); `_norm` borra el "¿" (los patrones "^¿ y" no coincidían).
Verificación: secuencias hold-out 3 y hold-out 2 completas (1 corrida cada una, sin juez) + 52 frases del
clasificador + 10 seguimientos con intención previa. Limitaciones que siguen: "¿Con qué palabras?" con otro NPC
presente se toma como hablarle a ese NPC; la redacción del 7B en reglas a veces es torpe aunque las cifras salgan bien.

## Pruebas exploratorias (15-oct) — 7 escenarios, ~90 jugadas con frases nuevas  🔍 pendientes
Escenarios: comercio, movimiento, combate, exploración, reglas, memoria, entradas raras (scratchpad `t_explora.py`;
repetidos en serie para descartar artefactos de carga). Confirmados en serie:
- GRAVE: regatear ("¿Me la dejas en 5 monedas?") COMPRA a 10; "¿Cuánto cuesta?" → `comprar` y repite la pregunta.
- GRAVE: eco — el narrador copia su narración anterior (combate: "el goblin cae inconsciente… recoges 50 monedas"
  repetido 3 jugadas, con el oro sin cambiar; "Me duermo" = respuesta a "asdfgh").
- GRAVE: "Recojo lo que haya dejado el goblin" → oro 15→65 pero el mensaje dice "No hay 'cofre' aquí".
- GRAVE: preguntas que crean contenido ("¿Encontré algo?" → `explorar` → WorldBuilder crea una llave);
  "Miro a mi alrededor" → `explorar` → crea un pasadizo (jugar.py).
- Narración que contradice el estado: "Lanzo la espada al fuego" (la narra, sigue en el inventario, fuego en la
  plaza); "¿Qué hora es?" → "Es mañana… luz del atardecer"; poción con 20/20 se gasta ("Recuperas 8").
- NPC ausente: "Le pregunto a Goruk si me vio bailar" (en la plaza) → responde Elena.
- Movimiento: "Voy a la taberna" estando ahí → "No hay camino directo… desde la taberna"; "Vuelvo atrás" no
  se resuelve; "Voy a la plaza" estando ahí → "Llegas nuevamente".
- Reglas: inventa lo que no está en el SRD (beholder "rayos láser", condición envenenado); docs cortados a 700
  caracteres (aliento del dragón rojo no llega); traducciones: VD → "resistencia a la enfermedad", saving throw →
  "adivinanza"; descanso corto "no proporciona recuperación" (falso).
- Fragmentos tras los filtros ("¿Quieres disculparte con ella…?" sin contexto); erratas ("Recoljas", "Exames").
- jugar.py: "salir" mueve al jugador (solo "/salir" termina); "/srd" sin consulta devuelve una araña gigante.
- Latencia: 2–45 s por jugada en serie; 60–240 s con 7 partidas en paralelo (el "eco" también aumenta con carga).
Bien: compra/oro insuficiente, servicio de Bron, citas de diálogo, resumen y "¿qué hice primero?", rutas,
movimientos ilegales, "forja" → herrería, inglés, atacar a un NPC amistoso, enemigo inexistente.

## Arreglos de las pruebas exploratorias (15-oct)  ✅ (post hold-out; respaldos `proyecto_final_v3_pre_explora*.ipynb`)
Principio común: lo que tiene una respuesta exacta en el estado o el registro del mundo lo escribe el CÓDIGO
(como ya pasaba con estado y compras); el narrador queda para la ambientación y lo abierto.
- Regateo/precio ("¿Cuánto cuesta?", "¿Me la dejas en 5?") → conversación con el comerciante, nunca compra.
- Preguntas ("¿Encontré algo?") y "miro a mi alrededor" no disparan al WorldBuilder; "reviso lo que llevo" → estado.
- Acción sin herramienta: si la intención es atacar/recoger/curarse/soltar/comprar y la frase tiene ese verbo, la
  herramienta se ejecuta aunque el planner elija otra cosa ("Ataco al lobo" → "No hay ningún enemigo así aquí").
- Combate narrado por el código desde las tiradas (tirada vs CA, daño, PG de ambos); antes inventaba PG ("16/20").
- Herramienta nueva `drop_item` (soltar/tirar/lanzar), narrada por el código; poción con vida al máximo no se gasta.
- Eco: si la narración repite ≥50 % de las oraciones de una narración de la ventana, se reescribe sin historial.
- "Llegas/entras/sales" se quitan si no hubo movimiento; "Ya estás en X"; destino desconocido → "No conoces ese
  lugar. Desde X puedes ir a: …"; sinónimos (forja→herrería, posada→taberna…); "vuelvo atrás".
- NPC nombrado que no está → "Goruk no está aquí (lo encuentras en taberna)" (antes respondía/robaba Elena).
- Memoria factual por código: rutas (shortest_path), "¿puedo volver a ese sitio?", compras y servicios ("¿quién me
  afiló la espada?"), lugares descubiertos, "¿encontré algo?" (lo creado en la jugada anterior), quién dijo qué
  (o "No recuerdo que nadie te dijera eso"), dónde estaba un objeto. Resúmenes y preguntas abiertas → narrador.
- Reglas: abstención si no hay cita verificable ("No encontré eso en las reglas oficiales"); documentos a 1500
  caracteres; citas comparadas sin signos/markdown (tablas de cobertura); glosario (VD, tirada de salvación, dados de
  golpe); respuesta en inglés → se pide de nuevo en español; seguimiento con el documento CITADO antes.
- Detector de seguimiento ("¿Hay un máximo?" continúa; "¿Qué pasa si estoy envenenado?" no) con el modelo del
  vigilante (72B): 7B 8-10/20, 72B 19/20 (~0.5 s; solo pregunta corta tras otra pregunta).
- Ambiente con el momento del día; erratas frecuentes del 7B corregidas ("Recoljas" → "Recoges"); jugar.py: "salir"
  termina, /srd sin consulta muestra el uso.
Limitaciones que siguen: el SRD 5.1 cargado no tiene condiciones (envenenado responde con un veneno concreto);
resúmenes y "¿qué fue lo más importante?" siguen con el narrador (a veces flojos); el DialogueAgent a veces dice
cosas raras ("No busques al tabernero, que aquí no lo hay"); latencia 2–60 s por jugada.
- Ronda final: si el jugador nombra a un NPC, solo contesta ese (un NPC creado en la herrería se metía en la charla
  con Bron); nombres de objetos creados sin "_"; "No llevas eso" sin duplicar; "Busco una puerta trasera" → explorar.
Verificación final: 8 escenarios (~100 jugadas), secuencias hold-out 3 y hold-out 2 completas, 52 frases del
clasificador (50/52, igual que antes), 17 seguimientos (16/17), pruebas dirigidas (`pruebas/t_ronda4.py`, `t_ronda5.py`,
`t_memoria.py`). Scripts y resultados en `pruebas/`.
