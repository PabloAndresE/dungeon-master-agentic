"""Clasificación de intención: regex actuales vs clasificador LLM con salida estructurada."""
import json, contextlib, io, sys, time, re
from typing import Literal
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

MODELO = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:latest"
nb = json.load(open("/root/dungeon-master-agentic/proyecto_final_v3.ipynb"))
g = {}
for c in nb["cells"]:
    if c["cell_type"] != "code":
        continue
    s = "".join(c["source"]).replace("http://localhost:11434", "http://127.0.0.1:11500")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(s, g)
    if c.get("id") == "graph-v2":
        break
g["reset_game"]()

CASOS = [  # (frase, intención correcta, lugar donde está el jugador)
    ("me voy pa la plaza", "mover", "taberna"), ("camino hacia el bosque", "mover", "taberna"),
    ("regreso a la taberna", "mover", "plaza"), ("quiero ir a la herrería", "mover", "plaza"),
    ("me largo de aquí hacia la cueva", "mover", "bosque"), ("salgo de la taberna rumbo a la plaza", "mover", "taberna"),
    ("busco algo raro en las paredes", "explorar", "cueva"), ("reviso detrás de los barriles", "explorar", "taberna"),
    ("inspecciono el suelo por si hay trampillas", "explorar", "taberna"), ("exploro los alrededores", "explorar", "bosque"),
    ("le pregunto al tabernero qué sabe del bosque", "hablar", "taberna"), ("hola goruk, qué tal", "hablar", "taberna"),
    ("¿conoces a alguien que venda armas?", "hablar", "taberna"), ("le cuento a elena que vengo de lejos", "hablar", "plaza"),
    ("saludo al herrero", "hablar", "herreria"), ("qué opinas de los goblins", "hablar", "taberna"),
    ("quiero comprar una poción", "comprar", "plaza"), ("le pago a bron para que afile mi espada", "comprar", "herreria"),
    ("véndeme una poción", "comprar", "plaza"), ("me llevo una poción, aquí tienes las monedas", "comprar", "plaza"),
    ("le doy un espadazo al goblin", "atacar", "cueva"), ("ataco", "atacar", "cueva"),
    ("golpeo al bicho con mi espada", "atacar", "cueva"), ("me lanzo contra el goblin", "atacar", "cueva"),
    ("agarro la antorcha", "recoger", "taberna"), ("tomo las hierbas", "recoger", "bosque"),
    ("me guardo el escudo", "recoger", "herreria"), ("me tomo la poción", "curarse", "bosque"),
    ("bebo la poción de curación", "curarse", "bosque"), ("me curo", "curarse", "cueva"),
    ("¿cuánta vida tengo?", "pregunta_estado", "cueva"), ("qué llevo encima", "pregunta_estado", "taberna"),
    ("donde estoy", "pregunta_estado", "bosque"), ("me queda oro?", "pregunta_estado", "plaza"),
    ("¿quién hay por aquí?", "pregunta_estado", "plaza"),
    ("¿cuánto daño hace un hacha de guerra?", "pregunta_reglas", "taberna"), ("cómo funciona la ventaja", "pregunta_reglas", "taberna"),
    ("¿qué estadísticas tiene un orco?", "pregunta_reglas", "taberna"), ("según las reglas, ¿un oso es peligroso?", "pregunta_reglas", "bosque"),
    ("¿qué lugares he descubierto?", "pregunta_memoria", "taberna"), ("resume lo que pasó", "pregunta_memoria", "taberna"),
    ("¿cómo vuelvo a la taberna?", "pregunta_memoria", "cueva"), ("¿por dónde se llega a la cueva?", "pregunta_memoria", "plaza"),
    ("¿qué me dijo goruk?", "pregunta_dialogo", "taberna"), ("repite lo que dijo elena", "pregunta_dialogo", "plaza"),
]


