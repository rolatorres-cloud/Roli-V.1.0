import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # --- LLM para generación de guiones/copy ---
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Generación de medios ---
    image_gen_api_key: str = os.getenv("IMAGE_GEN_API_KEY", "")   # ej. Ideogram / Flux
    kling_api_key: str = os.getenv("KLING_API_KEY", "")           # Kling AI — video
    tts_api_key: str = os.getenv("TTS_API_KEY", "")               # ej. ElevenLabs

    kling_base_url: str = "https://api.klingai.com"
    kling_model: str = "kling-v2.6-pro"
    kling_poll_interval_seconds: int = 8
    kling_poll_timeout_seconds: int = 300

    # --- Proveedor de video activo: "sandbox" (gratis, local, sin API) o "kling" (de paga) ---
    video_provider: str = os.getenv("VIDEO_PROVIDER", "sandbox")

    # --- Gate de aprobación vía Telegram (un tap) ---
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- Publicación ---
    meta_access_token: str = os.getenv("META_ACCESS_TOKEN", "")   # Instagram/Facebook Graph API
    ig_business_account_id: str = os.getenv("IG_BUSINESS_ACCOUNT_ID", "")
    tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")

    # --- Nicho / voz de marca ---
    niche: str = "deportes y análisis (MLB, LMB, Liga MX)"
    tone: str = "directo, con datos, cercano, sin relleno"
    platforms: list = field(default_factory=lambda: ["instagram", "tiktok"])

    # --- Programación ---
    posts_per_day: int = 2
    preferred_hours: list = field(default_factory=lambda: [12, 19])  # hora local


config = Config()
