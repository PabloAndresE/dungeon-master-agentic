"""v3 — arreglos de las pruebas exploratorias (15-oct): regateo, eco, recoger, preguntas que crean, soltar, momento, poción, reglas."""
exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())

# ── 1. Regatear / preguntar el precio NO es comprar ──
rep("graph-v2", '''    previa = game_state.get("_intencion_previa")''',
    '''    if _intent("comprar") and re.search(REGATEO, _norm(accion)):
        # "¿Cuánto cuesta?", "¿Me la dejas en 5?": se conversa con el comerciante; comprar solo si lo pide
        INTENCION["tipo"] = "hablar" if _npc_aqui(accion) or _comerciante_aqui() else "pregunta_estado"
    if _intent("explorar") and accion.strip().startswith("¿"):
        INTENCION["tipo"] = "pregunta_memoria"  # "¿Encontré algo?" pregunta por lo que pasó: no crea contenido
    if _intent("explorar") and MIRAR_ALREDEDOR.match(_norm(accion).strip(" .!")):
        INTENCION["tipo"] = "otra"  # "Miro a mi alrededor" describe el lugar; buscar/examinar sí puede descubrir
    previa = game_state.get("_intencion_previa")''')
rep("graph-v2", '''def _seguimiento_corto(accion):''', '''REGATEO = (r"cuanto (cuesta|vale|cobras|sale|pides)|\\bprecio\\b|me (la|lo) (dejas|das) (en|por)|rebaja|descuento|"
           r"mas barat|regate")
MIRAR_ALREDEDOR = re.compile(r"^(miro|echo (un vistazo|una mirada|una ojeada)|observo|contemplo)( (a mi )?alrededor| el lugar|"
                             r" por (la|el) \\w+| (la|el) \\w+| a mi alrededor en (la|el) \\w+)?$")


def _comerciante_aqui():
    loc = game_state["location"]
    return next((n for n in world["locations"][loc]["npcs"] if world["npcs"].get(n, {}).get("vende")
                 and n not in game_state["enemies_defeated"]), None)


def _seguimiento_corto(accion):''')
rep("graph-v2", '''"¿puedo volver a ese sitio?" → pregunta_memoria (preguntar si puede ir no es ir)"""''',
    '''"¿puedo volver a ese sitio?" → pregunta_memoria (preguntar si puede ir no es ir) ·
"¿cuánto cuesta la poción?" → hablar (preguntar el precio no es comprar) · "tiro la antorcha" → soltar"""''')
# "hablar" con el comerciante cuando no lo nombra: ya lo cubre "un solo NPC presente" en pensar

# ── 2. Eco: el narrador copiaba su narración anterior ──
rep("graph-v2", '''        response = llm_narrador.invoke(mensajes)
        if re.search(r"[\\u3040-\\u30ff\\u4e00-\\u9fff\\uac00-\\ud7af]", response.content):''',
    '''        response = llm_narrador.invoke(mensajes)
        previa_ai = next((m.content for m in reversed(state["messages"][:-1]) if isinstance(m, AIMessage)), "")
        if _repite(response.content, previa_ai):
            # Eco: copió su narración anterior (pasaba en combate y con acciones sin herramienta). Se reescribe SIN
            # las jugadas previas en el contexto, solo con las observaciones de esta jugada.
            response = llm_narrador.invoke([SystemMessage(content=SYSTEM_NARRADOR), HumanMessage(
                content=f"Acción del jugador: {_accion(state)}\\n\\n{contexto}\\n\\nNarra SOLO lo que pasó en esta jugada.")])
        if re.search(r"[\\u3040-\\u30ff\\u4e00-\\u9fff\\uac00-\\ud7af]", response.content):''')
rep("graph-v2", '''def narrar_node(state: AgentState):''', '''def _repite(texto, previo, umbral=0.5):
    """¿La narración nueva repite la anterior? (fracción de sus oraciones que ya estaban, palabra por palabra)"""
    norm = lambda t: {re.sub(r"\\W+", " ", _norm(o)).strip() for o in re.split(r"(?<=[.!?])\\s+", t.split("[HP:")[0])
                      if len(o) > 25}
    nuevas, viejas = norm(texto), norm(previo)
    return bool(nuevas) and len(nuevas & viejas) / len(nuevas) >= umbral


def narrar_node(state: AgentState):''')

