exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())
rep("graph-v2", '''        texto = "\\n".join(l for l in texto.splitlines() if not re.search(cjk, l)).strip()
        if not texto:  # nunca una respuesta vacía: la cita oficial tal cual''',
    '''        texto = "\\n".join(l for l in texto.splitlines() if not re.search(cjk, l)).strip()
        ingles = len(re.findall(r"\\b(the|of|to|a|an|and|or|it|its|takes|creature|maximum|damage|each|feet)\\b", texto.lower()))
        if texto and ingles >= 0.25 * max(1, len(texto.split())):  # copió la cita sin traducir ("to a maximum of 20d6.")
            texto = llm_reglas.invoke([SystemMessage(content=SYSTEM_TRADUCIR_REGLAS), HumanMessage(
                content=f"Pregunta: {accion_r}\\nTexto oficial:\\n" + ("\\n".join(citas) or texto) +
                        "\\nResponde en ESPAÑOL, en una oración completa.")]).content.strip()
        if not texto:  # nunca una respuesta vacía: la cita oficial tal cual''')
for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
