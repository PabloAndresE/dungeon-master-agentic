# Proyecto Final NLP — Dungeon Master con LangGraph

## Contexto del proyecto
- **Curso**: NLP (MMIA 6021 4889), profesor Diego Villacreses
- **Fecha de entrega**: 16 de octubre 2026
- **Presentación**: 5 min + 3 min Q&A
- **Estudiante**: Pablo Encalada

## Qué es esto
Un Dungeon Master de D&D que compara tres enfoques:
1. **Baseline**: LLM directo (chat sin estado)
2. **Agente v1**: LangGraph con 1 nodo agente + herramientas + estado externo
3. **Multi-agente v2**: LangGraph con 3 nodos especializados (Narrator, WorldBuilder, CoherenceChecker) + mundo dinámico que se expande
4. **v3 (futuro)**: v2 + generación de imágenes con Stable Diffusion

## Archivos

```
Proyecto Final/
├── proyecto_final.ipynb          # v1 — EJECUTADO Y LISTO, es el entregable principal
├── proyecto_final_v2.ipynb       # v2 — multi-agente, CREADO PERO NO EJECUTADO AÚN
├── proyecto_final_backup.ipynb   # backup de v1
├── proyecto_final_executed.ipynb # copia de ejecución de v1
└── CLAUDE.md                     # este archivo
```

## Resultados de v1 (ya ejecutado, final)

| Métrica | Baseline | Agente v1 |
|---------|----------|-----------|
| Keywords (binaria) | 22/25 (88%) | 22/25 (88%) |
| Juez ≥ 75 (binaria) | 17/25 (68%) | 22/25 (88%) |
| **Nota promedio juez** | **70.6** | **90.5** |
| Tiempo total | 820s | 916s |

El agente gana por +20 puntos. La ventaja viene de herramientas que anclan respuestas a estado real (check_state, move_to, attack_enemy). El baseline "inventa" cuando no recuerda.

Turnos donde el agente domina: movimiento ilegal (6-7), HP tras combate (10), navegación con reglas (23-24), memoria de eventos (17).

## Arquitectura v2 (multi-agente)

### Grafo LangGraph
```
START → narrator → narrator_tools → narrator (loop)
                 → world_builder → wb_tools → world_builder (loop)
                                 → coherence → narrator
                 → END
```

### 3 nodos especializados
- **Narrator** (temp=0.7): narra, usa check_state/move_to/attack/etc. Si detecta exploración nueva, emite `[EXPANDIR_MUNDO]`
- **WorldBuilder** (temp=0.9): crea ubicaciones/NPCs/items con create_location, create_npc, create_item
- **CoherenceChecker** (temp=0.1): valida que la expansión sea consistente

### Herramientas nuevas en v2
- `create_location(name, description, connected_to)` — crea ubicación, conecta bidireccionalmente
- `create_npc(name, description, location, hostile)` — crea NPC
- `create_item(name, description, location)` — coloca objeto

### Secuencia de prueba v2
25 turnos: los primeros 11 son iguales a v1, luego turnos 12-21 provocan expansión dinámica ("busco puerta escondida", "busco sendero oculto", etc.), y turnos 22-25 evalúan memoria de las expansiones.

## Configuración del LLM

### Para Ollama local (Mac)
```python
OLLAMA_MODEL = "qwen2.5:latest"  # 7B
OLLAMA_BASE_URL = "http://localhost:11434"
```

### Para el server Nvidia Spark
```python
OLLAMA_MODEL = "qwen2.5:72b"  # o 32b si 72b no cabe
OLLAMA_BASE_URL = "http://<IP_DEL_SPARK>:11434"
```
En el Spark:
```bash
ollama pull qwen2.5:72b
```
Solo hay que cambiar esas 2 líneas en la celda `config-v2` (o `heze5091kjn` en v1).

## Evaluación (cómo funciona)

### Método 1: Keywords (binario)
Busca patrones en la respuesta (ubicación correcta, inventario, movimiento ilegal bloqueado, etc.). Rápido pero superficial.

### Método 2: LLM-as-judge con logprobs (patrón Semana 2 Clase 3)
- Juez: mismo modelo, escala 0-4, system prompt "responde solo con un dígito"
- Se usa `OpenAI(base_url="http://...:11434/v1")` con `logprobs=True, top_logprobs=10, max_tokens=1`
- Se extraen probabilidades de tokens "0","1","2","3","4"
- Nota = valor_esperado × 25 (da 0-100 continuo)
- Esto replica EXACTAMENTE el patrón de la clase

## Técnicas del curso usadas
- **Semana 1**: prompting, system prompts
- **Semana 2 Clase 3**: LLM-as-judge con logprobs
- **Semana 3**: LangChain, herramientas, @tool decorator
- **Semana 3-4**: LangGraph, StateGraph, ReAct pattern (Yao et al. 2023)
- **Semana 3 Clase 4**: RAGAS (mencionado como referencia, no usado directamente porque no es RAG)

## Errores conocidos y soluciones

1. **`StdinNotImplementedError` en demo interactiva**: `input()` no funciona en batch. La demo está wrapeada en función que no se llama por defecto.

2. **Baseline puede ganar si la secuencia no tiene turnos de reglas/estado**: qwen2.5:7B es muy capaz narrativamente. La diferencia se ve en movimiento ilegal, HP, inventario.

3. **`num_ctx` bajo perjudica al agente**: los tool schemas consumen ~500 tokens del contexto. Con num_ctx=2048 o 4096, el agente pierde. Solución: usar contexto completo.

