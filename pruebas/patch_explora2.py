"""v3 — segunda ronda de las pruebas exploratorias."""
exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())

# ── A. "seguimiento" lo decide el clasificador (contar palabras fallaba: "¿Qué pasa si estoy envenenado?") ──
rep("graph-v2", '''class IntencionJugador(BaseModel):
    tipo: Literal[''', '''class IntencionJugador(BaseModel):
    seguimiento: bool = Field(description=(
        "true SOLO si la frase NO se entiende sola y continúa la jugada anterior ('¿Hay un máximo?', '¿Y su aliento?', "
        "'¿Cuáles son?', '¿Cuánto le pagué?'); false si nombra su propio tema ('¿Qué pasa si estoy envenenado?')"))
    tipo: Literal[''')
rep("graph-v2", '''        INTENCION["tipo"] = clasificador_intencion.invoke([SystemMessage(content=SYSTEM_INTENCION), HumanMessage(
            content=f"Jugador (está en {game_state['location']}): {_accion(state)}")]).tipo''',
    '''        humanas = [m.content for m in state["messages"] if isinstance(m, HumanMessage)]
        r_int = clasificador_intencion.invoke([SystemMessage(content=SYSTEM_INTENCION), HumanMessage(
            content=f"Jugada anterior: {humanas[-2] if len(humanas) > 1 else '(ninguna)'}\\n"
                    f"Jugador (está en {game_state['location']}): {_accion(state)}")])
        INTENCION["tipo"], INTENCION["seguimiento"] = r_int.tipo, r_int.seguimiento''')
rep("graph-v2", '''    except Exception:
        INTENCION["tipo"] = "otra"
    accion = _accion(state)''', '''    except Exception:
        INTENCION["tipo"], INTENCION["seguimiento"] = "otra", False
    accion = _accion(state)''')
rep("graph-v2", '''    a = accion.strip()
    return a.startswith("¿") and (len(re.findall(r"\\w+", a)) <= 5 or bool(re.match(r"^\\W*y\\b", _norm(a))))''',
    '''    a = accion.strip()
    return a.startswith("¿") and len(re.findall(r"\\w+", a)) <= 8 and (
        INTENCION.get("seguimiento", False) or bool(re.match(r"^\\W*y\\b", _norm(a))))''')
rep("graph-v2", '''INTENCION = {"tipo": "otra"}''', '''INTENCION = {"tipo": "otra", "seguimiento": False}''')

# ── B. Si la intención es una acción de juego y el planner no la eligió, se ejecuta igual (la herramienta valida) ──
rep("graph-v2", '''    if _intent("soltar") and not previos and paso.accion != "soltar":
        paso = Paso(intencion="accion", pensamiento=paso.pensamiento, accion="soltar", argumento=accion)''',
    '''    for tipo_ in ("soltar", "atacar", "recoger", "curarse"):
        # "Ataco al lobo" → el planner miraba el estado y el narrador inventaba la pelea; ahora la herramienta
        # responde ("No hay ningún enemigo así aquí") y la narración no puede contradecirla
        if _intent(tipo_) and not previos and paso.accion != tipo_:
            paso = Paso(intencion="accion", pensamiento=paso.pensamiento, accion=tipo_, argumento=accion)''')
rep("tools-v2", '''    for npc in npcs_here:
        if enemy_name.lower() in npc.lower():
            enemy = npc
            break
    if not enemy:
        return f"No hay enemigo '{enemy_name}' aqui. NPCs: {npcs_here or 'nadie'}"''',
    '''    pedido = _norm_txt(enemy_name)
    for npc in npcs_here:  # "goblin", "Goblin centinela" o "ataco al goblin" → Goblin centinela
        if pedido in _norm_txt(npc) or any(w in pedido.split() for w in _norm_txt(npc).split() if len(w) >= 4):
            enemy = npc
            break
    if not enemy:
        return f"No hay ningun enemigo asi aqui. Presentes: {npcs_here or 'nadie'}"''')
