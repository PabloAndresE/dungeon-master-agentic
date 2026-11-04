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


# ── #1: pregunta_dialogo solo si pregunta por lo que alguien DIJO; si no, es memoria ──
rep("graph-v2", '''- pregunta_memoria: pregunta por el PASADO o el mapa: qué lugares descubrió, resumen, cómo llegar a un lugar''',
    '''- pregunta_memoria: pregunta por el PASADO o el mapa: qué lugares descubrió, resumen o "cuéntame la aventura",
  quién HIZO algo ("¿quién me afiló la espada?"), cómo llegar a un lugar, si puede volver a un sitio''')
rep("graph-v2", '''"le pido un vaso de agua al tabernero" → hablar · "¿qué historias me cuenta Bron?" → hablar"""''',
    '''"le pido un vaso de agua al tabernero" → hablar · "¿qué historias me cuenta Bron?" → hablar ·
"¿quién me afiló la espada?" → pregunta_memoria · "cuéntame la aventura completa" → pregunta_memoria ·
"¿puedo volver a ese sitio?" → pregunta_memoria (preguntar si puede ir no es ir)"""''')
rep("graph-v2", '''    if _intent("pregunta_dialogo") and not re.search(r"\\b(dijo|dijeron|conto|respondio|contesto|menciono|explico)\\b",
                                                     _norm(accion)) and _npc_aqui(accion):
        INTENCION["tipo"] = "hablar"  # "¿qué aventuras me menciona Goruk?" (presente, Goruk está aquí) → conversar''',
    '''    if _intent("pregunta_dialogo") and not re.search(VERBOS_DECIR, _norm(accion)):
        # "¿qué aventuras me menciona Goruk?" (presente, Goruk está aquí) → conversar;
        # "¿quién me afiló la espada?" / "cuéntame la aventura" no preguntan qué DIJO alguien → memoria
        INTENCION["tipo"] = "hablar" if _npc_aqui(accion) else "pregunta_memoria"
    if _intent("mover") and accion.strip().startswith("¿"):
        INTENCION["tipo"] = "pregunta_memoria"  # "¿Puedo volver a ese sitio?" pregunta, no mueve (hold-out 3)''')
rep("graph-v2", '''def clasificar_node(state: AgentState):''',
    '''VERBOS_DECIR = r"\\b(dijo|dijeron|conto|contaron|respondio|contesto|menciono|explico|advirtio|ofrecio|recomendo|aconsejo|pidio|hablo)\\b"


def clasificar_node(state: AgentState):''')
# el diálogo que se cita es el que corresponde a la pregunta (NPC nombrado o tema), no siempre el último
rep("graph-v2", '''    if _intent("pregunta_dialogo") \\
            and game_state.get("dialogos"):
        # "¿Qué me respondió?": la frase literal que quedó registrada (no la reconstruye el LLM)
        d = game_state["dialogos"][-1]''', '''    d = _dialogo_pedido(_accion(state)) if _intent("pregunta_dialogo") else None
    if d:
        # "¿Qué me respondió?": la frase literal que quedó registrada (no la reconstruye el LLM)''')
rep("graph-v2", '''def narrar_node(state: AgentState):''', '''def _dialogo_pedido(accion):
    """Diálogo registrado al que se refiere la pregunta: el del NPC nombrado; si no nombra a nadie, el que comparte
    el tema ("¿quién me advirtió del bosque?"); "¿qué me dijo?" sin más → el último. Si ninguno corresponde,
    None (responde la memoria; antes se citaba siempre el último diálogo, fuera cual fuera la pregunta)."""
    dialogos = game_state.get("dialogos", [])
    a = _norm(accion)
    nombrados = [d for d in dialogos if any(w in a.split() for w in _norm(d["npc"]).split() if len(w) >= 4)]
    if nombrados:
        return nombrados[-1]
    temas = {w for w in re.findall(r"[a-z]{5,}", a)} - {"quien", "dijeron", "menciono", "advirtio", "conto", "ofrecio",
                                                         "respondio", "contesto", "explico", "recomendo", "aconsejo"}
    con_tema = [d for d in dialogos if temas & set(re.findall(r"[a-z]{5,}", _norm(d["dijo"])))]
    if con_tema:
        return con_tema[-1]
    if dialogos and not temas and not a.startswith("quien"):
        return dialogos[-1]
    return None


def narrar_node(state: AgentState):''')

