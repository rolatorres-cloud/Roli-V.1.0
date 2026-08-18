"""
Fuente de temas/ideas para el contenido.
Empieza simple (lista manual / RSS) y se puede conectar después
a Google Trends, X API, o scraping de hashtags por plataforma.
"""
from datetime import datetime


def get_topic_candidates(niche: str, n: int = 3) -> list[str]:
    """
    Punto de entrada único. Cambia el cuerpo de esta función por:
      - una llamada a pytrends (Google Trends)
      - una consulta a una API de noticias deportivas
      - resultados recientes de tus propios análisis (ej. Algoritmo ROLI)
    Por ahora devuelve placeholders para que el pipeline sea probable end-to-end.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        f"Resultado/dato curioso de la jornada MLB del {today}",
        f"Comparativa de rendimiento: 2 equipos calientes en Liga MX",
        f"Explicación rápida de una estadística poco conocida (ej. WHIP, fatiga de abridor)",
    ][:n]