rep("tools-v2", '''        parecidos = [i for i in available_lower if item and (item in i or i in item)]''',
    '''        parecidos = [i for i in available_lower if item and (item in i or i in item)] or \\
                    [i for i in available_lower if any(w in item.split() for w in i.split() if len(w) >= 5)]''')
# _norm_txt se usa en attack_enemy, que está antes de drop_item: se define arriba de todo
s = get("tools-v2")
s = s.replace('''def _norm_txt(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode().strip()


''', "")
i = s.index("@tool")
s = s[:i] + '''def _norm_txt(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode().strip()


''' + s[i:]
put("tools-v2", s)

# ── C. Combate narrado por el código desde las tiradas reales (el narrador inventaba PG: "16/20", "cae inconsciente") ──
rep("graph-v2", '''    libre = not solo_dialogo and not fallidas and not hechas and not no_ejecutadas''',
    '''    combate = [o for p, o in state.get("pasos", []) if p.accion == "atacar" and o and "--- COMBATE vs" in o]
    if combate and not fallidas and not hechas:
        texto = " ".join(_narrar_combate(o) for o in combate)
    libre = not solo_dialogo and not fallidas and not hechas and not no_ejecutadas and not combate''')
rep("graph-v2", '''def _repite(texto, previo, umbral=0.5):''', '''def _narrar_combate(obs):
    """Ronda de combate contada desde la observación de attack_enemy (como las compras: sin margen para inventar)."""
    enemigo = re.search(r"COMBATE vs (.+?) ---", obs).group(1)
    m = re.search(r"Tu ataque(?: con (.+?))?: d20=\\d+\\+\\d+=(\\d+) vs CA (\\d+) -> (CRÍTICO|ACIERTO|FALLO)"
                  r"(?:, (\\d+) de daño \\(PG de .+?: (\\d+)/(\\d+)\\))?", obs)
    arma, total, ca, res, dano, pg, pg_max = m.groups()
    t = f"Atacas a {enemigo}{f' con tu {arma}' if arma else ''} (tirada {total} contra CA {ca}): "
    t += (f"{'¡golpe crítico! ' if res == 'CRÍTICO' else '¡aciertas! '}Le haces {dano} de daño"
          f"{'' if 'derrotado' in obs else f' y le quedan {pg}/{pg_max} PG'}." if res != "FALLO" else "fallas.")
    if "ha sido derrotado" in obs:
        return t + f" ¡{enemigo} cae derrotado!"
    e = re.search(r"Ataque de .+?: d20=\\d+\\+\\d+=(\\d+) vs tu CA (\\d+) -> (ACIERTO|FALLO)(?:, (\\d+) de daño a ti)?", obs)
    if e:
        et, eca, eres, edano = e.groups()
        t += f" {enemigo} te ataca (tirada {et} contra tu CA {eca}): "
        t += f"te hace {edano} de daño." if eres == "ACIERTO" else "falla."
    if "Caes inconsciente" in obs:
        t += " ¡Caes inconsciente! Despiertas más tarde, maltrecho, con 1 PG."
    return t + f" Te quedan {game_state['hp']}/{game_state['max_hp']} PG."


def _repite(texto, previo, umbral=0.5):''')

# ── D. Eco contra TODAS las narraciones de la ventana (no solo la última) ──
rep("graph-v2", '''        previa_ai = next((m.content for m in reversed(state["messages"][:-1]) if isinstance(m, AIMessage)), "")
        if _repite(response.content, previa_ai):''',
    '''        previas_ai = [m.content for m in state["messages"][:-1] if isinstance(m, AIMessage)]
        if any(_repite(response.content, p_ai) for p_ai in previas_ai):''')

# ── E. NPC nombrado que no está aquí: no responde otro ──
rep("graph-v2", '''    if se_dirige and not npc_nombrado and len(presentes) == 1:''',
    '''    if se_dirige and not npc_nombrado and len(presentes) == 1 and not _npc_ausente(accion):''')