# ── #2: "Entro en lo que haya encontrado" → el lugar recién descubierto conectado al actual ──
rep("graph-v2", '''def _location_in(text):''', '''REFERENCIA_DESCUBIERTO = re.compile(r"lo que (haya|he|hemos|acabo de)? ?(encontrado|descubierto|hallado|visto)|"
                                    r"\\b(eso|ahi|alli|ese (sitio|lugar|pasaje|pasadizo)|lo (nuevo|descubierto|encontrado))\\b")


def _destino_referido(text):
    """'Entro en lo que haya encontrado' no nombra el lugar: se resuelve al lugar DINÁMICO más reciente conectado
    a la ubicación actual (hold-out 3: el jugador se quedaba en la cueva y el narrador inventaba un cofre)."""
    if not REFERENCIA_DESCUBIERTO.search(_norm(text)):
        return None
    conexiones = world["locations"][game_state["location"]]["connections"]
    dinamicos = [c for c in conexiones if world["locations"][c].get("dynamic")]
    return max(dinamicos, key=lambda c: world["locations"][c]["created_turn"]) if dinamicos else None


def _location_in(text):''')
rep("graph-v2", '''    destino = _location_in(accion)
    if (paso.accion == "responder" and not previos and destino and not no_mueve''',
    '''    destino = _location_in(accion) or (_destino_referido(accion) if _intent("mover") else None)
    if (paso.accion in ("responder", "ver_estado") and not previos and destino and not no_mueve''')
rep("graph-v2", '''        nombrado = _location_in(_accion(state))
        destino = nombrado''', '''        nombrado = _location_in(_accion(state)) or _destino_referido(_accion(state))
        destino = nombrado''')
# la pregunta "¿puedo volver a…?" se responde con las conexiones reales
rep("graph-v2", '''    if _intent("pregunta_memoria"):
        obs += [f"- grafo: {l}" for l in memoria.splitlines() if l.startswith(("Ruta más corta", "No hay ruta"))]''',
    '''    if _intent("pregunta_memoria"):
        obs += [f"- grafo: {l}" for l in memoria.splitlines() if l.startswith(("Ruta más corta", "No hay ruta"))]
        obs += [f"- mapa: desde {game_state['location']} se puede ir a: "
                f"{', '.join(world['locations'][game_state['location']]['connections'])}"]''')

# ── #3: reglas — temperatura 0, todos los límites del texto, nada que no esté (mínimos inventados) ──
rep("graph-v2", '''llm_planner = ChatOllama(''', '''llm_reglas = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)  # v3: reglas sin variación
llm_planner = ChatOllama(''')
rep("graph-v2", '''Traduce al español y responde en 1-3 oraciones con las cifras exactas. No describas ningún lugar ni
escena, no menciones al jugador ni a personajes, no agregues nada que no esté en el texto."""''',
    '''Traduce al español y responde en 1-3 oraciones con las cifras exactas, incluidos los LÍMITES que diga el texto
("to a maximum of 20d6" → "hasta un máximo de 20d6"). No inventes mínimos, máximos ni excepciones que no estén.
No describas ningún lugar ni escena, no menciones al jugador ni a personajes, no agregues nada que no esté en el texto."""''')
rep("graph-v2", '''        texto = llm_narrador.invoke([SystemMessage(content=SYSTEM_SOLO_REGLAS), HumanMessage(
            content=f"TEXTO OFICIAL:\\n{chr(10).join(srd_jugada)[:3000] or '(no se encontró)'}\\n\\nPregunta: {_accion(state)}")]).content''',
    '''        fuente = chr(10).join(srd_jugada)[:3000]
        mensajes_r = [SystemMessage(content=SYSTEM_SOLO_REGLAS), HumanMessage(
            content=f"TEXTO OFICIAL:\\n{fuente or '(no se encontró)'}\\n\\nPregunta: {_accion(state)}")]
        texto = llm_reglas.invoke(mensajes_r).content
        # Chequeo con el texto oficial: dados que no aparecen, un "mínimo" que el texto no dice, 
        fuente_n = _norm(fuente)
        malos = [x for x in re.findall(r"\\d+d\\d+", _norm(texto)) if x not in fuente_n]
        if "minim" in _norm(texto) and "minimum" not in fuente_n:
            malos.append("un mínimo que el texto no dice")
        if malos:
            texto = llm_reglas.invoke(mensajes_r + [AIMessage(content=texto), HumanMessage(content=(
                f"Revisa contra el TEXTO OFICIAL: tu respuesta incluye {', '.join(malos)}. "
                "Corrige la respuesta (traducción fiel, sin agregar nada)."))]).content''')

for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
