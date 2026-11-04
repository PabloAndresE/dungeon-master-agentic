exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
from langchain_core.messages import HumanMessage
g["reset_game"]()
for prev, f in [("pregunta_reglas","¿qué lugares he descubierto?"),("pregunta_reglas","¿Hay un máximo?"),("pregunta_reglas","¿Cuánto peso aguanta?"),
                ("pregunta_reglas","¿Y si la cobertura es de tres cuartos?"),("pregunta_reglas","¿Dónde estoy?"),("pregunta_memoria","¿Cuáles son?"),
                ("pregunta_memoria","¿Cuánto le pagué?"),("pregunta_memoria","¿Cuántos son?"),("pregunta_memoria","¿Cuánto oro tengo?"),("pregunta_reglas","¿Qué me dijo Goruk?")]:
    g["game_state"]["_intencion_previa"]=prev
    g["clasificar_node"]({"messages":[HumanMessage(content=f)]}); print(prev,"→",g["INTENCION"]["tipo"],"|",f)
