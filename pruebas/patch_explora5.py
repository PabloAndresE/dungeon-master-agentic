exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())
rep("graph-v2", '''- pregunta_reglas: pregunta por las reglas de D&D: estadísticas de criaturas, daño de armas, cómo funciona una regla''',
    '''- pregunta_reglas: pregunta por las reglas de D&D: estadísticas de criaturas, daño de armas, cómo funciona una regla,
  qué efecto tiene una condición o un descanso ("¿qué pasa si estoy envenenado?", "¿cuánto cura un descanso corto?")''')
for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
