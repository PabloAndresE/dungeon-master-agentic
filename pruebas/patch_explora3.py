"""v3 — detector de seguimiento con el modelo grande (el 7B acertaba 8-10/20; el 72B 19/20)."""
exec(open("/root/dungeon-master-agentic/pruebas/patch_base.py").read())
rep("graph-v2", '''class IntencionJugador(BaseModel):
    seguimiento: bool = Field(description=(
        "true SOLO si la frase NO se entiende sola y continúa la jugada anterior ('¿Hay un máximo?', '¿Y su aliento?', "
        "'¿Cuáles son?', '¿Cuánto le pagué?'); false si nombra su propio tema ('¿Qué pasa si estoy envenenado?')"))
    tipo: Literal[''', '''class IntencionJugador(BaseModel):
    tipo: Literal[''')
rep("graph-v2", '''        r_int = clasificador_intencion.invoke([SystemMessage(content=SYSTEM_INTENCION), HumanMessage(
            content=f"Jugada anterior: {humanas[-2] if len(humanas) > 1 else '(ninguna)'}\\n"
                    f"Jugador (está en {game_state['location']}): {_accion(state)}")])
        INTENCION["tipo"], INTENCION["seguimiento"] = r_int.tipo, r_int.seguimiento''',
    '''        INTENCION["tipo"] = clasificador_intencion.invoke([SystemMessage(content=SYSTEM_INTENCION), HumanMessage(
            content=f"Jugador (está en {game_state['location']}): {_accion(state)}")]).tipo
        INTENCION["seguimiento"] = False
        previa_txt = humanas[-2] if len(humanas) > 1 else ""
        if (previa_txt and game_state.get("_intencion_previa", "").startswith("pregunta")
                and _accion(state).strip().startswith("¿") and len(re.findall(r"\\w+", _accion(state))) <= 8):
            INTENCION["seguimiento"] = detector_seguimiento.invoke([SystemMessage(content=SYSTEM_SEGUIMIENTO), HumanMessage(
                content=f"Pregunta anterior: {previa_txt}\\nPregunta nueva: {_accion(state)}")]).continua == "si"''')
rep("graph-v2", '''    return a.startswith("¿") and len(re.findall(r"\\w+", a)) <= 8 and (
        INTENCION.get("seguimiento", False) or bool(re.match(r"^\\W*y\\b", _norm(a))))''',
    '''    return a.startswith("¿") and INTENCION.get("seguimiento", False)''')
rep("graph-v2", '''INTENCION = {"tipo": "otra", "seguimiento": False}''', '''INTENCION = {"tipo": "otra", "seguimiento": False}


# Detector de PREGUNTAS DE SEGUIMIENTO ("¿Hay un máximo?" continúa la anterior; "¿Qué pasa si estoy envenenado?" no).
# Contar palabras fallaba y el 7B acertaba 8-10 de 20 casos; el modelo grande (el del vigilante) 19/20, ~0.5 s.
# Solo se llama cuando la jugada anterior fue una pregunta y esta es una pregunta corta.
class Seguimiento(BaseModel):
    tema_propio: str = Field(description="lo que la pregunta nueva NOMBRA ella misma, o 'ninguno'")
    continua: Literal["si", "no"]


SYSTEM_SEGUIMIENTO = """\\
Decides si la PREGUNTA NUEVA de un jugador continúa la PREGUNTA ANTERIOR (no se entiende sola) o trae un tema propio.
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
- anterior "¿qué es un orco?" · nueva "¿Dónde estoy?" → "ubicación del jugador", "no".\"\"\"

detector_seguimiento = ChatOllama(model=WATCHER_MODEL, base_url=OLLAMA_BASE_URL, temperature=0).with_structured_output(
    Seguimiento, method="json_schema")''')
# las herencias de intención usaban "corta" por palabras: ahora usan el detector
for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c.get("id"), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
json.dump(nb, open(PATH, "w"), ensure_ascii=False, indent=1)
print("patched")
