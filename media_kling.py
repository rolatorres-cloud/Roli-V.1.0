"""
Generación de medios. Video vía Kling AI (API oficial, key simple).
Flujo Kling: POST crea el task -> polling de status -> descarga del video final.
Docs: https://klingai.com (video generation API)
"""
import time
import requests
from pathlib import Path
from core.config import config

MEDIA_DIR = Path(__file__).parent.parent / "data" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

_HEADERS = {
    "Authorization": f"Bearer {config.kling_api_key}",
    "Content-Type": "application/json",
}


def _poll_task(task_id: str, endpoint: str) -> dict:
    """Hace polling a un task de Kling hasta que termine o expire el timeout."""
    url = f"{config.kling_base_url}{endpoint}/{task_id}"
    elapsed = 0

    while elapsed < config.kling_poll_timeout_seconds:
        resp = requests.get(url, headers=_HEADERS)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("task_status") or data.get("status")
        if status in ("succeed", "completed", "success"):
            return data
        if status in ("failed", "error"):
            raise RuntimeError(f"Kling task {task_id} falló: {data}")

        time.sleep(config.kling_poll_interval_seconds)
        elapsed += config.kling_poll_interval_seconds

    raise TimeoutError(f"Kling task {task_id} no terminó tras {config.kling_poll_timeout_seconds}s")


def _download(video_url: str, content_id: int) -> str:
    resp = requests.get(video_url, stream=True)
    resp.raise_for_status()
    path = MEDIA_DIR / f"{content_id}.mp4"
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return str(path)


def kling_generate_video(script: str, content_id: int, aspect_ratio: str = "9:16") -> str:
    """
    Texto -> video vía Kling. `script` se usa como prompt visual; si tu guion es muy largo
    (hablado), considera generar primero un prompt visual corto con el LLM antes de pasarlo aquí.
    """
    if not config.kling_api_key:
        raise RuntimeError("Falta KLING_API_KEY")

    resp = requests.post(
        f"{config.kling_base_url}/v1/videos/text2video",
        headers=_HEADERS,
        json={
            "model": config.kling_model,
            "prompt": script,
            "duration": 5,
            "aspect_ratio": aspect_ratio,
            "mode": "professional",
        },
    )
    resp.raise_for_status()
    task_id = resp.json()["task_id"]

    result = _poll_task(task_id, "/v1/videos/text2video")
    video_url = result["videos"][0]["url"]  # estructura típica de respuesta de Kling
    return _download(video_url, content_id)


def kling_generate_video_from_image(image_path_or_url: str, prompt: str, content_id: int) -> str:
    """Imagen -> video, útil si partes de una foto/miniatura base."""
    if not config.kling_api_key:
        raise RuntimeError("Falta KLING_API_KEY")

    resp = requests.post(
        f"{config.kling_base_url}/v1/videos/image2video",
        headers=_HEADERS,
        json={
            "model": config.kling_model,
            "image": image_path_or_url,  # Kling acepta URL pública o base64 según el endpoint
            "prompt": prompt,
            "duration": 5,
        },
    )
    resp.raise_for_status()
    task_id = resp.json()["task_id"]

    result = _poll_task(task_id, "/v1/videos/image2video")
    video_url = result["videos"][0]["url"]
    return _download(video_url, content_id)


def kling_generate_image(prompt: str, content_id: int) -> str:
    """
    TODO: conecta tu proveedor de imagen preferido (Ideogram, Flux, etc.) si necesitas
    portadas/miniaturas separadas del video.
    """
    raise NotImplementedError("Conecta aquí tu proveedor de generación de imagen")
