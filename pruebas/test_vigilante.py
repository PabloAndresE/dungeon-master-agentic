"""Calibración del vigilante con casos etiquetados (narraciones correctas e incorrectas)."""
import sys, time
from typing import Literal
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

MODELO = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:72b"
URL = "http://127.0.0.1:11500"


class Afirmaciones(BaseModel):
    afirmaciones: list[str] = Field(description="Hechos de JUEGO afirmados (máx 6): quién está, qué hay, qué pasó, "
                                                "rasgos de personajes, resultados. NO incluyas ambiente (luz, olores, sonidos).")


class Chequeo(BaseModel):
    evidencia: str = Field(description="Cita textual de la VERDAD relacionada con la afirmación, o 'ninguna'.")
    estado: Literal["compatible", "inventa", "contradice"] = Field(description=(
        "compatible: la verdad lo confirma, o es una acción/resultado que muestran las observaciones, o es un detalle "
        "menor que no cambia el juego · inventa: agrega un objeto, criatura, personaje, lugar, rasgo de personaje o "
        "resultado que NO aparece en la verdad · contradice: dice algo opuesto a la verdad"))


extraer = ChatOllama(model=MODELO, base_url=URL, temperature=0).with_structured_output(Afirmaciones, method="json_schema")
chequear = ChatOllama(model=MODELO, base_url=URL, temperature=0).with_structured_output(Chequeo, method="json_schema")

NOTA = ("La VERDAD describe el estado DESPUÉS de esta jugada y las OBSERVACIONES lo que pasó en ella: es normal que "
        "la narración cuente la transición (\"llegas a…\", \"recoges…\") si las observaciones la muestran.")


def revisar(verdad, narracion):
    afs = extraer.invoke(f"Extrae los hechos de juego afirmados en esta narración:\n{narracion}").afirmaciones[:6]
    malos = []
    for a in afs:
        c = chequear.invoke(f"{NOTA}\n\nVERDAD:\n{verdad}\n\nAFIRMACIÓN: {a}\n\n¿Es compatible con la verdad?")
        if c.estado != "compatible":
            malos.append((c.estado, a, c.evidencia[:80]))
    return afs, malos


TABERNA = ("ESTADO: [HP: 20/20 | Oro: 15 | Ubicacion: taberna | Inventario: espada oxidada, pocion de curacion]\n"
           "LUGAR taberna: Una taberna calida con olor a estofado. Un fuego crepita en la chimenea.\n"
           "PERSONAJES PRESENTES:\n- Goruk el tabernero: Enano tabernero, gruñón pero de buen corazón.\n"
           "Objetos aquí: antorcha. Puedes ir a: plaza, bosque.\nOBSERVACIONES DE ESTA JUGADA:\n- ver_estado()")
BOSQUE = ("ESTADO: [HP: 20/20 | Oro: 15 | Ubicacion: bosque | Inventario: espada oxidada, pocion de curacion]\n"
          "LUGAR bosque: Arboles altos bloquean la luz. Se escuchan ruidos entre la maleza.\nPERSONAJES PRESENTES:\n- nadie\n"
          "Objetos aquí: hierbas medicinales.\nOBSERVACIONES DE ESTA JUGADA:\n- mover(bosque): MOVIMIENTO EXITOSO → el jugador está en: bosque.")
SIN_POCION = ("ESTADO: [HP: 20/20 | Oro: 15 | Ubicacion: plaza | Inventario: espada oxidada, antorcha]\n"
              "LUGAR plaza: La plaza central del pueblo.\nPERSONAJES PRESENTES:\n- Elena la comerciante: comerciante astuta y amable.\n"
              "OBSERVACIONES DE ESTA JUGADA:\n- curarse(): Bebiste la pocion. Recuperas 6 HP.")
CUEVA_FALLO = ("ESTADO: [HP: 17/20 | Oro: 15 | Ubicacion: cueva | Inventario: espada oxidada, antorcha]\n"
               "LUGAR cueva: Una cueva oscura y humeda.\nPERSONAJES PRESENTES:\n- Goblin centinela (hostil)\n"
               "OBSERVACIONES DE ESTA JUGADA:\n- atacar(goblin): Tu ataque: d20=6 -> FALLO. Ataque de Goblin: d20=14 -> ACIERTO, 3 de dano a ti. Goblin centinela sigue en pie.")
CUEVA_GANA = CUEVA_FALLO.replace("d20=6 -> FALLO", "d20=15 -> ACIERTO, 4 de dano").replace(
    "Goblin centinela sigue en pie.", "¡Goblin centinela ha sido derrotado!")

CASOS = [  # (verdad, narración, ¿tiene error?)
    (TABERNA, "Miras a tu alrededor. Goruk el tabernero, un enano gruñón, limpia jarras detrás de la barra. Ves una antorcha junto a la puerta.", False),
    (TABERNA, "Goruk el tabernero, un humano alto y delgado, te sirve una cerveza.", True),
    (TABERNA, "Un mago anciano te observa desde una mesa del fondo. Goruk te saluda.", True),
    (TABERNA, "Desde aquí puedes ir a la plaza o al bosque.", False),
    (BOSQUE, "Llegas al bosque. Los árboles bloquean la luz y entre la maleza ves unas hierbas medicinales.", False),
    (BOSQUE, "Llegas al bosque, donde un lobo gris te gruñe desde los arbustos.", True),
    (SIN_POCION, "Bebes la poción y sientes cómo tus heridas sanan.", False),
    (SIN_POCION, "Bebes un sorbo de la poción y la guardas: todavía te queda la mitad en tu mochila.", True),
    (CUEVA_FALLO, "Tu espada falla y el goblin te hiere en el brazo; sigue en pie, gruñendo.", False),
    (CUEVA_FALLO, "Tu espada atraviesa al goblin, que cae derrotado a tus pies.", True),
    (CUEVA_GANA, "Tu espada atraviesa al goblin, que cae derrotado a tus pies.", False),
    (CUEVA_GANA, "Derrotas al goblin y encuentras una llave dorada en su cinturón.", True),
]

tp = fp = fn = tn = 0
t0 = time.time()
for verdad, narr, error in CASOS:
    afs, malos = revisar(verdad, narr)
    detecta = bool(malos)
    tp += detecta and error; fp += detecta and not error; fn += (not detecta) and error; tn += (not detecta) and not error
    marca = "✓" if detecta == error else "✗"
    print(f"{marca} error={error!s:5s} detecta={detecta!s:5s} | {narr[:70]}")
    for m in malos:
        print(f"      [{m[0]}] {m[1][:70]} | evid: {m[2]}")
print(f"\n{MODELO}: detecta {tp}/{tp+fn} errores (recall), falsos positivos {fp}/{fp+tn}, {time.time()-t0:.0f}s para {len(CASOS)} casos")
