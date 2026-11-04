exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())
rep("graph-v2", '''    if (_seguimiento_corto(accion) and previa in ("pregunta_memoria", "pregunta_reglas")
            and (_intent("pregunta_estado", "otra") or (previa == "pregunta_memoria" and _intent("pregunta_reglas"))
                 or (previa == "pregunta_reglas" and re.match(r"^\\W*y\\b", _norm(accion.strip()))))
            and (not _es_pregunta_estado(accion) or re.search(r"\\b(pague|pagaste|costo|por cuanto)\\b", _norm(accion)))
            and not (previa == "pregunta_memoria" and PREGUNTA_REGLAS.search(_norm(accion)))):''',
    '''    if _seguimiento_corto(accion) and previa in ("pregunta_memoria", "pregunta_reglas"):''')
for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
