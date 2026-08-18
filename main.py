"""
Orquestador del pipeline completo.

Ejecuta en dos modos:
  python main.py generate   -> crea contenido nuevo y lo manda a aprobación (Telegram)
  python main.py publish    -> revisa lo 'approved' y lo publica
  python main.py listen     -> escucha los taps de aprobación/rechazo (dev, polling)

En producción, corre 'generate' y 'publish' con un scheduler (ej. cron, APScheduler)
según config.preferred_hours, y 'listen' como proceso/webhook siempre activo.
"""
import sys
from core import db
from core.config import config
from core.approval import send_for_approval, poll_updates
from generators.trends import get_topic_candidates
from generators.copywriter import generate_content
from generators.media import generate_video
from publishers.social import publish


def run_generate():
    db.init_db()
    topics = get_topic_candidates(config.niche, n=config.posts_per_day)

    for topic in topics:
        content_type = "video"  # o alterna video/post según tu mezcla deseada
        generated = generate_content(topic, content_type)

        content_id = db.create_content(
            content_type=content_type,
            platform=config.platforms[0],
            topic=topic,
            caption=f"{generated['hook']}\n\n{generated['caption']}\n\n{generated['cta']}",
            script=generated["script"],
            hashtags=generated["hashtags"],
        )

        try:
            media_path = generate_video(generated["script"], content_id)
            db.update_status(content_id, "draft", media_path=media_path)
        except Exception as e:
            print(f"#{content_id}: no se pudo generar video ({e}). Se manda a aprobar sin media.")

        send_for_approval(content_id)
        print(f"Contenido #{content_id} generado y enviado a aprobación.")


def run_publish():
    approved = db.get_by_status("approved")
    for item in approved:
        if "_sandbox" in (item.get("media_path") or ""):
            print(f"#{item['id']}: es contenido SANDBOX, no se publica. Cambia VIDEO_PROVIDER=kling para producción.")
            continue
        try:
            post_id = publish(item)
            db.update_status(item["id"], "published", meta_json=str({"post_id": post_id}))
            print(f"#{item['id']} publicado -> {post_id}")
        except Exception as e:
            db.update_status(item["id"], "failed")
            print(f"#{item['id']} falló: {e}")


def run_listen():
    print("Escuchando aprobaciones de Telegram (Ctrl+C para salir)...")
    offset = None
    while True:
        offset = poll_updates(offset)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"
    {"generate": run_generate, "publish": run_publish, "listen": run_listen}.get(
        cmd, lambda: print("Uso: python main.py [generate|publish|listen]")
    )()
