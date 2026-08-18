"""
Gate de aprobación con un solo tap, vía bot de Telegram.
Flujo:
  1. send_for_approval() manda un mensaje con el preview + botones [Aprobar] [Rechazar]
  2. Un webhook/polling (approval_listener) recibe el callback y actualiza el status en DB

Por qué Telegram: la API de bots es gratuita, sin revisión de app, y los botones inline
dan aprobación de un tap desde el celular — encaja con "gate ligero".
"""
import requests
from core.config import config
from core import db

API_BASE = f"https://api.telegram.org/bot{config.telegram_bot_token}"


def send_for_approval(content_id: int):
    item = db.get_by_id(content_id)
    if not item:
        return

    warning = ""
    if item.get("media_path", "") and "_sandbox" in (item.get("media_path") or ""):
        warning = "\n\n⚠️ *Video SANDBOX* — no es apto para publicar, solo prueba el flujo."

    text = (
        f"📋 *Nuevo contenido para revisar* (#{item['id']})\n\n"
        f"*Plataforma:* {item['platform']}\n"
        f"*Tipo:* {item['content_type']}\n"
        f"*Tema:* {item['topic']}\n\n"
        f"*Caption:*\n{item['caption']}\n\n"
        f"*Hashtags:* {item['hashtags']}"
        f"{warning}"
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Aprobar", "callback_data": f"approve:{content_id}"},
            {"text": "❌ Rechazar", "callback_data": f"reject:{content_id}"},
        ]]
    }

    requests.post(f"{API_BASE}/sendMessage", json={
        "chat_id": config.telegram_chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard,
    })

    db.update_status(content_id, "pending_approval")


def handle_callback(callback_data: str):
    """Llamar desde tu listener/webhook de Telegram cuando llega un callback_query."""
    action, content_id = callback_data.split(":")
    content_id = int(content_id)

    if action == "approve":
        db.update_status(content_id, "approved")
    elif action == "reject":
        db.update_status(content_id, "rejected")


def poll_updates(offset=None):
    """
    Long-polling simple para desarrollo/local. En producción usa un webhook.
    Devuelve el próximo offset a usar.
    """
    resp = requests.get(f"{API_BASE}/getUpdates", params={"offset": offset, "timeout": 30})
    updates = resp.json().get("result", [])

    for u in updates:
        cq = u.get("callback_query")
        if cq:
            handle_callback(cq["data"])
        offset = u["update_id"] + 1

    return offset
