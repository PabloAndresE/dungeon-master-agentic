exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
for k in range(4):
    g["reset_game"](); dm=g["MultiAgentDM"](g["app_v2"])
    for q in ["Según las reglas, ¿cuánto daño hace una caída?","¿Hay un máximo?","Según las reglas, ¿qué tan resistente es un oso pardo?","¿Cuánto daño hacen sus garras?","¿Cómo funciona la ventaja en una tirada según las reglas?","Según las reglas, ¿cuánto aguanto sin respirar?"]:
        print(k, q, "→", dm.play(q).split("\n\n[HP")[0][:300].replace("\n"," "), flush=True)
