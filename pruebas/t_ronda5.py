exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
g["reset_game"](); dm = g["MultiAgentDM"](g["app_v2"])
g["create_npc"].invoke({"name": "Ferrik el Pico Corto", "description": "Minero enano", "location": "herreria", "hostile": False})
for a in ["Busco una puerta trasera.", "Examino la chimenea.", "¿Encontré algo?", "Tiro la antorcha al fuego.", "Voy a la plaza.",
          "Voy a la herrería.", "Bron, ¿sabes algo de los goblins?", "¿Qué llevo?"]:
    r = dm.play(a).split("\n\n[HP")[0]
    print(f"[{g['INTENCION']['tipo']}] {a} | inv {g['game_state']['inventory']}\n    → {r[:260]!r}", flush=True)
