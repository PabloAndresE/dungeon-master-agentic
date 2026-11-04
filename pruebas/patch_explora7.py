"""v3 — cuarta ronda: seguimiento de reglas con el documento citado, compra forzada, NPC ausente en cualquier acción,
destino desconocido."""
exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())

# ── 1. El seguimiento de reglas usa SOLO el documento que se citó en la respuesta anterior ──
rep("graph-v2", '''        _log("reglas", citas=citas)''', '''        _log("reglas", citas=citas)
        if citas and game_state.get("ultimo_srd"):  # qué documento respondió de verdad (para el seguimiento)
            citados = [d for d in game_state["ultimo_srd"].get("docs", [])
                       if any(_plano(c) in _plano(srd_docs[d]["text"][:1500]) for c in citas)]
            if citados:
                game_state["ultimo_srd"]["citados"] = citados''')
rep("graph-v2", '''        srd_jugada = ["\\n".join(f"[{d}] {srd_docs[d]['text'][:1500]}" for d in ult["docs"])]
        if _intent("pregunta_reglas"):''', '''        # "¿Hay un máximo?" se responde con el documento que respondió la pregunta anterior (con los 3 recuperados citaba
        # "Damage Rolls" y decía "No hay un máximo")
        srd_jugada = ["\\n".join(f"[{d}] {srd_docs[d]['text'][:1500]}" for d in (ult.get("citados") or ult["docs"]))]
        if _intent("pregunta_reglas"):''')

# ── 2. Comprar también se ejecuta si el planner no la eligió (inventaba "Le pagas otra vez…" con 0 de oro) ──
rep("graph-v2", '''    for tipo_ in ("soltar", "atacar", "recoger", "curarse"):''', '''    for tipo_ in ("soltar", "atacar", "recoger", "curarse", "comprar"):''')
rep("graph-v2", '''                 "curarse": r"\\b(bebo|tomo|uso|me curo|curarme)", "soltar": r"\\b(tiro|lanzo|dejo|suelto|arrojo|me deshago)"}''',
    '''                 "curarse": r"\\b(bebo|tomo|uso|me curo|curarme)", "soltar": r"\\b(tiro|lanzo|dejo|suelto|arrojo|me deshago)",
                 "comprar": r"\\b(compr|pago|pagar|le pago|vendeme|me llevo)"}''')
rep("tools-v2", '''            if articulo in pedido or any(w[:5] in pedido for w in palabras):''',
    '''            if articulo in pedido or any(w[:4] in pedido for w in palabras):  # "afile" → afilar''')
# el planner podía elegir 'reglas' en una conversación ("¿Cuánto cuesta una poción?" → SRD potion of healing)
rep("graph-v2", '''    if npc_nombrado and not previos and paso.accion not in ("hablar", "reglas"):''',
    '''    if npc_nombrado and not previos and (paso.accion != "hablar" and not (paso.accion == "reglas" and
                                                                          PREGUNTA_REGLAS.search(_norm(accion)))):''')

# ── 3. NPC nombrado ausente: vale para cualquier acción (no solo hablar/comprar) ──
rep("graph-v2", '''    ausente = _npc_ausente(_accion(state)) if _intent("hablar", "comprar") and not dialogos else None''',
    '''    ausente = (_npc_ausente(_accion(state)) if not INTENCION["tipo"].startswith("pregunta") and not _intent("mover", "explorar")
               and not dialogos else None)  # "Le robo el oro a Goruk" en la plaza: le robaba a Elena''')

# ── 4. Moverse a un lugar que no existe: respuesta del código (inventaba "del pantano al castillo") ──
rep("graph-v2", '''    if _intent("mover") and not any(p.accion == "mover" for p, _ in state.get("pasos", [])) \\
            and _location_in(_accion(state)) == game_state["location"]:''',
    '''    if _intent("mover") and not any(p.accion == "mover" for p, _ in state.get("pasos", [])) \\
            and not _location_in(_accion(state)) and not _destino_referido(_accion(state)):
        conexiones = ", ".join(c.replace("_", " ") for c in world["locations"][game_state["location"]]["connections"])
        texto = f"No conoces ese lugar. Desde {game_state['location'].replace('_', ' ')} puedes ir a: {conexiones}."
        _log("narrar", observaciones=obs, memoria_grafo=memoria)
        return {"messages": [AIMessage(content=f"{texto}\\n\\n{_state_summary()}")]}
    if _intent("mover") and not any(p.accion == "mover" for p, _ in state.get("pasos", [])) \\
            and _location_in(_accion(state)) == game_state["location"]:''')

for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
