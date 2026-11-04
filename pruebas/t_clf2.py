exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
from langchain_core.messages import HumanMessage
src=open("/root/dungeon-master-agentic/pruebas/test_intencion.py").read()
CASOS=eval(src[src.index("CASOS = [")+8:src.index("]\n\n\ndef regex_actual")+1])
CASOS += [("Entro en lo que haya encontrado.","mover","cueva"),("¿Puedo volver a ese sitio?","pregunta_memoria","cueva"),
          ("¿Quién me afiló la espada?","pregunta_memoria","bosque"),("Cuéntame la aventura completa.","pregunta_memoria","bosque"),
          ("¿Quién me advirtió del bosque?","pregunta_memoria","plaza"),("¿Qué me respondió?","pregunta_dialogo","plaza"),
          ("¿Qué aventuras me menciona Goruk?","hablar","taberna")]
g["reset_game"](); ok=0
for f,e,loc in CASOS:
    g["game_state"]["location"]=loc
    g["clasificar_node"]({"messages":[HumanMessage(content=f)]}); r=g["INTENCION"]["tipo"]; ok+=r==e
    if r!=e: print("✗",r,"esperado",e,"|",f)
print(f"{ok}/{len(CASOS)}")
