"""v3 — tercera ronda: memoria factual, reglas (seguimiento con los docs anteriores, citas con tablas), regresiones."""
exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())

# ── 1. Forzar la acción solo si la frase tiene un verbo de esa acción (si no, amplifica errores del clasificador) ──
rep("graph-v2", '''        if _intent(tipo_) and not previos and paso.accion != tipo_:''',
    '''        if _intent(tipo_) and not previos and paso.accion != tipo_ and re.search(VERBOS_ACCION[tipo_], _norm(accion)):''')
rep("graph-v2", '''def _comerciante_aqui():''', '''VERBOS_ACCION = {"atacar": r"\\b(atac|ataco|golpe|luch|pele|embist|apunal|arreo|pego|me lanzo contra)",
                 "recoger": r"\\b(recoj|recog|cojo|coger|tomo|agarr|guardo|levant|me llevo)",
                 "curarse": r"\\b(bebo|tomo|uso|me curo|curarme)", "soltar": r"\\b(tiro|lanzo|dejo|suelto|arrojo|me deshago)"}
REVISAR_INVENTARIO = re.compile(r"^(revis\\w*|miro|chequeo) (todo )?(mi|mis|lo que llevo|el equipo|el inventario)\\b|^(que|cuanto) llevo")


def _comerciante_aqui():''')
rep("graph-v2", '''    if _intent("explorar") and accion.strip().startswith("¿"):''',
    '''    if REVISAR_INVENTARIO.search(_norm(accion).strip(" ¿?.")):
        INTENCION["tipo"] = "pregunta_estado"  # "Reviso lo que llevo / todo mi equipo" (salía recoger o explorar)
    if _intent("explorar") and accion.strip().startswith("¿"):''')
# palabras sin puntuación ("goblin." no coincidía con "goblin")
rep("tools-v2", '''        if pedido in _norm_txt(npc) or any(w in pedido.split() for w in _norm_txt(npc).split() if len(w) >= 4):''',
    '''        if pedido in _norm_txt(npc) or any(w in re.findall(r"[a-z]+", pedido) for w in _norm_txt(npc).split() if len(w) >= 4):''')
rep("tools-v2", '''                    [i for i in available_lower if any(w in item.split() for w in i.split() if len(w) >= 5)]
        if len(parecidos) != 1:
            return f"No hay '{item}' aqui. Objetos disponibles: {available or 'ninguno'}"''',
    '''                    [i for i in available_lower if any(w in re.findall(r"[a-z]+", _norm_txt(item)) for w in _norm_txt(i).split()
                                                       if len(w) >= 5)]
        if len(parecidos) != 1:
            llevo = [i for i in game_state["inventory"] if any(w in re.findall(r"[a-z]+", _norm_txt(item))
                                                               for w in _norm_txt(i).split() if len(w) >= 5)]
            if llevo:
                return f"Ya llevas {llevo[0]}."
            return f"No hay eso aqui. Objetos disponibles: {available or 'ninguno'}"''')
rep("tools-v2", '''    cand = [i for i in inv if pedido and (pedido in _norm_txt(i) or any(w in pedido.split() for w in _norm_txt(i).split()''',
    '''    cand = [i for i in inv if pedido and (pedido in _norm_txt(i) or any(w in re.findall(r"[a-z]+", pedido) for w in _norm_txt(i).split()''')
rep("tools-v2", '''        return f"Aqui nadie vende nada. NPCs: {world['locations'][loc]['npcs'] or 'nadie'}"''',
    '''        return f"NO SE COMPRO: aqui nadie vende nada. NPCs: {world['locations'][loc]['npcs'] or 'nadie'}"''')

