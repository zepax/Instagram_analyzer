#!/usr/bin/env python3
"""
Prueba SIMPLE del exportador HTML con datos REALES
Usa directamente los archivos JSON de Instagram.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def cargar_datos_instagram_reales():
    """Carga datos reales de Instagram desde los archivos JSON"""

    data_path = project_root / "data" / "sample_exports" / "instagram-pcFuHXmB"

    # Cargar posts
    posts_file = data_path / "your_instagram_activity" / "media" / "posts_1.json"
    stories_file = data_path / "your_instagram_activity" / "media" / "stories.json"

    posts_data = []
    stories_data = []

    print(f"📂 Cargando datos desde: {data_path}")

    # Cargar posts
    if posts_file.exists():
        with open(posts_file, encoding="utf-8") as f:
            raw_posts = json.load(f)

        print(f"✅ Posts cargados: {len(raw_posts)} posts encontrados")

        # Procesar los primeros 10 posts para el reporte
        for i, post in enumerate(raw_posts[:10]):
            if "media" in post and post["media"]:
                media_item = post["media"][0]

                post_data = {
                    "id": f"post_{i+1}",
                    "timestamp": datetime.fromtimestamp(
                        media_item.get("creation_timestamp", 0)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "caption": post.get("title", "") or f"Post {i+1}",
                    "full_caption": post.get("title", "")
                    or f"Post {i+1} - contenido real de Instagram",
                    "likes": 0,  # No disponible en export
                    "comments": 0,  # No disponible en export
                    "media_count": len(post["media"]),
                    "hashtags": [],
                    "mentions": [],
                    "media": [],
                }

                # Agregar info de media
                for j, media in enumerate(post["media"][:3]):  # Máximo 3 por performance
                    # Crear thumbnail SVG simple con colores del tema
                    svg_thumbnail = (
                        f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
                        f"width='150' height='150'%3E%3Crect width='150' height='150' "
                        f"fill='%23{['667eea', '764ba2', 'f093fb'][j % 3]}'/%3E%3Ctext x='75' "
                        f"y='75' font-family='Arial' font-size='16' fill='white' "
                        f"text-anchor='middle' dy='.3em'%3EPost {i+1}.{j+1}%3C/text%3E%3C/svg%3E"
                    )

                    post_data["media"].append(
                        {
                            "uri": media.get("uri", ""),
                            "type": "image",  # Asumir imagen por defecto
                            "title": media.get("title", ""),
                            "thumbnail": svg_thumbnail,
                        }
                    )

                posts_data.append(post_data)

    # Cargar stories
    if stories_file.exists():
        with open(stories_file, encoding="utf-8") as f:
            raw_stories_data = json.load(f)

        # El archivo de stories tiene estructura: {"ig_stories": [...]}
        raw_stories = raw_stories_data.get("ig_stories", [])

        print(f"✅ Stories cargadas: {len(raw_stories)} stories encontradas")

        # Procesar las primeras 5 stories
        for i, story in enumerate(raw_stories[:5]):
            story_data = {
                "timestamp": datetime.fromtimestamp(
                    story.get("creation_timestamp", 0)
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "caption": story.get("title", "") or f"Story {i+1}",
                "media_uri": story.get("uri", ""),
                "media_type": "image",
            }

            stories_data.append(story_data)

    return posts_data, stories_data


def crear_reporte_datos_reales():
    """Crear estructura de reporte con datos reales"""

    posts_data, stories_data = cargar_datos_instagram_reales()

    # Calcular estadísticas básicas
    total_posts = len(posts_data)
    total_stories = len(stories_data)

    # Análisis temporal básico
    if posts_data:
        fechas = [
            datetime.strptime(p["timestamp"], "%Y-%m-%d %H:%M:%S") for p in posts_data
        ]
        meses = {}
        for fecha in fechas:
            mes = fecha.strftime("%B %Y")
            meses[mes] = meses.get(mes, 0) + 1
    else:
        meses = {}

    return {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": total_posts,
            "total_stories": total_stories,
            "total_reels": 0,
            "version": "0.2.1",
            "data_source": "instagram-pcFuHXmB (datos reales)",
        },
        "overview": {
            "total_posts": total_posts,
            "total_likes": 0,  # No disponible en export
            "total_comments": 0,  # No disponible en export
            "avg_likes_per_post": 0,
            "avg_comments_per_post": 0,
            "most_liked_post": posts_data[0] if posts_data else {},
            "posting_frequency": f"Datos de {len(meses)} meses" if meses else "Sin datos",
            "engagement_rate": "N/A (datos de export)",
        },
        "temporal_analysis": {
            "posts_by_month": meses,
            "posts_by_weekday": {},
            "posts_by_hour": {},
        },
        "engagement_analysis": {
            "likes_distribution": [],
            "comments_distribution": [],
            "engagement_by_post_type": {
                "photo": {"likes": 0, "comments": 0},
                "carousel": {"likes": 0, "comments": 0},
                "video": {"likes": 0, "comments": 0},
            },
            "peak_engagement_times": [],
        },
        "content_analysis": {
            "hashtags_frequency": {},
            "mentions_frequency": {},
            "caption_lengths": [len(p["caption"]) for p in posts_data],
            "avg_caption_length": (
                sum(len(p["caption"]) for p in posts_data) / len(posts_data)
                if posts_data
                else 0
            ),
        },
        "posts": posts_data,
        "stories": stories_data,
        "reels": [],
        "charts_data": {
            "temporal_analysis": {
                "labels": list(meses.keys())[:6],  # Últimos 6 meses
                "data": list(meses.values())[:6],
            },
            "engagement_analysis": {
                "labels": [f"Post {i+1}" for i in range(min(10, len(posts_data)))],
                "likes_data": [0] * min(10, len(posts_data)),  # No hay datos de likes
                "comments_data": [0]
                * min(10, len(posts_data)),  # No hay datos de comments
            },
            "hashtags_analysis": {"labels": [], "data": []},
        },
        "network_graph": {"nodes": [], "edges": []},
        "additional_content": [],
        "story_interactions": [],
    }


def test_exportador_datos_reales():
    """Test del exportador con datos reales de Instagram"""

    print("🧪 Test del Exportador HTML con DATOS REALES de Instagram")
    print("=" * 65)

    try:
        # Verificar que existe la carpeta de datos
        data_path = project_root / "data" / "sample_exports" / "instagram-pcFuHXmB"
        if not data_path.exists():
            print(f"❌ No se encontró la carpeta: {data_path}")
            return False

        print("✅ Carpeta de datos encontrada")

        # Crear exportador
        print("\n🌐 Creando exportador HTML...")
        exporter = HTMLExporter()
        print("✅ Exportador creado")

        # Generar datos del reporte
        print("\n📊 Procesando datos reales de Instagram...")
        report_data = crear_reporte_datos_reales()

        print(f"✅ Datos procesados:")
        print(f"  • Posts reales: {report_data['metadata']['total_posts']}")
        print(f"  • Stories reales: {report_data['metadata']['total_stories']}")
        print(f"  • Fuente: {report_data['metadata']['data_source']}")

        # Renderizar HTML
        print("\n🎨 Generando reporte HTML...")
        html_content = exporter._render_template(report_data)

        # Crear directorio de salida
        output_dir = project_root / "reporte_datos_reales_output"
        output_dir.mkdir(exist_ok=True)

        # Guardar archivo
        output_file = output_dir / "instagram_analisis_datos_reales.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_size = output_file.stat().st_size / 1024
        print(f"✅ Reporte generado: {output_file}")
        print(f"📄 Tamaño: {file_size:.1f} KB")

        # Verificaciones del HTML
        verificaciones = [
            ("<!DOCTYPE html>", "HTML válido"),
            ("Instagram Analysis Report", "Título correcto"),
            ("chart.js", "Chart.js incluido"),
            ("datos reales", "Datos reales procesados"),
            ("new Chart(", "Gráficos generados"),
            (str(report_data["metadata"]["total_posts"]), "Posts en HTML"),
        ]

        print(f"\n🔍 Verificando HTML generado:")
        checks_passed = 0
        for check, desc in verificaciones:
            if check in html_content:
                print(f"  ✅ {desc}")
                checks_passed += 1
            else:
                print(f"  ❌ {desc}")

        success_rate = (checks_passed / len(verificaciones)) * 100

        print(f"\n📈 Resultados:")
        print(
            f"  • Verificaciones: {checks_passed}/{len(verificaciones)} ({success_rate:.1f}%)"
        )
        print(f"  • Posts procesados: {report_data['metadata']['total_posts']}")
        print(f"  • Tamaño final: {file_size:.1f} KB")

        return success_rate >= 80  # 80% de éxito mínimo

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Función principal"""
    start_time = datetime.now()

    success = test_exportador_datos_reales()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n⏱️  Tiempo total: {duration:.2f} segundos")

    if success:
        print("\n🎉 ¡Test con datos reales EXITOSO!")
        print("\n💡 Para ver el reporte:")
        print("  1. Abrir VS Code Explorer")
        print("  2. Ir a reporte_datos_reales_output/")
        print("  3. Click derecho en instagram_analisis_datos_reales.html")
        print("  4. Seleccionar 'Open with Live Server'")
        print("  5. ¡Ver tu análisis de Instagram real!")
        return 0
    else:
        print("\n💥 Test falló")
        return 1


if __name__ == "__main__":
    sys.exit(main())