rep("graph-v2", '''def _npc_aqui(nombre):''', '''def _npc_ausente(texto):
    """NPC conocido que el jugador nombra pero que NO está en este lugar ("le pregunto a Goruk…" en la plaza)."""
    loc, t = game_state["location"], set(re.findall(r"[a-z]+", _norm(texto)))
    return next((n for n, d in world["npcs"].items() if d.get("location") != loc and n not in game_state["enemies_defeated"]
                 and any(w in t for w in _norm(n).split()[:1] if len(w) >= 4)), None)


def _npc_aqui(nombre):''')
rep("graph-v2", '''    if solo_dialogo:
        # Jugada que es solo conversación''', '''    ausente = _npc_ausente(_accion(state)) if _intent("hablar", "comprar") and not dialogos else None
    if ausente and not _npc_aqui(_accion(state)):
        lugar_n = world["npcs"][ausente].get("location", "otro lugar").replace("_", " ")
        texto = f"{ausente} no está aquí (lo encuentras en {lugar_n})."
        _log("narrar", observaciones=obs + [f"- NPC AUSENTE: {ausente}"], memoria_grafo=memoria)
        return {"messages": [AIMessage(content=f"{texto}\\n\\n{_state_summary()}")]}
    if _intent("mover") and not any(p.accion == "mover" for p, _ in state.get("pasos", [])) \\
            and _location_in(_accion(state)) == game_state["location"]:
        texto = f"Ya estás en {game_state['location'].replace('_', ' ')}."  # antes: "Llegas a la plaza" estando ahí
        _log("narrar", observaciones=obs, memoria_grafo=memoria)
        return {"messages": [AIMessage(content=f"{texto}\\n\\n{_state_summary()}")]}
    if solo_dialogo:
        # Jugada que es solo conversación''')

# ── F. Movimiento: sinónimos de lugares y "vuelvo atrás" ──
rep("graph-v2", '''def _location_in(text):
    """Ubicación conocida mencionada en el texto del jugador (sin acentos), o None."""
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    hits = [k for k in world["locations"] if re.search(rf"\\b{re.escape(k.replace('_', ' '))}\\b", t.replace("_", " "))]''',
    '''ALIAS_LUGARES = {"forja": "herreria", "herrero": "herreria", "bar": "taberna", "posada": "taberna", "meson": "taberna",
                 "mercado": "plaza", "fuente": "plaza", "arboleda": "bosque", "caverna": "cueva", "gruta": "cueva"}


def _location_in(text):
    """Ubicación conocida mencionada en el texto del jugador (sin acentos), o None. Acepta sinónimos ("la forja")."""
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    hits = [k for k in world["locations"] if re.search(rf"\\b{re.escape(k.replace('_', ' '))}\\b", t.replace("_", " "))]
    hits += [v for a, v in ALIAS_LUGARES.items() if v in world["locations"] and re.search(rf"\\b{a}\\b", t)]''')
rep("graph-v2", '''    if not REFERENCIA_DESCUBIERTO.search(_norm(text)):
        return None''', '''    if re.search(r"\\b(atras|de donde vine|donde estaba antes|lugar anterior)\\b", _norm(text)):
        anterior = game_state.get("ubicacion_anterior")  # "Vuelvo atrás"
        return anterior if anterior in world["locations"][game_state["location"]]["connections"] else None
    if not REFERENCIA_DESCUBIERTO.search(_norm(text)):
        return None''')
rep("graph-v2", '''    if paso.accion == "mover" and game_state["location"] != antes:  # una imagen por ESCENA: cada llegada a un lugar''',
    '''    if paso.accion == "mover" and game_state["location"] != antes:
        game_state["ubicacion_anterior"] = antes  # para "vuelvo atrás"
    if paso.accion == "mover" and game_state["location"] != antes:  # una imagen por ESCENA: cada llegada a un lugar''')

for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
