"""Convierte el SRD 5e (5e-bits/5e-database, src/2014/en) en docs.jsonl para embeddings.
Uso: python -I build_docs.py [directorio_srd]
Atribucion: SRD 5.1 (c) Wizards of the Coast, CC-BY-4.0. Datos JSON: 5e-bits/5e-database (MIT).
"""
import json, sys
from fractions import Fraction
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)
MAX_DESC = 600  # recorta textos largos de accion/rasgo

def load(n): return json.load(open(D / f"5e-SRD-{n}.json", encoding="utf-8"))
def cut(s, n=MAX_DESC): s = " ".join(s.split()); return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."
def cr(x): return str(Fraction(x).limit_denominator(8))
def joind(d): return " ".join(d) if isinstance(d, list) else (d or "")

def monster(m):
    ac = m["armor_class"][0]["value"] if m.get("armor_class") else "?"
    typ = m["type"] + (f" ({m['subtype']})" if m.get("subtype") else "")
    spd = ", ".join(f"{k} {v}" for k, v in m.get("speed", {}).items())
    st = " ".join(f"{a[:3].upper()} {m[a]}" for a in ["strength","dexterity","constitution","intelligence","wisdom","charisma"])
    parts = [f"{m['name']}. {m['size']} {typ}, {m['alignment']}. CA {ac}, PG {m['hit_points']} ({m.get('hit_dice','')}), VD {cr(m['challenge_rating'])} ({m.get('xp',0)} XP). Velocidad: {spd}. {st}."]
    if m.get("languages"): parts.append(f"Idiomas: {m['languages']}.")
    if m.get("damage_immunities"): parts.append("Inmune: " + ", ".join(m["damage_immunities"]) + ".")
    for lab, key in [("Rasgos", "special_abilities"), ("Acciones", "actions"), ("Acciones legendarias", "legendary_actions")]:
        if m.get(key): parts.append(f"{lab}: " + " ".join(f"{a['name']}: {cut(a.get('desc',''), 250)}" for a in m[key]))
    if m.get("desc"): parts.append(cut(joind(m["desc"])))
    meta = {"cr": m["challenge_rating"], "type": m["type"], "size": m["size"], "alignment": m["alignment"],
            "hp": m["hit_points"], "ac": ac, "xp": m.get("xp")}
    return "monster", m, " ".join(parts), meta

def magic_item(i):
    rar = i.get("rarity", {}).get("name", "?"); cat = i["equipment_category"]["name"]
    return "magic_item", i, f"{i['name']}. Objeto magico ({cat}), rareza {rar}. {cut(joind(i['desc']), 1200)}", {"rarity": rar, "category": cat}

def equipment(e):
    cat = e["equipment_category"]["name"]; bits = [f"{e['name']}. Equipo ({cat})."]
    if e.get("cost"): bits.append(f"Coste {e['cost']['quantity']} {e['cost']['unit']}.")
    if e.get("weight"): bits.append(f"Peso {e['weight']} lb.")
    if e.get("damage"): bits.append(f"Dano {e['damage']['damage_dice']} {e['damage']['damage_type']['name']}.")
    if e.get("armor_class"): bits.append(f"CA base {e['armor_class']['base']}.")
    if e.get("properties"): bits.append("Propiedades: " + ", ".join(p["name"] for p in e["properties"]) + ".")
    if e.get("desc"): bits.append(cut(joind(e["desc"])))
    return "equipment", e, " ".join(bits), {"category": cat, "cost": e.get("cost")}

def spell(s):
    lvl = "truco" if s["level"] == 0 else f"nivel {s['level']}"
    t = (f"{s['name']}. Conjuro de {lvl}, escuela {s['school']['name']}. Tiempo {s['casting_time']}, alcance {s['range']}, "
         f"duracion {s['duration']}{', concentracion' if s.get('concentration') else ''}. Clases: {', '.join(c['name'] for c in s.get('classes', []))}. "
         f"{cut(joind(s['desc']), 900)}")
    return "spell", s, t, {"level": s["level"], "school": s["school"]["name"]}

def rule(r):
    return "rule", r, f"{r['name']}. Regla. {cut(r['desc'], 1500)}", {}

docs = []
for fname, fn in [("Monsters", monster), ("Magic-Items", magic_item), ("Equipment", equipment), ("Spells", spell), ("Rule-Sections", rule)]:
    for e in load(fname):
        typ, src, text, meta = fn(e)
        meta["source"] = "SRD 5.1 (CC-BY-4.0)"
        docs.append({"id": f"{typ}:{src['index']}", "type": typ, "name": src["name"], "text": text, "metadata": meta})

with open(D / "docs.jsonl", "w", encoding="utf-8") as f:
    for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
from collections import Counter
c = Counter(d["type"] for d in docs)
for t in c: print(t, c[t], "media chars:", round(sum(len(d["text"]) for d in docs if d["type"] == t) / c[t]))
print("TOTAL", len(docs), "media chars:", round(sum(len(d["text"]) for d in docs) / len(docs)))