4. **Timeout en ejecución larga**: 25 turnos × 2-3 sistemas puede tardar >15 min por celda. Usar `--ExecutePreprocessor.timeout=3600`.

## Cómo ejecutar

```bash
# Ejecutar v1 (ya está ejecutado, solo si necesitas re-ejecutar)
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 \
  --ExecutePreprocessor.kernel_name=python3 \
  proyecto_final.ipynb --output proyecto_final_executed.ipynb

# Ejecutar v2 (aún no ejecutado)
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=3600 \
  --ExecutePreprocessor.kernel_name=python3 \
  proyecto_final_v2.ipynb --output proyecto_final_v2_executed.ipynb

# Luego copiar el ejecutado como entregable
cp proyecto_final_v2_executed.ipynb proyecto_final_v2.ipynb
```

## Dependencias Python
```
langchain-ollama langchain-core langgraph openai pandas matplotlib
```
pip install:
```bash
pip install langchain-ollama langchain-core langgraph openai pandas matplotlib
```

## Pendiente
- [ ] Ejecutar v2 (no se completó localmente, mover al Spark)
- [ ] Actualizar conclusiones de v2 tras ejecución
- [ ] Verificar que las gráficas de v2 se ven bien
- [ ] Implementar v3 con generación de imágenes
- [ ] Preparar presentación (5 min)

## Plan v3: Multi-agente + Generación de Imágenes

### Idea
Cada vez que el jugador entra a una nueva ubicación o ocurre un evento importante (combate, descubrimiento, NPC nuevo), el sistema genera una imagen ilustrativa. Esto transforma la experiencia de texto puro a una aventura visual.

### Arquitectura v3
```
START → narrator → narrator_tools → narrator (loop)
                 → world_builder → wb_tools → coherence → narrator
                 → image_generator → narrator
                 → END
```

Nuevo nodo **ImageGenerator**: se activa cuando el Narrator detecta un momento visual clave.

### Implementación propuesta

#### Opción A: Stable Diffusion local (recomendada para el Spark)
```python
from diffusers import StableDiffusionXLPipeline
import torch

pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
).to("cuda")

def generate_scene_image(description: str, style: str = "fantasy art") -> str:
    """Genera imagen de una escena y la guarda como archivo."""
    prompt = f"{style}, medieval fantasy RPG, {description}, detailed, atmospheric lighting"
    negative = "text, watermark, blurry, modern, sci-fi"
    image = pipe(prompt, negative_prompt=negative, num_inference_steps=25).images[0]
    path = f"images/scene_{int(time.time())}.png"
    image.save(path)
    return path
```

#### Opción B: Ollama multimodal (si hay modelo vision disponible)
Usar un modelo como LLaVA para describir → no genera imágenes, descartado.

#### Opción C: API externa (DALL-E, Midjourney)
```python
# Si se quiere usar OpenAI DALL-E
from openai import OpenAI
client_img = OpenAI(api_key="...")
response = client_img.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024")
```

### Herramienta nueva para v3
```python
@tool
def generate_image(scene_description: str) -> str:
    """Genera una imagen de la escena actual.
    Usa esto cuando el jugador llega a un lugar nuevo, descubre algo,
    o hay un evento visual importante (combate, tesoro, NPC)."""
    prompt = f"fantasy RPG scene, {scene_description}, digital painting, dramatic lighting"
    image = pipe(prompt, num_inference_steps=25).images[0]
    path = f"images/scene_{len(os.listdir('images'))+1}.png"
    image.save(path)
    return f"Imagen generada: {path}"
```

### Cuándo generar imágenes (triggers)
El Narrator incluye `[GENERAR_IMAGEN]` (similar a `[EXPANDIR_MUNDO]`) cuando:
1. El jugador llega a una ubicación **nueva** (dinámica o primera vez)
2. Ocurre un **combate**
3. Se descubre un **objeto o tesoro** importante
4. Aparece un **NPC nuevo**
5. El jugador lo pide ("describe cómo se ve esto")

### Modelo recomendado en el Spark (128GB)
- **SDXL Base** (~7GB VRAM): buena calidad, ~5-10 seg/imagen
- **SDXL Turbo** (~5GB VRAM): más rápido (~2 seg/imagen), calidad aceptable
- Alternativa: **Flux.1-schnell** si hay soporte

### Dependencias adicionales para v3
```bash
pip install diffusers transformers accelerate torch
# Descargar modelo (~7GB)
python -c "from diffusers import StableDiffusionXLPipeline; StableDiffusionXLPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0')"
```

### Evaluación v3
Además de las métricas de v1/v2, agregar:
- **Imágenes generadas por partida**: ¿cuántas escenas se ilustraron?
- **Relevancia visual** (LLM-as-judge): ¿la imagen corresponde a la escena descrita?
- **Tiempo de generación**: overhead por imagen
- Mostrar las imágenes inline en el notebook con `IPython.display.Image`

## Decisiones de diseño clave
- Mismo modelo para todo (narrator, world_builder, coherence, juez) — solo cambia temperatura y system prompt
- El mundo es un dict mutable en Python, no en el contexto del LLM
- Las herramientas de expansión registran `dynamic: True` para rastrear qué fue creado vs predefinido
- El CoherenceChecker usa temp=0.1 para ser determinista
- El WorldBuilder usa temp=0.9 para ser creativo
