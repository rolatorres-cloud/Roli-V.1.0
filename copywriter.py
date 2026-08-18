"""
Convierte un tema en contenido publicable: guion (para video) o caption (para post).
Usa la API de Anthropic. Requiere ANTHROPIC_API_KEY en el entorno.
"""
import json
import anthropic
from core.config import config

client = anthropic.Anthropic(api_key=config.anthropic_api_key)

SYSTEM_PROMPT = """Eres un guionista de contenido para redes sociales especializado en {niche}.
Tono: {tone}.
Devuelve SIEMPRE únicamente un JSON válido, sin texto adicional ni markdown, con este esquema:
{{
  "hook": "primera línea que detiene el scroll (máx 12 palabras)",
  "script": "guion completo si es video (30-45s hablado), o cuerpo del post si es texto",
  "caption": "caption corto para la publicación (máx 2 líneas)",
  "hashtags": "5-8 hashtags relevantes separados por espacio",
  "cta": "llamado a la acción final"
}}"""


def generate_content(topic: str, content_type: str = "video") -> dict:
    system = SYSTEM_PROMPT.format(niche=config.niche, tone=config.tone)
    user_msg = f"Tipo de contenido: {content_type}\nTema: {topic}"

    response = client.messages.create(
        model=config.anthropic_model,
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = response.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback simple si el modelo no devolvió JSON limpio
        return {
            "hook": topic[:60],
            "script": raw,
            "caption": raw[:150],
            "hashtags": "",
            "cta": "",
        }
