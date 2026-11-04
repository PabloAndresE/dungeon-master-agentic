"""Pruebas exploratorias de la v3: escenarios con frases nuevas; registra intención, pasos, estado y chequeos."""
exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
import json, sys, time, re, copy, traceback
ESC = {
 "comercio": ["Voy a la plaza.", "Hola Elena, ¿qué vendes?", "¿Cuánto cuesta una poción?", "¿Me la dejas en 5 monedas?",
              "Le compro una poción a Elena.", "Le compro otra poción.", "¿Cuánto oro me queda?", "Voy a la herrería.",
              "Bron, ¿sabes algo de los goblins?", "Le pago a Bron para que afile mi espada.", "Le pago otra vez para que la afile.",
              "¿Qué me dijo Elena?", "¿Qué compré hoy?"],
 "movimiento": ["Voy al castillo.", "Voy a la taberna.", "Salgo a la calle.", "Me voy a la forja.", "Voy a la plaza.",
                "Vuelvo atrás.", "Voy a la plaza.", "Corro hacia el bosque y luego a la cueva.", "¿Dónde estoy?",
                "Regreso a la taberna directamente.", "¿Cómo llego a la cueva?", "Voy a la cueva."],
 "combate": ["Ataco a Goruk.", "¿Cuánta vida tengo?", "Me tomo la poción.", "Me tomo otra poción.", "Voy al bosque.",
             "Ataco al lobo.", "Voy a la cueva.", "Ataco al goblin.", "Ataco al goblin.", "Ataco al goblin.", "Ataco al goblin.",
             "Ataco al goblin.", "¿El goblin sigue vivo?", "Ataco al goblin otra vez.", "Recojo lo que haya dejado el goblin.", "¿Cuánta vida me queda?"],
 "exploracion": ["Examino la chimenea de la taberna.", "¿Encontré algo?", "Lo recojo.", "¿Qué llevo?", "Examino la chimenea otra vez.",
                 "Busco una puerta trasera.", "Entro por ahí.", "¿Dónde estoy?", "Vuelvo a la taberna.", "¿Qué sitios nuevos hay?",
                 "Busco al tabernero.", "Recojo la antorcha.", "Recojo la antorcha."],
 "reglas": ["Según las reglas, ¿qué tan peligroso es un dragón rojo adulto?", "¿Y su aliento?", "¿Cuánto daño hace una bola de fuego?",
            "¿A qué nivel se puede subir?", "¿Qué daño hace una espada larga a dos manos?", "¿Qué pasa si estoy envenenado?",
            "¿Cuánto cura un descanso corto?", "¿Cuánto cuesta una cuerda de cáñamo según las reglas?", "¿Dónde estoy?",
            "¿Qué es un beholder?", "¿Qué hace la ventaja?"],
 "memoria": ["Hablo con Goruk sobre el bosque.", "Voy a la plaza.", "Le compro una poción a Elena.", "Voy al bosque.", "Recojo las hierbas medicinales.",
             "¿Qué compré y a quién?", "¿A quién conocí hasta ahora?", "¿Qué me advirtió Goruk?", "¿Dónde estaban las hierbas?",
             "¿Qué hice primero?", "Resume en una frase lo que hice.", "¿Cuántas veces cambié de lugar?"],
 "arreglos": ["Miro a mi alrededor.", "Voy a la plaza.", "¿Cuánto cuesta una poción?", "¿Me la dejas en 5 monedas?",
              "¿Cuánto oro tengo?", "Me tomo la poción.", "Lanzo la espada al suelo.", "¿Qué llevo?", "Recojo la espada.",
              "¿Qué hora es?", "Voy a la taberna.", "Examino la chimenea con cuidado.", "¿Encontré algo?", "Lo recojo.",
              "Tiro la antorcha al fuego.", "¿Qué llevo?", "Quiero comprar una poción.", "Voy a la plaza.", "Le compro una poción a Elena."],
 "raro": ["...", "I go to the plaza.", "asdfgh qwerty", "¿Qué hora es?", "Bailo en la mesa.", "Me duermo un rato.",
          "Le robo el oro a Goruk.", "Grito muy fuerte.", "Lanzo la espada al fuego.", "¿Qué llevo?", "Le pregunto a Goruk si me vio bailar.",
          "Quiero salir de la aventura."],
}
nombre = sys.argv[1]; out = []
g["reset_game"](); dm = g["MultiAgentDM"](g["app_v2"])
CJK = re.compile(r"[぀-ヿ一-鿿가-힯]")
for a in ESC[nombre]:
    gs = g["game_state"]; antes = copy.deepcopy({k: gs[k] for k in ("location", "hp", "gold", "inventory")})
    n = 0; t0 = time.time()
    try:
        r = dm.play(a); err = None
    except Exception as e:
        r, err = "", traceback.format_exc()[-600:]
    dt = time.time() - t0
    gs = g["game_state"]; desp = {k: copy.deepcopy(gs[k]) for k in ("location", "hp", "gold", "inventory")}
    pasos = [(d.get("herramienta"), d.get("args"), str(d.get("observacion"))[:160]) for nodo, d in g["TRAZA"][n:] if nodo == "actuar"]
    cuerpo = r.split("\n\n[HP")[0]
    flags = []
    if err: flags.append("EXCEPCION")
    if not cuerpo.strip(): flags.append("VACIA")
    if CJK.search(r): flags.append("CJK")
    if "[HP:" not in r and not err: flags.append("SIN_ESTADO")
    m = re.search(r"\bllegas (?:de nuevo |nuevamente )?(?:a|al) (?:la |el )?([a-záéíóúñ ]+)", cuerpo.lower())
    if m and desp["location"] == antes["location"]: flags.append(f"DICE_LLEGAS_SIN_MOVER({m.group(1)[:20]})")
    if desp["location"] != antes["location"] and g["INTENCION"]["tipo"] != "mover": flags.append("MOVIO_SIN_INTENCION_MOVER")
    if dt > 60: flags.append(f"LENTO({dt:.0f}s)")
    out.append(dict(a=a, intencion=g["INTENCION"]["tipo"], pasos=pasos, antes=antes, despues=desp, resp=cuerpo, flags=flags, t=round(dt, 1), err=err))
    print(f"[{g['INTENCION']['tipo']}] {a} ({dt:.0f}s) {flags}\n   pasos={[(p[0], p[1]) for p in pasos]}\n   {antes['location']}→{desp['location']} hp {antes['hp']}→{desp['hp']} oro {antes['gold']}→{desp['gold']} inv {desp['inventory']}\n   → {cuerpo[:350]!r}", flush=True)
json.dump(out, open(f"/root/dungeon-master-agentic/pruebas/resultados/explora_{nombre}.json", "w"), ensure_ascii=False, indent=1, default=str)
