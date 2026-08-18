"""
Proveedor SANDBOX — 100% gratis, corre local, no requiere API key ni internet.
Genera un video placeholder (fondo + texto del guion) usando FFmpeg, para poder
probar el pipeline completo (generación -> aprobación -> publicación) sin gastar
en generación de video real mientras calibras el resto del sistema.

Cuando quieras video real con IA, cambia VIDEO_PROVIDER=kling en tu entorno.
"""
import subprocess
import textwrap
from pathlib import Path

MEDIA_DIR = Path(__file__).parent.parent / "data" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Paleta simple para que no todos los placeholders se vean idénticos
_BG_COLORS = ["1a1a2e", "16213e", "0f3460", "222831", "393e46"]


def _wrap_text(text: str, width: int = 32) -> str:
    """Envuelve el texto para que quepa en el video y escapa caracteres para FFmpeg."""
    wrapped = "\n".join(textwrap.wrap(text, width=width))
    return wrapped.replace(":", r"\:").replace("'", r"\'")


def sandbox_generate_video(script: str, content_id: int, duration: int = 6, aspect_ratio: str = "9:16") -> str:
    """
    Crea un .mp4 local con el guion superpuesto sobre un fondo de color sólido.
    No es contenido publicable — es SOLO para probar el flujo de datos end-to-end.
    """
    width, height = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
    color = _BG_COLORS[content_id % len(_BG_COLORS)]
    text = _wrap_text(script[:200])  # recorta para que no desborde el placeholder
    out_path = MEDIA_DIR / f"{content_id}_sandbox.mp4"

    drawtext = (
        f"drawtext=text='{text}':fontcolor=white:fontsize=42:"
        f"x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=12"
    )
    watermark = (
        "drawtext=text='SANDBOX - no publicar':fontcolor=yellow@0.8:fontsize=28:"
        "x=(w-text_w)/2:y=60"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=#{color}:s={width}x{height}:d={duration}",
        "-vf", f"{drawtext},{watermark}",
        "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(out_path)
