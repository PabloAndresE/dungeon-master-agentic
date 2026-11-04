exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
g["reset_game"](); dm = g["MultiAgentDM"](g["app_v2"])
for a in ["Voy al castillo.", "Quiero salir de la aventura.", "Voy a la plaza.", "Le robo el oro a Goruk.", "¿Cuánto cuesta una poción?",
          "Le compro una poción a Elena.", "Voy a la herrería.", "Le pago a Bron para que afile mi espada.",
          "Le pago otra vez para que la afile.", "Ataco al goblin.",
          "Según las reglas, ¿cuánto daño hace una caída?", "¿Hay un máximo?",
          "Según las reglas, ¿qué tan peligroso es un dragón rojo adulto?", "¿Y su aliento?", "¿Qué pasa si estoy envenenado?"]:
    r = dm.play(a).split("\n\n[HP")[0]
    print(f"[{g['INTENCION']['tipo']}{'·seg' if g['INTENCION'].get('seguimiento') else ''}] {a} | oro {g['game_state']['gold']}\n    → {r[:230]!r}", flush=True)
