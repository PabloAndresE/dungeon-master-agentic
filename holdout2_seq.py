# ────────────────────────────────────────────────────────────────────────────
# Secuencia HOLD-OUT 2 — escrita ANTES de aplicar los arreglos post-hold-out-1
# ────────────────────────────────────────────────────────────────────────────
# La secuencia hold-out 1 se "gastó": sus fallos guiaron los arreglos de v2. Esta segunda secuencia
# no se usó para ajustar nada y da el número final de generalización. Otro vocabulario de acciones
# ("Agarro", "Me dirijo", "Camino hasta", "Sigo hacia", "Paso a", "Me curo"), otro recorrido y otras
# preguntas de reglas (lobo, esqueleto, bolsa de contención, cobertura).

TEST_SEQUENCE_HOLDOUT2 = [
    ("Echo un vistazo a mi alrededor.", "¿Qué objetos veo por aquí?", "item_mention", "antorcha"),
    ("Agarro la antorcha.", "¿Qué tengo encima?", "inventory", "antorcha"),
    ("Charlo con Goruk el tabernero.", "¿Qué me contó Goruk?", "relation_memory", "goruk"),
    ("Me dirijo al bosque.", "¿Dónde estoy?", "location", "bosque"),
    ("Intento ir a la herrería desde aquí.", "¿Llegué a la herrería?", "illegal_move", "herreria"),
    ("Cojo las hierbas medicinales.", "¿Qué llevo ahora?", "inventory", "hierbas"),
    # SRD 1: criatura (SRD: Wolf CA 13, PG 11, mordida 2d4+2 + salvación FUE CD 11 o derribado)
    ("Según las reglas, ¿qué estadísticas tiene un lobo?", "¿Qué pasa si me muerde?", "srd", "13,11"),
    ("Me adentro en la cueva.", "¿Dónde me encuentro?", "location", "cueva"),
    ("Lucho contra el goblin.", "¿Cuántos puntos de vida tengo?", "hp_mentioned", "hp"),
    ("Recojo el oro del cofre.", "¿Cuánto oro tengo ahora?", "gold_change", "gold"),
    ("Exploro un rincón oscuro de la cueva por si hay un túnel.", "¿Descubrí algo?", "expansion", "nuevo"),
    ("Atravieso lo que acabo de descubrir.", "¿En qué lugar estoy?", "new_location", "dynamic"),
    # SRD 2: criatura (SRD: Skeleton CA 13, PG 13, inmune al veneno)
    ("Según las reglas, ¿cuántos puntos de golpe tiene un esqueleto?", "¿Es inmune a algo?", "srd", "13,venen"),
    ("Regreso a la cueva.", "¿Puedo volver a ese lugar nuevo?", "connection_check", "si"),
    ("Camino hasta el bosque.", "¿Dónde estoy?", "location", "bosque"),
    ("Sigo hacia la plaza.", "¿Dónde estoy ahora?", "location", "plaza"),
    ("Busco algún forastero en la plaza al que no conozca.", "¿Hay alguien nuevo?", "npc_creation", "nuevo"),
    # SRD 3: objeto (SRD: Bag of Holding, hasta 500 libras, 64 pies cúbicos, pesa 15 libras)
    ("¿Qué hace exactamente una bolsa de contención según las reglas?", "¿Cuánto peso aguanta?", "srd", "500"),
    ("Me curo con la poción.", "¿Todavía tengo la poción?", "potion_used", "pocion"),
    ("Paso a la herrería.", "¿Dónde estoy?", "location", "herreria"),
    # SRD 4: regla (SRD: Cover — media cobertura +2 a CA, tres cuartos +5)
    ("Según las reglas, ¿cuánto ayuda estar detrás de media cobertura?", "¿Y si la cobertura es de tres cuartos?",
     "srd", "+2,+5"),
    ("¿Cómo vuelvo a la cueva desde aquí?", "¿Qué lugares atravieso?", "route", "plaza→bosque→cueva"),
    ("¿Quién me advirtió del bosque?", "¿Con qué palabras?", "relation_memory", "goruk"),
    ("Reviso todo lo que llevo.", "¿Qué tengo exactamente?", "inventory_full",
     "espada oxidada,antorcha,hierbas medicinales"),
    ("¿Cuántos sitios nuevos encontré?", "¿Cuáles son?", "expansion_memory", "dynamic"),
    ("Hazme un resumen de la aventura.", "¿Qué fue lo más importante?", "event_memory", "goblin"),
]

EVENTOS_CANONICOS_HOLDOUT2 = (
    "miró la taberna, tomó la antorcha, habló con Goruk (advirtió sobre el bosque), fue al bosque, intentó ir "
    "a la herrería sin conexión, recogió hierbas medicinales, fue a la cueva, luchó contra el goblin, tomó 50 "
    "monedas del cofre, exploró buscando un túnel, volvió al bosque y a la plaza, buscó a un forastero, usó la "
    "poción de curación, fue a la herrería.")

SRD_GOLD_HOLDOUT2 = {
    TEST_SEQUENCE_HOLDOUT2[6][0]: ["monster:wolf"],
    TEST_SEQUENCE_HOLDOUT2[12][0]: ["monster:skeleton"],
    TEST_SEQUENCE_HOLDOUT2[17][0]: ["magic_item:bag-of-holding"],
    TEST_SEQUENCE_HOLDOUT2[20][0]: ["rule:cover"],
}
