"""
Un publicador por plataforma. Todos exponen publish(content_dict) -> post_id | None.
Cada plataforma requiere que tu app esté aprobada/registrada en su developer portal.
"""
import requests
from core.config import config


def publish_instagram(item: dict) -> str | None:
    """
    Requiere: cuenta de Instagram Business/Creator vinculada a una Página de Facebook,
    y un token de larga duración con permisos instagram_content_publish.
    Flujo real (Graph API):
      1. POST /{ig-user-id}/media  (crea el contenedor con media_url + caption)
      2. POST /{ig-user-id}/media_publish  (publica el contenedor creado)
    """
    if not config.meta_access_token:
        raise RuntimeError("Falta META_ACCESS_TOKEN")

    base = f"https://graph.facebook.com/v20.0/{config.ig_business_account_id}"

    container = requests.post(f"{base}/media", data={
        "image_url": item.get("media_url"),   # debe ser una URL pública, no ruta local
        "caption": f"{item['caption']}\n\n{item['hashtags']}",
        "access_token": config.meta_access_token,
    }).json()

    if "id" not in container:
        raise RuntimeError(f"Error creando contenedor: {container}")

    publish = requests.post(f"{base}/media_publish", data={
        "creation_id": container["id"],
        "access_token": config.meta_access_token,
    }).json()

    return publish.get("id")


def publish_tiktok(item: dict) -> str | None:
    """
    Requiere acceso aprobado a TikTok Content Posting API (proceso de revisión de app).
    Ver: https://developers.tiktok.com/doc/content-posting-api-get-started
    """
    raise NotImplementedError("Conecta aquí TikTok Content Posting API")


PUBLISHERS = {
    "instagram": publish_instagram,
    "tiktok": publish_tiktok,
}


def publish(item: dict) -> str | None:
    fn = PUBLISHERS.get(item["platform"])
    if not fn:
        raise ValueError(f"Plataforma no soportada: {item['platform']}")
    return fn(item)