# ── 3. Un paso fallido no tapa uno exitoso de la misma acción ("recoger cofre" falla, "recoger cofre con 50…" sí) ──
rep("graph-v2", '''                     for p, o in state.get("pasos", [])
                     if p.accion in ("atacar", "recoger", "curarse") and o and "NO SE EJECUTÓ" in o]''',
    '''                     for p, o in state.get("pasos", [])
                     if p.accion in ("atacar", "recoger", "curarse", "soltar") and o and "NO SE EJECUTÓ" in o
                     and not any(p2.accion == p.accion and o2 and "NO SE EJECUTÓ" not in o2
                                 for p2, o2 in state.get("pasos", []))]''')
rep("tools-v2", '''    if item not in available_lower:
        return f"No hay '{item}' aqui. Objetos disponibles: {available or 'ninguno'}"''',
    '''    if item not in available_lower:  # v3: "tablero de ajedrez" → "viejo tablero de ajedrez" (si es uno solo)
        parecidos = [i for i in available_lower if item and (item in i or i in item)]
        if len(parecidos) != 1:
            return f"No hay '{item}' aqui. Objetos disponibles: {available or 'ninguno'}"
        item = parecidos[0]''')

# ── 4. (en 1) preguntas y "miro alrededor" no disparan al WorldBuilder ──

# ── 5a. soltar / tirar / lanzar un objeto: herramienta nueva (antes se narraba y el inventario no cambiaba) ──
rep("tools-v2", '''@tool
def use_potion() -> str:''', '''@tool
def drop_item(item_name: str) -> str:
    """Suelta, tira o lanza un objeto del inventario: queda en la ubicación actual."""
    pedido = _norm_txt(item_name)
    inv = game_state["inventory"]
    cand = [i for i in inv if pedido and (pedido in _norm_txt(i) or any(w in pedido.split() for w in _norm_txt(i).split()
                                                                       if len(w) >= 4))]
    if not cand:
        return f"No llevas '{item_name}'. Inventario: {inv}"
    obj = cand[0]
    inv.remove(obj)
    loc = game_state["location"]
    if obj in game_state["items_taken"]:
        game_state["items_taken"].remove(obj)
    if obj not in world["locations"][loc]["items"]:
        world["locations"][loc]["items"].append(obj)
    world["items"].setdefault(obj, {"description": obj, "location": loc})
    world["items"][obj].update(status="en el suelo", location=loc)
    game_state["events"].append(f"Solto: {obj} (en {loc})")
    return f"Soltaste: {obj}. Queda en {loc}. {_state_summary()}"


def _norm_txt(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode().strip()


@tool
def use_potion() -> str:''')
rep("graph-v2", '''    accion: Literal["ver_estado", "mover", "recoger", "atacar", "curarse", "hablar", "comprar",''',
    '''    accion: Literal["ver_estado", "mover", "recoger", "soltar", "atacar", "curarse", "hablar", "comprar",''')
rep("graph-v2", '''- recoger(objeto) · atacar(enemigo) · hablar(personaje) · curarse() con una poción · tirar_dados(notación)''',
    '''- recoger(objeto) · soltar(objeto): tira, deja o lanza algo que lleva · atacar(enemigo) · hablar(personaje)
- curarse() con una poción · tirar_dados(notación)''')
rep("graph-v2", '''            "reglas": (consultar_reglas, "consulta"), "comprar": (buy_item, "item_name")}''',
    '''            "reglas": (consultar_reglas, "consulta"), "comprar": (buy_item, "item_name"),
            "soltar": (drop_item, "item_name")}''')