# ── 2. Memoria factual: lo que tiene respuesta exacta en el registro del mundo lo responde el código ──
rep("graph-v2", '''def narrar_node(state: AgentState):''', '''def _ruta(destino):
    lugares = nx.Graph([(a, b) for a, d in world["locations"].items() for b in d["connections"]])
    try:
        return nx.shortest_path(lugares, game_state["location"], destino)
    except Exception:
        return None


def respuesta_memoria(accion, seguimiento=False):
    """Preguntas de memoria con respuesta exacta (rutas, "¿puedo volver?", compras, lugares descubiertos, "¿encontré
    algo?", quién dijo qué, dónde estaba un objeto): las responde el código desde el registro del mundo. El narrador
    las respondía con contradicciones ("Goruk… Bron te afiló la espada") o inventaba ("un cofre oculto").
    Devuelve None si la pregunta no es de ese tipo (resúmenes, "¿qué hice primero?" → narrador)."""
    a, loc = _norm(accion), game_state["location"]
    nom = lambda k: k.replace("_", " ")
    if re.search(r"\\bpuedo (volver|ir|regresar|llegar)\\b", a):
        dest = _location_in(accion)
        if not dest and re.search(r"\\b(ese|esa|ahi|alli|nuevo|descubiert|encontr)", a):
            din = [k for k, v in world["locations"].items() if v.get("dynamic")]
            dest = max(din, key=lambda k: world["locations"][k]["created_turn"]) if din else None
        if dest:
            if dest == loc:
                return f"Ya estás en {nom(dest)}."
            r = _ruta(dest)
            if r and len(r) == 2:
                return f"Sí: desde {nom(loc)} puedes ir directamente a {nom(dest)}."
            return f"Sí, pero no directamente: {' → '.join(map(nom, r))}." if r else f"No conoces un camino a {nom(dest)}."
    if PREGUNTA_RUTA.search(accion) or re.search(r"lugares (cruzo|atravieso|paso|recorro)|por donde paso", a):
        dest = _location_in(accion) or game_state.get("ultima_ruta")
        if dest and dest != loc and _ruta(dest):
            game_state["ultima_ruta"] = dest
            return f"La ruta más corta de {nom(loc)} a {nom(dest)} es: {' → '.join(map(nom, _ruta(dest)))}."
    compras = [m for m in (re.match(r"Compro (.+?) a (.+?) por (\\d+) de oro", e) for e in game_state["events"]) if m]
    if re.search(r"\\b(compr\\w*|pague|pagaste|gaste|gastaste|afil\\w*|vend\\w*|cobr\\w*)\\b", a):
        tema = [m for m in compras if any(w[:4] in a for w in _norm(m.group(1)).split() if len(w) >= 4)]
        lista = tema or ([compras[i] for i in game_state.get("_ultimas_compras", []) if i < len(compras)]
                         if seguimiento else []) or compras
        game_state["_ultimas_compras"] = [compras.index(m) for m in lista]
        if not lista:
            return "No has comprado ni pagado nada todavía."
        return " ".join(f"Le pagaste {m.group(3)} de oro a {m.group(2)} por {m.group(1).replace('afilar espada', 'afilar tu espada')}."
                        for m in lista)
    din = sorted([k for k, v in world["locations"].items() if v.get("dynamic")], key=lambda k: world["locations"][k]["created_turn"])
    if re.search(r"(sitios|lugares) (nuevos|descubiert|que (descubri|encontre|conoci))|cuantos (sitios|lugares)", a) or (
            seguimiento and re.search(r"cuales son|cuantos son|cuantos hay", a) and game_state.get("_ultima_memoria") == "lugares"):
        game_state["_ultima_memoria"] = "lugares"
        if not din:
            return "Todavía no descubriste lugares nuevos."
        return (f"Descubriste {len(din)} lugar{'es' if len(din) > 1 else ''} nuevo{'s' if len(din) > 1 else ''}: " +
                "; ".join(f"{nom(k)} (se llega desde {nom(world['locations'][k]['connections'][0])})" for k in din) + ".")
    if re.search(r"\\b(encontre|descubri|halle)\\b.*\\balgo\\b", a):
        t = game_state["turn"] - 1
        cosas = ([f"un lugar nuevo: {nom(k)}" for k, v in world["locations"].items() if v.get("dynamic") and v["created_turn"] == t] +
                 [k for k, v in world["items"].items() if v.get("dynamic") and v.get("created_turn") == t] +
                 [f"a {k}" for k, v in world["npcs"].items() if v.get("dynamic") and v.get("created_turn") == t])
        return ("Sí: encontraste " + ", ".join(cosas) + ".") if cosas else "No, no encontraste nada nuevo."
    if re.search(VERBOS_DECIR, a):
        d = _dialogo_pedido(accion)
        if d:
            return f'{d["npc"]} te dijo: "{d["dijo"]}"'
        if re.match(r"\\W*quien", a):
            return "No recuerdo que nadie te dijera eso."
    m = re.search(r"donde (estaba|estaban|encontre|halle|recogi) (.+)", a)
    if m:
        obj = next((k for k in world["items"] if any(w in re.findall(r"[a-z]+", m.group(2))
                                                     for w in _norm(k).split() if len(w) >= 4)), None)
        if obj and world["items"][obj].get("location"):
            return f"{obj[0].upper() + obj[1:]} estaba{'n' if obj.endswith('s') else ''} en {nom(world['items'][obj]['location'])}."
    return None


def _corregir_erratas(t):
    for mal, bien in {"Recoljas": "Recoges", "Recolgas": "Recoges", "Recolijes": "Recoges", "Recoljes": "Recoges",
                      "Exames": "Examinas", "Entra en la": "Entras en la"}.items():
        t = t.replace(mal, bien)
    return t


def narrar_node(state: AgentState):''')
rep("graph-v2", '''    if _intent("pregunta_estado") and not dialogos:
        # Pregunta de ESTADO''', '''    if _intent("pregunta_memoria", "pregunta_dialogo") and not dialogos:
        memoria_f = respuesta_memoria(_accion(state), INTENCION.get("seguimiento", False))
        if memoria_f:
            _log("narrar", observaciones=obs + [f"- RESPUESTA DE MEMORIA (código): {memoria_f}"], memoria_grafo=memoria)
            return {"messages": [AIMessage(content=f"{memoria_f}\\n\\n{_state_summary()}")]}
    if _intent("pregunta_estado") and not dialogos:
        # Pregunta de ESTADO''')

