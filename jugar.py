"""Jugar con el Dungeon Master multi-agente (v3 por defecto) desde la terminal, viendo qué hace cada agente.

Uso:
    python jugar.py                                   # v3, Ollama en http://localhost:11434
    python jugar.py --url http://<IP_DEL_SPARK>:11434
    python jugar.py --imagenes                        # v3 con imágenes de la escena (SDXL-Turbo)
    python jugar.py --sin-traza                       # solo la narración
    python jugar.py --notebook proyecto_final_v2.ipynb   # la v2 evaluada (congelada)

Carga el código del notebook (celdas hasta el wrapper del agente), así que siempre usa la misma
versión que el notebook. Requiere en Ollama: qwen2.5:latest y bge-m3.

Comandos dentro del juego:
    /grafo            guarda el grafo del mundo en grafo_partida.png
    /memoria          resumen del grafo (lugares creados, relaciones narrativas)
    /contexto <texto> qué recuperaría el grafo para ese texto (local search)
    /srd <consulta>   qué documentos del SRD recupera la consulta
    /estado           estado del jugador
    /traza on|off     activar/desactivar la traza
    /salir
"""
import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")   # v3: sin el flood de warnings de TensorFlow/CUDA
os.environ.setdefault("USE_TF", "0")                 # transformers no carga TensorFlow (no se usa)
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
import warnings
warnings.filterwarnings("ignore")
import argparse
import contextlib
import io
import json
import os

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--url", default=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
parser.add_argument("--notebook", default="proyecto_final_v3.ipynb")
parser.add_argument("--sin-traza", action="store_true")
parser.add_argument("--imagenes", action="store_true", help="v3: generar imágenes de la escena (SDXL-Turbo)")
parser.add_argument("--gpu-imagenes", default="cuda:1", help="dispositivo para SDXL-Turbo")
args = parser.parse_args()
os.environ.setdefault("PERSONAJES_PARTIDA", "personajes_partida")  # v3: fichas .md de los NPCs creados al jugar
if args.imagenes:  # se lee al ejecutar la celda del grafo de la v3
    os.environ["IMAGENES"], os.environ["IMAGE_DEVICE"] = "1", args.gpu_imagenes

# ── cargar el código del notebook hasta el wrapper del agente ───────────────
nb = json.load(open(args.notebook))
g = {}
print(f"Cargando {args.notebook} (Ollama: {args.url})...")
for c in nb["cells"]:
    if c["cell_type"] != "code":
        continue
    src = "".join(c["source"]).replace('OLLAMA_BASE_URL = "http://localhost:11434"', f'OLLAMA_BASE_URL = "{args.url}"')
    if c.get("id") == "wrapper-v2":
        src = src[:src.index("# Prueba rápida")]
    with contextlib.redirect_stdout(io.StringIO()):
        exec(src, g)
    if c.get("id") == "wrapper-v2":
        break

import matplotlib
matplotlib.use("Agg")  # en la terminal el grafo se guarda como imagen

dm = g["MultiAgentDM"](g["app_v2"])
traza = not args.sin_traza
print(__doc__.split("Comandos dentro del juego:")[1])
print(g["check_state"].invoke({}))

while True:
    try:
        accion = input("\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not accion or accion.lower().strip("/ .!") in ("salir", "exit", "quit", "fin"):
        break
    if accion == "/grafo":
        g["draw_graph"](titulo=f"Grafo tras {g['game_state']['turn']} jugadas")
        g["plt"].tight_layout()
        g["plt"].savefig("grafo_partida.png", dpi=120)
        g["plt"].close("all")
        print(f"Guardado grafo_partida.png ({g['G'].number_of_nodes()} entidades, {g['G'].number_of_edges()} relaciones)")
    elif accion == "/memoria":
        print(g["graph_summary"]())
    elif accion.startswith("/contexto"):
        print(g["graph_context"](accion[len("/contexto"):].strip() or g["game_state"]["location"]))
    elif accion.startswith("/srd"):
        consulta = accion[4:].strip()
        if not consulta:
            print("Uso: /srd <consulta>   (ej. /srd daño por caída)")
            continue
        for d in g["buscar_srd"](f"{g['reescribir_consulta'](consulta)} {consulta}"):  # igual que consultar_reglas
            print(f"  [{d['id']}] {d['text'][:200]}")
    elif accion == "/estado":
        print(g["check_state"].invoke({}))
    elif accion.startswith("/traza"):
        traza = accion.endswith("on")
        print(f"Traza {'activada' if traza else 'desactivada'}")
    else:
        print(f"\nDM: {dm.play(accion, traza=traza)}")
        if getattr(dm, "ultima_imagen", None):
            print(f"\n    [Imagen: {dm.ultima_imagen}]")
print("Fin de la partida.")