rep("graph-v2", '''    requiere = {"recoger": "recoger", "atacar": "atacar", "curarse": "curarse", "comprar": "comprar"}''',
    '''    requiere = {"recoger": "recoger", "atacar": "atacar", "curarse": "curarse", "comprar": "comprar", "soltar": "soltar"}
    if _intent("soltar") and not previos and paso.accion != "soltar":
        paso = Paso(intencion="accion", pensamiento=paso.pensamiento, accion="soltar", argumento=accion)''')
rep("graph-v2", '''    tipo: Literal["mover", "explorar", "hablar", "comprar", "atacar", "recoger", "curarse",''',
    '''    tipo: Literal["mover", "explorar", "hablar", "comprar", "atacar", "recoger", "soltar", "curarse",''')
rep("graph-v2", '''- atacar: pelea, golpea, ataca a alguien · recoger: toma/agarra/guarda un objeto · curarse: bebe/usa una poción, se cura''',
    '''- atacar: pelea, golpea, ataca a alguien · recoger: toma/agarra/guarda un objeto · curarse: bebe/usa una poción, se cura
- soltar: tira, deja, lanza, arroja o se deshace de un objeto que LLEVA ("lanzo la espada al fuego", "dejo la antorcha")''')
rep("graph-v2", '''    if paso.accion in ("recoger", "curarse", "atacar", "comprar") and estado_despues == estado_antes:''',
    '''    if paso.accion in ("recoger", "curarse", "atacar", "comprar", "soltar") and estado_despues == estado_antes:''')

# ── 5b. la frase de ambiente respeta el momento del día ──
rep("graph-v2", '''            content=f"Lugar: {game_state['location']} — {world['locations'][game_state['location']]['description']}")]).content''',
    '''            content=f"Lugar: {game_state['location']} — {world['locations'][game_state['location']]['description']}\\n"
                    f"Momento del día: {game_state.get('momento', 'mañana')} (la luz debe corresponder a este momento)")]).content''')

# ── 5c. poción con la vida al máximo: no se gasta ──
rep("tools-v2", '''    heal = _roll("2d4+2")
    game_state["inventory"].remove("pocion de curacion")''', '''    if game_state["hp"] >= game_state["max_hp"]:  # v3: no se desperdicia
        return f"Ya tienes la vida al maximo ({game_state['hp']}/{game_state['max_hp']}): guardas la pocion."
    heal = _roll("2d4+2")
    game_state["inventory"].remove("pocion de curacion")''')

# ── 8. Reglas: abstención sin cita verificada, documentos más largos, glosario ──
rep("graph-v2", '''            texto = r.respuesta
        except Exception:
            citas, texto = [], llm_reglas.invoke(mensajes_r).content''', '''            texto = r.respuesta
        except Exception:
            citas, texto = [], ""
        if not citas:  # sin cita verificable en el texto oficial: abstenerse (antes inventaba: beholder, "envenenado")
            texto = "No encontré eso en las reglas oficiales que tengo (SRD 5.1)."''')
rep("graph-v2", '''        fuente = chr(10).join(srd_jugada)[:3000]''', '''        fuente = chr(10).join(srd_jugada)[:5000]''')
rep("graph-v2", '''        srd_jugada = ["\\n".join(f"[{d}] {srd_docs[d]['text'][:900]}" for d in ult["docs"])]''',
    '''        srd_jugada = ["\\n".join(f"[{d}] {srd_docs[d]['text'][:1500]}" for d in ult["docs"])]''')
rep("srd-v2", '''    return "REGLAS OFICIALES (SRD 5.1):\\n" + "\\n".join(f"[{d['id']}] {d['text'][:700]}" for d in docs)''',
    '''    # v3: 1500 caracteres (con 700 no llegaba el aliento del dragón rojo, en el carácter 1056)
    return "REGLAS OFICIALES (SRD 5.1):\\n" + "\\n".join(f"[{d['id']}] {d['text'][:1500]}" for d in docs)''')
rep("graph-v2", '''contundente, slashing = cortante, piercing = perforante."""''',
    '''contundente, slashing = cortante, piercing = perforante, saving throw = tirada de salvación, VD (challenge) = valor de
desafío, Hit Dice = dados de golpe, short/long rest = descanso corto/largo."""''')

for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