# ── 3. Reglas: el seguimiento usa los MISMOS documentos de la pregunta anterior (no busca de nuevo); citas con tablas ──
rep("graph-v2", '''    if paso.accion == "reglas" and ult and ult["jugada"] == game_state["turn"] - 1 and _seguimiento_corto(accion):
        # "¿Hay un máximo?" / "¿Cuánto daño hacen sus garras?": seguimiento corto → se busca con la pregunta anterior
        paso = Paso(intencion="pregunta", pensamiento=paso.pensamiento, accion="reglas", argumento=_consulta_grafo(state))''',
    '''    if paso.accion == "reglas" and ult and ult["jugada"] == game_state["turn"] - 1 and _seguimiento_corto(accion):
        # "¿Hay un máximo?", "¿Y su aliento?": se responde con los documentos de la pregunta anterior (buscar de nuevo con
        # la pregunta combinada traía otra regla y la respuesta se contradecía: "No hay un máximo")
        paso = Paso(intencion="pregunta", pensamiento=paso.pensamiento, accion="ver_estado", argumento="")''')
rep("graph-v2", '''    if not srd_jugada and ult and ult["jugada"] == game_state["turn"] - 1:   # seguimiento de una pregunta de reglas
        srd_jugada = ["\\n".join(f"[{d}] {srd_docs[d]['text'][:1500]}" for d in ult["docs"])]''',
    '''    if not srd_jugada and ult and ult["jugada"] == game_state["turn"] - 1:   # seguimiento de una pregunta de reglas
        srd_jugada = ["\\n".join(f"[{d}] {srd_docs[d]['text'][:1500]}" for d in ult["docs"])]
        if _intent("pregunta_reglas"):
            ult["jugada"] = game_state["turn"]  # una cadena de seguimientos ("¿Y su aliento?" → "¿Y su mordisco?") sigue''')
s = get("graph-v2")
n = s.count('re.sub(r"\\s+", " ", _norm(c)).strip(" .") in fuente_n')
assert n == 2, n
s = s.replace('re.sub(r"\\s+", " ", _norm(c)).strip(" .") in fuente_n', '_plano(c) in _plano(fuente)')
s = s.replace('''def _ruta(destino):''', '''def _plano(t):
    """Texto sin signos ni markdown (tablas "| Half cover |", "**", "***"): para verificar citas literales."""
    return re.sub(r"[^a-z0-9]+", " ", _norm(t)).strip()


def _ruta(destino):''')
put("graph-v2", s)

# ── 4. soltar narrado por el código; erratas; "llegas" sin haberse movido ──
rep("graph-v2", '''    if combate and not fallidas and not hechas:
        texto = " ".join(_narrar_combate(o) for o in combate)''',
    '''    if combate and not fallidas and not hechas:
        texto = " ".join(_narrar_combate(o) for o in combate)
    soltados = [re.search(r"Soltaste: (.+?)\\. Queda en (.+?)\\.", o) for p, o in state.get("pasos", [])
                if p.accion == "soltar" and o and o.startswith("Soltaste")]
    if soltados and not combate:  # el narrador "derretía" la espada en un fuego que no existía
        texto = " ".join(f"Sueltas {m.group(1)}: queda en el suelo ({m.group(2).replace('_', ' ')})." for m in soltados if m)
    combate = combate or soltados''')
rep("graph-v2", '''    fallidas = [o.split("NO SE COMPRO:", 1)[1]''', '''    texto = _corregir_erratas(texto)
    fallidas = [o.split("NO SE COMPRO:", 1)[1]''')
rep("graph-v2", '''        for linea_d in _discoveries_this_turn():  # lo recién creado no puede quedar fuera de la narración''',
    '''        if not any(p_.accion == "mover" and o_ and o_.startswith("MOVIMIENTO EXITOSO") for p_, o_ in state.get("pasos", [])):
            # sin movimiento no se "llega" a ningún lado (lo narraba al examinar o con texto sin sentido)
            texto = " ".join(f for f in re.split(r"(?<=[.!?])\\s+", texto)
                             if not re.match(r"(llegas|entras|sales|regresas|vuelves|te diriges)\\b", _norm(f))).strip()
        for linea_d in _discoveries_this_turn():  # lo recién creado no puede quedar fuera de la narración''')

for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
