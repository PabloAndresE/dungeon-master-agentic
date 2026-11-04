exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
g["reset_game"](); dm = g["MultiAgentDM"](g["app_v2"])
for a in ["Hablo con Goruk sobre el bosque.", "Voy a la plaza.", "Le compro una poción a Elena.", "Voy a la herrería.",
          "Le pago a Bron para que afile mi espada.", "Voy a la plaza.", "Voy al bosque.", "Voy a la cueva.",
          "Examino los rincones de la cueva por si hay otra salida.", "¿Encontré algo?", "¿Puedo volver a ese sitio?",
          "¿Cómo llego a la herrería desde aquí?", "¿Qué lugares cruzo?", "¿Quién me afiló la espada?", "¿Cuánto le pagué?",
          "¿Qué lugares he descubierto?", "¿Cuántos son?", "¿Quién me advirtió del bosque?", "¿Quién me habló de dragones?",
          "¿Dónde estaban las hierbas?", "¿Qué compré y a quién?", "Según las reglas, ¿cuánto daño hace una caída?", "¿Hay un máximo?",
          "Según las reglas, ¿cuánto ayuda estar detrás de media cobertura?", "¿Y si la cobertura es de tres cuartos?"]:
    r = dm.play(a).split("\n\n[HP")[0]
    print(f"[{g['INTENCION']['tipo']}{'·seg' if g['INTENCION'].get('seguimiento') else ''}] {a}\n    → {r[:260]!r}", flush=True)
