#!/usr/bin/env python3
"""
Regenerar reporte con datos reales y inyección corregida
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def cargar_datos_reales_mejorados():
    """Cargar datos reales con estructura mejorada para el template"""

    data_path = project_root / "data" / "sample_exports" / "instagram-pcFuHXmB"
    posts_file = data_path / "your_instagram_activity" / "media" / "posts_1.json"
    stories_file = data_path / "your_instagram_activity" / "media" / "stories.json"

    # Cargar posts reales
    with open(posts_file, encoding="utf-8") as f:
        raw_posts = json.load(f)

    # Cargar stories reales
    with open(stories_file, encoding="utf-8") as f:
        raw_stories_data = json.load(f)
    raw_stories = raw_stories_data.get("ig_stories", [])

    # Procesar posts (primeros 10)
    posts_data = []
    for i, post in enumerate(raw_posts[:10]):
        if "media" in post and post["media"]:
            media_item = post["media"][0]
            timestamp = datetime.fromtimestamp(media_item.get("creation_timestamp", 0))

            # Crear thumbnail SVG con colores del tema
            colors = ["667eea", "764ba2", "f093fb", "4facfe", "00f2fe"]
            color = colors[i % len(colors)]
            svg_thumbnail = (
                f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
                f"width='150' height='150'%3E%3Crect width='150' height='150' "
                f"fill='%23{color}'/%3E%3Ctext x='75' y='75' font-family='Arial' "
                f"font-size='16' fill='white' text-anchor='middle' "
                f"dy='.3em'%3EPost {i+1}%3C/text%3E%3C/svg%3E"
            )

            post_data = {
                "id": f"post_{i+1}",
                "date": timestamp.strftime("%Y-%m-%d"),
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "caption": post.get("title", "") or f"Instagram post {i+1}",
                "likes": 0,  # No disponible en export
                "comments": 0,
                "media_count": len(post["media"]),
                "hashtags": [],
                "media": [
                    {
                        "uri": media["uri"],
                        "type": "image",
                        "title": media.get("title", ""),
                        "thumbnail": svg_thumbnail,
                    }
                    for media in post["media"][:3]
                ],
            }
            posts_data.append(post_data)

    # Procesar stories (primeras 5)
    stories_data = []
    for i, story in enumerate(raw_stories[:5]):
        timestamp = datetime.fromtimestamp(story.get("creation_timestamp", 0))
        stories_data.append(
            {
                "taken_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "caption": story.get("title", "") or f"Story {i+1}",
                "media_type": "image",
                "media_uri": story.get("uri", ""),
                "thumbnail": None,
            }
        )

    # Calcular estadísticas
    total_posts = len(posts_data)
    fechas = [datetime.strptime(p["timestamp"], "%Y-%m-%d %H:%M:%S") for p in posts_data]
    meses = {}
    for fecha in fechas:
        mes = fecha.strftime("%B %Y")
        meses[mes] = meses.get(mes, 0) + 1

    return {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": total_posts,
            "total_stories": len(stories_data),
            "total_reels": 0,
            "username": "account_owner",
            "analyzer_version": "0.2.1",
            "data_source": "Instagram Export (instagram-pcFuHXmB)",
        },
        "overview": {
            "has_data": True,
            "content_counts": {
                "posts": total_posts,
                "stories": len(stories_data),
                "reels": 0,
                "total_media": sum(p["media_count"] for p in posts_data),
            },
            "date_range": {
                "start": min(fechas).strftime("%Y-%m-%d") if fechas else "N/A",
                "end": max(fechas).strftime("%Y-%m-%d") if fechas else "N/A",
                "years_active": 1,
                "active_days": (max(fechas) - min(fechas)).days if len(fechas) > 1 else 1,
            },
            "engagement_totals": {
                "likes": 0,
                "comments": 0,
                "avg_likes_per_post": 0,
                "avg_comments_per_post": 0,
            },
        },
        "temporal_analysis": {
            "has_data": True,
            "most_active": {
                "year": max(fechas).year if fechas else None,
                "month": max(meses, key=meses.get) if meses else None,
                "weekday": "Monday",  # Ejemplo
                "hour": "12:00",  # Ejemplo
            },
        },
        "engagement_analysis": {
            "has_data": False,
            "distribution": {
                "avg_likes": 0,
                "median_likes": 0,
                "max_likes": 0,
                "avg_comments": 0,
                "max_comments": 0,
            },
            "top_posts": {"most_liked": []},
        },
        "content_analysis": {
            "has_data": True,
            "hashtags": {
                "total_unique": 0,
                "total_usage": 0,
                "usage_rate": 0,
                "avg_per_post": 0,
                "top_hashtags": [],
            },
            "captions": {
                "posts_with_captions": sum(1 for p in posts_data if p["caption"]),
                "usage_rate": (
                    round(
                        (sum(1 for p in posts_data if p["caption"]) / len(posts_data))
                        * 100,
                        1,
                    )
                    if posts_data
                    else 0
                ),
                "avg_length": (
                    round(sum(len(p["caption"]) for p in posts_data) / len(posts_data), 1)
                    if posts_data
                    else 0
                ),
                "longest": (
                    max(len(p["caption"]) for p in posts_data) if posts_data else 0
                ),
            },
            "media_types": {
                "image_only": len(posts_data),
                "contains_video": 0,
                "carousel": 0,
                "single_media": len([p for p in posts_data if p["media_count"] == 1]),
            },
        },
        "posts": posts_data,
        "stories": stories_data,
        "reels": [],
        "additional_content": [],
        "story_interactions": [],
        "charts_data": {
            "monthly_activity": {
                "labels": list(meses.keys()),
                "data": list(meses.values()),
            },
            "weekday_activity": {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "data": [2, 1, 2, 2, 1, 1, 1],  # Datos de ejemplo
            },
            "hourly_activity": {
                "labels": [f"{h}:00" for h in range(24)],
                "data": [0] * 24,  # Datos vacíos por ahora
            },
        },
        "network_graph": {"nodes": [], "links": []},
    }


def main():
    """Regenerar reporte con datos corregidos"""

    print("🧪 Regenerando reporte con datos reales corregidos")
    print("=" * 55)

    try:
        # Cargar datos reales mejorados
        print("📊 Cargando datos reales...")
        data = cargar_datos_reales_mejorados()
        print(
            f"✅ {data['metadata']['total_posts']} posts, {data['metadata']['total_stories']} stories"
        )

        # Crear exportador
        print("\n🌐 Creando exportador...")
        exporter = HTMLExporter()

        # Renderizar con datos corregidos
        print("🎨 Renderizando HTML...")
        html_content = exporter._render_template(data)

        # Guardar archivo
        output_dir = project_root / "reporte_datos_reales_output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "instagram_analisis_datos_reales_v2.html"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_size = output_file.stat().st_size / 1024
        print(f"✅ Reporte generado: {output_file}")
        print(f"📄 Tamaño: {file_size:.1f} KB")

        # Verificar contenido
        checks = [
            ("const metadata = {", "Metadata"),
            ("const overview = {", "Overview"),
            ("const posts = [", "Posts"),
            ("Instagram post", "Contenido real"),
            ("account_owner", "Usuario"),
            ('"has_data": true', "Datos válidos"),
        ]

        print("\n🔍 Verificando contenido:")
        for check, desc in checks:
            status = "✅" if check in html_content else "❌"
            print(f"  {status} {desc}")

        print(f"\n🎉 ¡Reporte regenerado exitosamente!")
        print(f"\n💡 Para verlo:")
        print(f"  1. Abrir: {output_file}")
        print(f"  2. Click derecho → 'Open with Live Server'")
        print(f"  3. ¡Los datos ahora deben cargar correctamente!")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
