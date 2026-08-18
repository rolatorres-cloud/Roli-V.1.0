"""
Punto único de entrada para generación de medios. El resto del pipeline
(main.py) llama SIEMPRE a estas funciones — nunca a un proveedor específico
directamente — así cambiar de sandbox a producción es solo una variable de entorno.
"""
from core.config import config


def generate_video(script: str, content_id: int, aspect_ratio: str = "9:16") -> str:
    if config.video_provider == "kling":
        from generators.media_kling import kling_generate_video
        return kling_generate_video(script, content_id, aspect_ratio)

    from generators.media_sandbox import sandbox_generate_video
    return sandbox_generate_video(script, content_id, aspect_ratio=aspect_ratio)


def generate_video_from_image(image_path_or_url: str, prompt: str, content_id: int) -> str:
    if config.video_provider == "kling":
        from generators.media_kling import kling_generate_video_from_image
        return kling_generate_video_from_image(image_path_or_url, prompt, content_id)

    from generators.media_sandbox import sandbox_generate_video
    return sandbox_generate_video(prompt, content_id)


def generate_image(prompt: str, content_id: int) -> str:
    """Sin equivalente sandbox por ahora — requiere proveedor real (Kling, Ideogram, etc.)."""
    from generators.media_kling import kling_generate_image
    return kling_generate_image(prompt, content_id)