def regex_actual(f, loc):
    """Réplica de las reglas regex actuales (las que no cubren atacar/recoger/curarse las deja al planner: 'otra')."""
    g["game_state"]["location"] = loc
    n = g["_norm"](f)
    if re.search(r"que me (dijo|dijeron|respondio|contesto)|que (dijo|respondio|contesto)", n): return "pregunta_dialogo"
    if g["PREGUNTA_REGLAS"].search(n): return "pregunta_reglas"
    if g["_es_pregunta_estado"](f): return "pregunta_estado"
    if g["EXPLORACION"].search(f): return "explorar"
    if re.search(r"\b(compro|compra|comprar|pago|pagar|vend[eao]me|me vend|adquiero)\b", n): return "comprar"
    se_dirige = bool(re.search(r"\b(hablo|habla|charlo|digo|dice|pregunto|pido|saludo|cuento|converso|le)\b", n)) or \
        bool(re.search(r"\b(conoces|sabes|tienes|vendes|puedes|has visto|has oido|me dices|opinas|piensas|crees|te parece)\b", n))
    if se_dirige: return "hablar"
    if g["_location_in"](f) or re.search(r"\b(voy|vuelvo|regreso|salgo|avanzo|camino|me dirijo|entro|ir a)\b", n):
        return "pregunta_memoria" if f.strip().startswith("¿") else "mover"
    return "otra"


class Intencion(BaseModel):
    tipo: Literal["mover", "explorar", "hablar", "comprar", "atacar", "recoger", "curarse",
                  "pregunta_estado", "pregunta_reglas", "pregunta_memoria", "pregunta_dialogo", "otra"]


SYSTEM = """\
Clasifica lo que escribe el jugador de un juego de rol en UNA intención:
- mover: quiere ir a otro lugar ("me voy a…", "vuelvo al…", "entro en…")
- explorar: busca/examina/inspecciona algo en el lugar (algo escondido, un rastro, un objeto)
- hablar: se dirige a un personaje: le pregunta, le cuenta, lo saluda, le pide su opinión ("¿conoces…?", "¿qué opinas…?")
- comprar: quiere comprar o pagar un servicio
- atacar: pelea, golpea, ataca a alguien · recoger: toma/agarra/guarda un objeto · curarse: bebe/usa una poción, se cura
- pregunta_estado: pregunta por SU estado actual: vida, oro, inventario, dónde está, quién/qué hay aquí
- pregunta_reglas: pregunta por las reglas de D&D: estadísticas de criaturas, daño de armas, cómo funciona una regla
- pregunta_memoria: pregunta por el PASADO o el mapa: qué lugares descubrió, resumen, cómo llegar a un lugar
- pregunta_dialogo: pregunta qué le dijo un personaje antes
- otra: nada de lo anterior
Ejemplos: "me voy pa la herrería" → mover · "miro debajo de la mesa" → explorar · "oye tabernero, ¿hay trabajo?" → hablar ·
"¿cuánto oro llevo?" → pregunta_estado · "¿qué daño hace una daga?" → pregunta_reglas · "¿cómo llego a la plaza?" → pregunta_memoria ·
"le arreo al lobo" → atacar · "¿qué me contó Bron?" → pregunta_dialogo"""

clf = ChatOllama(model=MODELO, base_url="http://127.0.0.1:11500", temperature=0).with_structured_output(Intencion, method="json_schema")

ok_r = ok_l = 0
t0 = time.time()
for f, et, loc in CASOS:
    r = regex_actual(f, loc)
    l = clf.invoke([SystemMessage(content=SYSTEM), HumanMessage(content=f"Jugador (está en {loc}): {f}")]).tipo
    rr = r == et or (et in ("atacar", "recoger", "curarse") and r == "otra")
    ok_r += rr; ok_l += l == et
    if not rr or l != et:
        print(f"{'✓' if rr else '✗'}regex={r:16s} {'✓' if l == et else '✗'}llm={l:16s} esperado={et:16s} | {f}")
n = len(CASOS)
print(f"\nREGEX: {ok_r}/{n} ({ok_r/n:.0%})   LLM {MODELO}: {ok_l}/{n} ({ok_l/n:.0%})   {(time.time()-t0)/n:.2f} s/frase")
