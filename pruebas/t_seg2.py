import re, sys
from typing import Literal
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
M = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:latest"
class Seg(BaseModel):
    tema_propio: str
    continua: Literal["si", "no"]
SYS = """Decides si la PREGUNTA NUEVA de un jugador continúa la PREGUNTA ANTERIOR (no se entiende sola) o trae un tema propio.
tema_propio: la criatura, objeto, regla o cosa que la pregunta nueva NOMBRA ella misma; "ninguno" si no nombra nada
(pronombres como "su", "sus", "lo", "eso" o palabras sueltas como "máximo", "peso", "daño" NO son un tema propio).
continua: "si" cuando tema_propio es "ninguno"; "no" cuando la pregunta nueva nombra su propio tema.
Ejemplos:
- anterior "¿cuánto daño hace una caída?" · nueva "¿Hay un máximo?" → tema_propio "ninguno", continua "si"
- anterior "¿qué es un dragón rojo?" · nueva "¿Y su aliento?" → "ninguno", "si"
- anterior "¿qué hace la bolsa de contención?" · nueva "¿Cuánto peso aguanta?" → "ninguno", "si"
- anterior "¿qué daño hace una espada larga?" · nueva "¿Qué pasa si estoy envenenado?" → "envenenado", "no"
- anterior "¿qué lugares descubrí?" · nueva "¿Cuántos son?" → "ninguno", "si"
- anterior "¿qué es un beholder?" · nueva "¿Qué hace la ventaja?" → "ventaja", "no"
- anterior "¿quién me afiló la espada?" · nueva "¿Cuánto le pagué?" → "ninguno", "si"
- anterior "¿qué es un orco?" · nueva "¿Dónde estoy?" → "ubicación del jugador", "no\""""
llm = ChatOllama(model=M, base_url="http://127.0.0.1:11500", temperature=0).with_structured_output(Seg, method="json_schema")
CASOS = [("Según las reglas, ¿cuánto daño hace una caída?", "¿Hay un máximo?", "si"),
 ("Según las reglas, ¿qué tan peligroso es un dragón rojo adulto?", "¿Y su aliento?", "si"),
 ("¿Qué hace una bolsa de contención según las reglas?", "¿Cuánto peso aguanta?", "si"),
 ("¿Qué daño hace una espada larga a dos manos?", "¿Qué pasa si estoy envenenado?", "no"),
 ("¿Qué pasa si estoy envenenado?", "¿Cuánto cura un descanso corto?", "no"),
 ("¿Qué es un beholder?", "¿Qué hace la ventaja?", "no"),
 ("Según las reglas, ¿cuánto ayuda estar detrás de media cobertura?", "¿Y si la cobertura es de tres cuartos?", "si"),
 ("Según las reglas, ¿cuántos puntos de golpe tiene un esqueleto?", "¿Es inmune a algo?", "si"),
 ("Según las reglas, ¿qué estadísticas tiene un lobo?", "¿Qué pasa si me muerde?", "si"),
 ("¿Cuántos sitios nuevos encontré?", "¿Cuáles son?", "si"),
 ("¿Quién me afiló la espada?", "¿Cuánto le pagué?", "si"),
 ("Cuéntame la aventura completa.", "¿Qué fue lo más importante?", "si"),
 ("Según las reglas, ¿qué tan resistente es un oso pardo?", "¿Cuánto daño hacen sus garras?", "si"),
 ("Según las reglas, ¿cuánto ayuda estar detrás de media cobertura?", "¿Cómo vuelvo a la cueva desde aquí?", "no"),
 ("Según las reglas, ¿qué tan peligroso es un dragón rojo adulto?", "¿Dónde estoy?", "no"),
 ("¿Qué es un beholder?", "¿Qué lugares he descubierto?", "no"),
 ("¿Qué hace una poción de curación según las reglas?", "¿Y un antídoto?", "no"),
 ("¿Cuánto daño hace una daga?", "¿Y un hacha de guerra?", "no"),
 ("¿Qué es un goblin?", "¿Cuántos puntos de golpe tiene?", "si"),
 ("¿Qué me dijo Goruk?", "¿Qué me dijo Elena?", "no")]
ok = 0
for prev, f, e in CASOS:
    r = llm.invoke([SystemMessage(content=SYS), HumanMessage(content=f"Pregunta anterior: {prev}\nPregunta nueva: {f}")])
    ok += r.continua == e
    print("✓" if r.continua == e else "✗", r.continua, repr(r.tema_propio), "|", f)
print(f"{M}: {ok}/{len(CASOS)}")
