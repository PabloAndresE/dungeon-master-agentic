exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())
# nombres de objetos sin guiones bajos ("trozo_de_humo_arrancado")
rep("tools-v2", '''    name = re.sub(r"^(un|una|unos|unas|el|la|los|las)\\s+", "", name.strip(), flags=re.I)  # v3: "un vial" → "vial"''',
    '''    name = re.sub(r"^(un|una|unos|unas|el|la|los|las)\\s+", "", name.strip().replace("_", " "), flags=re.I)  # "un vial" → "vial"''')
# "No llevas eso" sin repetir la frase del jugador
rep("tools-v2", '''        return f"No llevas '{item_name}'. Inventario: {inv}"''', '''        return f"No llevas eso. Inventario: {', '.join(inv) or 'nada'}"''')
# mensajes de acciones no ejecutadas sin duplicados
rep("graph-v2", '''    if no_ejecutadas and not fallidas:  # el narrador narraba el ataque/recogida igual: lo dice la herramienta
        texto = " ".join(no_ejecutadas)''', '''    if no_ejecutadas and not fallidas:  # el narrador narraba el ataque/recogida igual: lo dice la herramienta
        texto = " ".join(dict.fromkeys(no_ejecutadas))''')
# si el jugador le habla a un NPC por su nombre, no contestan otros
rep("graph-v2", '''    if paso.accion == "hablar" and not se_dirige:''', '''    if paso.accion == "hablar" and npc_nombrado and _npc_aqui(paso.argumento) not in (None, npc_nombrado) \\
            and _npc_aqui(accion):
        # "Bron, ¿sabes algo de los goblins?" → también contestaba Ferrik, un NPC creado que estaba en la herrería
        paso = Paso(intencion=paso.intencion, pensamiento=paso.pensamiento, accion="responder", argumento="")
    if paso.accion == "hablar" and not se_dirige:''')
# "Busco una puerta trasera" (sin lugar conocido) es explorar, no mover
rep("graph-v2", '''    if REVISAR_INVENTARIO.search(_norm(accion).strip(" ¿?.")):''',
    '''    if _intent("mover") and re.match(r"(busco|buscar|examino|investigo|exploro)\\b", _norm(accion).strip(" ¿?.")) \\
            and not _location_in(accion):
        INTENCION["tipo"] = "explorar"  # "Busco una puerta trasera" → puede descubrir algo (antes: "No conoces ese lugar")
    if REVISAR_INVENTARIO.search(_norm(accion).strip(" ¿?.")):''')
for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
