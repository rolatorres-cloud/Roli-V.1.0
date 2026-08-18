# Social Bot — Scaffold

Pipeline: **tema → guion/caption (Claude) → [media] → gate de aprobación (Telegram, 1 tap) → publicación**

## Estructura
```
social-bot/
├── core/
│   ├── config.py       # API keys, nicho, horarios
│   ├── db.py            # cola de contenido (SQLite)
│   └── approval.py      # gate de aprobación vía Telegram
├── generators/
│   ├── trends.py         # fuente de temas/ideas
│   ├── copywriter.py     # genera guion/caption con Claude
│   └── media.py           # STUB — conecta tu API de imagen/video
├── publishers/
│   └── social.py          # publicación en Instagram (funcional) / TikTok (stub)
├── data/                    # se crea solo (db + media)
└── main.py                  # orquestador
```

## Setup

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Variables de entorno necesarias:
   ```bash
   export ANTHROPIC_API_KEY="..."        # generación de guion/copy
   export KLING_API_KEY="..."            # generación de video — cuenta en klingai.com
   export TELEGRAM_BOT_TOKEN="..."       # gate de aprobación — habla con @BotFather
   export TELEGRAM_CHAT_ID="..."         # tu chat id (usa @userinfobot para obtenerlo)
   export META_ACCESS_TOKEN="..."        # Instagram/Facebook Graph API
   export IG_BUSINESS_ACCOUNT_ID="..."
   ```

3. Crear tu bot de Telegram (2 minutos):
   - Habla con `@BotFather` en Telegram → `/newbot` → te da el token
   - Manda un mensaje a tu bot y consulta `https://api.telegram.org/bot<TOKEN>/getUpdates`
     para obtener tu `chat_id`

## Uso

```bash
# Genera contenido nuevo y lo manda a tu Telegram para aprobar
python main.py generate

# Escucha los taps de Aprobar/Rechazar (déjalo corriendo)
python main.py listen

# Publica todo lo que ya está 'approved'
python main.py publish
```

## Modo Sandbox (gratis) vs Producción (Kling, de paga)

El proyecto arranca en **modo sandbox por defecto** — no gasta nada, no requiere ninguna
API de video. `generators/media_sandbox.py` genera un `.mp4` local con FFmpeg (fondo de
color + el guion como texto en pantalla), solo para poder probar el pipeline completo:
generación → aprobación por Telegram → (bloqueo de publicación real).

- Los videos sandbox llevan la marca "SANDBOX - no publicar" y el sistema **bloquea
  automáticamente** su publicación en `main.py publish`, como seguro extra.
- El mensaje de aprobación en Telegram también avisa cuando el contenido es sandbox.

Cuando el resto del sistema (copy, aprobación, timing) ya funcione bien y quieras
video real generado por IA:

```bash
export VIDEO_PROVIDER=kling
export KLING_API_KEY="..."
```

Y automáticamente `generators/media.py` enruta a Kling en vez del sandbox — no hay que
tocar `main.py` ni ningún otro archivo.

## Generación de video — Kling AI (producción)

`generators/media_kling.py` está conectado a la API de Kling (texto→video e imagen→video):
1. Crea cuenta en klingai.com y genera tu `KLING_API_KEY`
2. El pipeline manda el guion como prompt, hace polling del task, y descarga el .mp4 a `data/media/`
3. Se activa automáticamente en cuanto pones `VIDEO_PROVIDER=kling`

Nota: el prompt que se le manda a Kling es el guion completo. Si tus guiones son muy
largos o muy "hablados", conviene generar antes un prompt visual corto (una frase describiendo
la escena) con el LLM, en vez de pasarle el guion tal cual.

## Lo que falta conectar (a propósito, son decisiones tuyas)

- **`publishers/social.py: publish_tiktok`** — requiere aprobación de TikTok Content Posting API
- **Hosting de medios** — Instagram exige una URL pública del archivo (no una ruta local),
  así que necesitas subir el .mp4 generado por Kling a algún storage (S3, Cloudinary, etc.)
  antes de publicar
- **Scheduler real** — reemplaza la ejecución manual por APScheduler o un cron que llame
  `generate` y `publish` según `config.preferred_hours`

## Por qué el gate de aprobación

Publicar 100% a ciegas es la forma más rápida de que una plataforma marque la cuenta como
spam/bot, además de que un guion mal generado se publica sin que nadie lo vea. Un tap en
Telegram añade fricción mínima pero te da control real, sobre todo mientras calibras el
tono y la calidad del contenido generado.
