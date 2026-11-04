# ────────────────────────────────────────────────────────────────────────────
# Secuencia HOLD-OUT 3 — escrita ANTES de evaluar la v3 (14-oct, noche)
# ────────────────────────────────────────────────────────────────────────────
# El hold-out 2 ya se usó para evaluar v2 y mirar sus fallos. Esta secuencia da el número limpio de la v3.
# Cubre lo nuevo de la v3: comprar (Elena) y pagar un servicio (Bron), combate de varias rondas (CA y PG del
# SRD), diálogo con NPCs y reglas del SRD que no aparecieron antes (oso pardo, caídas).
# Recorrido: taberna → plaza → herrería → plaza → bosque → cueva → (descubrimiento) → cueva → bosque.

TEST_SEQUENCE_HOLDOUT3 = [
    ("Echo una mirada por la taberna.", "¿Qué cosas hay que pueda tomar?", "item_mention", "antorcha"),
    ("Le pregunto a Goruk qué se cuenta por el pueblo.", "¿Qué me dijo Goruk?", "relation_memory", "goruk"),
    ("Me dirijo a la plaza.", "¿En dónde estoy parado?", "location", "plaza"),
    ("Bebo mi poción de curación.", "¿Me queda alguna poción?", "potion_used", "pocion"),
    ("Le compro una poción a Elena.", "¿Cuánto oro me queda?", "gold_change", "gold"),
    ("Reviso lo que llevo.", "¿Llevo alguna poción ahora?", "inventory", "pocion"),
    ("Voy a la herrería.", "¿Dónde estoy ahora?", "location", "herreria"),
    ("Le pago a Bron para que afile mi espada.", "¿Cómo está mi espada ahora?", "inventory", "afilada"),
    ("Intento cruzar directo al bosque desde aquí.", "¿Llegué al bosque?", "illegal_move", "bosque"),
    ("Vuelvo a la plaza.", "¿Dónde estoy?", "location", "plaza"),
    ("Me adentro en el bosque.", "¿Dónde me encuentro?", "location", "bosque"),
    # SRD 1: criatura (SRD: Brown Bear CA 11, PG 34, mordisco 1d8+4, garras 2d6+4)
    ("Según las reglas, ¿qué tan resistente es un oso pardo?", "¿Cuánto daño hacen sus garras?", "srd", "11,34"),
    ("Sigo hasta la cueva.", "¿Dónde estoy?", "location", "cueva"),
    ("Ataco al goblin.", "¿Cómo va la pelea?", "hp_mentioned", "hp"),
    ("Lo ataco de nuevo.", "¿Cuánta vida me queda?", "hp_mentioned", "hp"),
    ("Sigo atacando al goblin.", "¿Cuánta vida tengo?", "hp_mentioned", "hp"),
    ("Examino los rincones de la cueva por si hay otra salida.", "¿Encontré algo?", "expansion", "nuevo"),
    # SRD 2: regla (SRD: The Environment — caída: 1d6 contundente por cada 10 pies, máximo 20d6)
    ("Según las reglas, ¿cuánto daño hace una caída?", "¿Hay un máximo?", "srd", "1d6,10"),
    ("Entro en lo que haya encontrado.", "¿Dónde estoy ahora?", "new_location", "dynamic"),
    ("Regreso a la cueva.", "¿Puedo volver a ese sitio?", "connection_check", "si"),
    ("Vuelvo al bosque.", "¿Dónde estoy?", "location", "bosque"),
    ("¿Cómo llego a la herrería desde aquí?", "¿Qué lugares cruzo?", "route", "plaza→herreria"),
    ("¿Quién me afiló la espada?", "¿Cuánto le pagué?", "relation_memory", "bron"),
    ("¿Qué sitios nuevos conocí?", "¿Cuántos son?", "expansion_memory", "dynamic"),
    ("Cuéntame la aventura completa.", "¿Qué fue lo más importante?", "event_memory", "goblin"),
    ("Reviso todo mi equipo.", "¿Qué llevo exactamente?", "inventory_full", "espada afilada,pocion de curacion"),
]

EVENTOS_CANONICOS_HOLDOUT3 = (
    "miró la taberna, habló con Goruk, fue a la plaza, bebió su poción, compró una poción a Elena por 10 de oro, "
    "fue a la herrería, pagó 5 de oro a Bron para afilar la espada, intentó ir al bosque sin conexión, volvió a la "
    "plaza, fue al bosque y a la cueva, combatió al goblin varias rondas, exploró la cueva buscando otra salida.")
ORO_CANONICO_HOLDOUT3 = "5 (15 iniciales − 10 de la poción)"

SRD_GOLD_HOLDOUT3 = {
    TEST_SEQUENCE_HOLDOUT3[11][0]: ["monster:brown-bear"],
    TEST_SEQUENCE_HOLDOUT3[17][0]: ["rule:the-environment"],
}
