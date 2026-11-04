exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
from langchain_core.messages import HumanMessage, AIMessage
CASOS = [  # (jugada anterior, intención anterior, frase, intención esperada, seguimiento esperado)
 ("Según las reglas, ¿cuánto daño hace una caída?", "pregunta_reglas", "¿Hay un máximo?", "pregunta_reglas", True),
 ("Según las reglas, ¿qué tan peligroso es un dragón rojo adulto?", "pregunta_reglas", "¿Y su aliento?", "pregunta_reglas", True),
 ("¿Qué hace una bolsa de contención según las reglas?", "pregunta_reglas", "¿Cuánto peso aguanta?", "pregunta_reglas", True),
 ("¿Qué daño hace una espada larga a dos manos?", "pregunta_reglas", "¿Qué pasa si estoy envenenado?", "pregunta_reglas", False),
 ("¿Qué pasa si estoy envenenado?", "pregunta_reglas", "¿Cuánto cura un descanso corto?", "pregunta_reglas", False),
 ("¿Qué es un beholder?", "pregunta_reglas", "¿Qué hace la ventaja?", "pregunta_reglas", False),
 ("Según las reglas, ¿cuánto ayuda estar detrás de media cobertura?", "pregunta_reglas", "¿Y si la cobertura es de tres cuartos?", "pregunta_reglas", True),
 ("Según las reglas, ¿cuántos puntos de golpe tiene un esqueleto?", "pregunta_reglas", "¿Es inmune a algo?", "pregunta_reglas", True),
 ("Según las reglas, ¿qué estadísticas tiene un lobo?", "pregunta_reglas", "¿Qué pasa si me muerde?", "pregunta_reglas", True),
 ("¿Cuántos sitios nuevos encontré?", "pregunta_memoria", "¿Cuáles son?", "pregunta_memoria", True),
 ("¿Quién me afiló la espada?", "pregunta_memoria", "¿Cuánto le pagué?", "pregunta_memoria", True),
 ("¿Qué sitios nuevos conocí?", "pregunta_memoria", "¿Cuántos son?", "pregunta_memoria", True),
 ("Cuéntame la aventura completa.", "pregunta_memoria", "¿Qué fue lo más importante?", "pregunta_memoria", True),
 ("Según las reglas, ¿qué tan resistente es un oso pardo?", "pregunta_reglas", "¿Cuánto daño hacen sus garras?", "pregunta_reglas", True),
 ("Según las reglas, ¿cuánto ayuda estar detrás de media cobertura?", "pregunta_reglas", "¿Cómo vuelvo a la cueva desde aquí?", "pregunta_memoria", False),
 ("Según las reglas, ¿qué tan peligroso es un dragón rojo adulto?", "pregunta_reglas", "¿Dónde estoy?", "pregunta_estado", False),
 ("¿Qué es un beholder?", "pregunta_reglas", "¿Qué lugares he descubierto?", "pregunta_memoria", False),
]
g["reset_game"](); ok = 0
for prev, iprev, f, e_int, e_seg in CASOS:
    g["game_state"]["_intencion_previa"] = iprev
    g["clasificar_node"]({"messages": [HumanMessage(content=prev), AIMessage(content="..."), HumanMessage(content=f)]})
    r_int, r_seg = g["INTENCION"]["tipo"], g["INTENCION"]["seguimiento"]
    bien = r_int == e_int and (r_seg == e_seg or not e_seg and r_int != iprev)
    ok += bien
    print(("✓" if bien else "✗"), f"int={r_int} seg={r_seg} | {f}   (esperado {e_int}, seg={e_seg})")
print(f"{ok}/{len(CASOS)}")
