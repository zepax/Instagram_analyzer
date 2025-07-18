#!/usr/bin/env python3
"""
Prueba completa del exportador HTML de Instagram
Crea datos simulados y genera un reporte HTML completo.
"""

import json
import sys
from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


# Mock simple classes para simular datos de Instagram
class MockMedia:
    def __init__(self, uri, media_type="image", title=""):
        self.uri = uri
        self.media_type = namedtuple("MediaType", ["value"])(media_type)
        self.title = title


class MockPost:
    def __init__(self, post_id, timestamp, caption="", likes=0, comments=0):
        self.post_id = post_id
        self.timestamp = timestamp
        self.caption = caption
        self.likes_count = likes
        self.comments_count = comments
        self.hashtags = []
        self.mentions = []
        self.media = [MockMedia(f"posts/post_{post_id}.jpg")]


class MockAnalyzer:
    """Simulador del InstagramAnalyzer para testing"""

    def __init__(self):
        self.data_path = Path("/tmp/mock_data")

        # Crear posts de prueba
        base_date = datetime(2024, 1, 1)
        self.posts = [
            MockPost(1, base_date, "Mi primer post del año! #newyear #2024", 125, 8),
            MockPost(
                2,
                base_date + timedelta(days=15),
                "Disfrutando del verano ☀️ #summer #beach",
                89,
                12,
            ),
            MockPost(
                3,
                base_date + timedelta(days=30),
                "Nueva receta de cocina 👨‍🍳 #cooking #food",
                156,
                23,
            ),
            MockPost(
                4,
                base_date + timedelta(days=45),
                "Viaje increíble! #travel #adventure",
                203,
                31,
            ),
            MockPost(
                5,
                base_date + timedelta(days=60),
                "Momento de reflexión 🧘‍♀️ #mindfulness #peace",
                78,
                15,
            ),
        ]

        # Datos vacíos para otros elementos
        self.stories = []
        self.reels = []
        self.story_interactions = []
        self.profile = None


def crear_datos_simulados():
    """Crear datos simulados para el reporte"""

    return {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": 5,
            "total_stories": 0,
            "total_reels": 0,
            "version": "0.2.1",
        },
        "overview": {
            "total_posts": 5,
            "total_likes": 651,
            "total_comments": 89,
            "avg_likes_per_post": 130.2,
            "avg_comments_per_post": 17.8,
            "most_liked_post": {
                "likes": 203,
                "caption": "Viaje increíble! #travel #adventure",
            },
            "posting_frequency": "Every 15 days",
            "engagement_rate": "18.5%",
        },
        "temporal_analysis": {
            "posts_by_month": {"January": 2, "February": 2, "March": 1},
            "posts_by_weekday": {
                "Monday": 1,
                "Tuesday": 0,
                "Wednesday": 2,
                "Thursday": 1,
                "Friday": 1,
                "Saturday": 0,
                "Sunday": 0,
            },
            "posts_by_hour": {"9": 1, "12": 2, "15": 1, "18": 1},
        },
        "engagement_analysis": {
            "likes_distribution": [125, 89, 156, 203, 78],
            "comments_distribution": [8, 12, 23, 31, 15],
            "engagement_by_post_type": {
                "photo": {"likes": 651, "comments": 89},
                "carousel": {"likes": 0, "comments": 0},
                "video": {"likes": 0, "comments": 0},
            },
            "peak_engagement_times": ["12:00", "15:00", "18:00"],
        },
        "content_analysis": {
            "hashtags_frequency": {
                "#newyear": 1,
                "#2024": 1,
                "#summer": 1,
                "#beach": 1,
                "#cooking": 1,
                "#food": 1,
                "#travel": 1,
                "#adventure": 1,
                "#mindfulness": 1,
                "#peace": 1,
            },
            "mentions_frequency": {},
            "caption_lengths": [35, 42, 38, 28, 45],
            "avg_caption_length": 37.6,
        },
        "posts": [
            {
                "id": "1",
                "timestamp": "2024-01-01 12:00:00",
                "caption": "Mi primer post del año! #newyear #2024",
                "full_caption": "Mi primer post del año! #newyear #2024",
                "likes": 125,
                "comments": 8,
                "media_count": 1,
                "hashtags": ["#newyear", "#2024"],
                "mentions": [],
                "media": [
                    {"uri": "posts/post_1.jpg", "type": "image", "title": "Post 1"}
                ],
            },
            {
                "id": "2",
                "timestamp": "2024-01-16 15:30:00",
                "caption": "Disfrutando del verano ☀️ #summer #beach",
                "full_caption": "Disfrutando del verano ☀️ #summer #beach",
                "likes": 89,
                "comments": 12,
                "media_count": 1,
                "hashtags": ["#summer", "#beach"],
                "mentions": [],
                "media": [
                    {"uri": "posts/post_2.jpg", "type": "image", "title": "Post 2"}
                ],
            },
            {
                "id": "3",
                "timestamp": "2024-01-31 18:00:00",
                "caption": "Nueva receta de cocina 👨‍🍳 #cooking #food",
                "full_caption": "Nueva receta de cocina 👨‍🍳 #cooking #food",
                "likes": 156,
                "comments": 23,
                "media_count": 1,
                "hashtags": ["#cooking", "#food"],
                "mentions": [],
                "media": [
                    {"uri": "posts/post_3.jpg", "type": "image", "title": "Post 3"}
                ],
            },
            {
                "id": "4",
                "timestamp": "2024-02-15 12:30:00",
                "caption": "Viaje increíble! #travel #adventure",
                "full_caption": "Viaje increíble! #travel #adventure",
                "likes": 203,
                "comments": 31,
                "media_count": 1,
                "hashtags": ["#travel", "#adventure"],
                "mentions": [],
                "media": [
                    {"uri": "posts/post_4.jpg", "type": "image", "title": "Post 4"}
                ],
            },
            {
                "id": "5",
                "timestamp": "2024-03-01 09:15:00",
                "caption": "Momento de reflexión 🧘‍♀️ #mindfulness #peace",
                "full_caption": "Momento de reflexión 🧘‍♀️ #mindfulness #peace",
                "likes": 78,
                "comments": 15,
                "media_count": 1,
                "hashtags": ["#mindfulness", "#peace"],
                "mentions": [],
                "media": [
                    {"uri": "posts/post_5.jpg", "type": "image", "title": "Post 5"}
                ],
            },
        ],
        "stories": [],
        "reels": [],
        "charts_data": {
            "temporal_analysis": {
                "labels": ["Enero", "Febrero", "Marzo"],
                "data": [2, 2, 1],
                "posts_by_weekday": {
                    "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                    "data": [1, 0, 2, 1, 1, 0, 0],
                },
            },
            "engagement_analysis": {
                "labels": ["Post 1", "Post 2", "Post 3", "Post 4", "Post 5"],
                "likes_data": [125, 89, 156, 203, 78],
                "comments_data": [8, 12, 23, 31, 15],
            },
            "hashtags_analysis": {
                "labels": [
                    "#newyear",
                    "#summer",
                    "#cooking",
                    "#travel",
                    "#mindfulness",
                ],
                "data": [1, 1, 1, 1, 1],
            },
        },
        "network_graph": {"nodes": [], "edges": []},
        "additional_content": [],
        "story_interactions": [],
    }


def test_exportador_completo():
    """Test completo del exportador HTML"""

    print("🧪 Iniciando prueba completa del Exportador HTML")
    print("=" * 55)

    try:
        # Crear exportador
        print("📊 Creando exportador HTML...")
        exporter = HTMLExporter()
        print("✅ Exportador creado correctamente")

        # Generar datos simulados
        print("\n🎭 Generando datos simulados...")
        datos_reporte = crear_datos_simulados()
        print(f"✅ Datos generados: {len(datos_reporte)} secciones")
        print(f"  • Posts: {len(datos_reporte['posts'])}")
        print(f"  • Total likes: {datos_reporte['overview']['total_likes']}")
        print(f"  • Total comments: {datos_reporte['overview']['total_comments']}")

        # Renderizar template
        print("\n🌐 Renderizando template HTML...")
        html_content = exporter._render_template(datos_reporte)
        print(f"✅ HTML generado: {len(html_content):,} caracteres")

        # Crear directorio de salida
        output_dir = project_root / "prueba_exportador_output"
        output_dir.mkdir(exist_ok=True)

        # Guardar archivo HTML
        output_file = output_dir / "reporte_instagram_completo.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_size_kb = output_file.stat().st_size / 1024
        print(f"✅ Archivo guardado: {output_file}")
        print(f"📄 Tamaño: {file_size_kb:.1f} KB")

        # Verificaciones del contenido
        print("\n🔍 Verificando contenido del HTML:")
        verificaciones = [
            ("<!DOCTYPE html>", "Declaración DOCTYPE"),
            ("Instagram Analysis Report", "Título del reporte"),
            ("chart.js", "Librería Chart.js"),
            ("d3js.org", "Librería D3.js"),
            ("Mi primer post del año", "Contenido de posts"),
            ("total_posts", "Datos de overview"),
            ("temporal_analysis", "Análisis temporal"),
            ("engagement_analysis", "Análisis de engagement"),
            ("new Chart(", "Creación de gráficos"),
            ("temporalChart", "Gráfico temporal"),
            ("engagementChart", "Gráfico de engagement"),
        ]

        checks_passed = 0
        for check, description in verificaciones:
            if check in html_content:
                print(f"  ✅ {description}")
                checks_passed += 1
            else:
                print(f"  ❌ {description}")

        # Verificar estructura JSON
        print("\n📊 Verificando datos JSON embebidos:")
        try:
            # Extraer JSON del HTML
            json_start = html_content.find("JSON.parse('") + 12
            json_end = html_content.find("');", json_start)
            json_str = html_content[json_start:json_end]

            # Parsear JSON
            parsed_data = json.loads(json_str)
            print(f"✅ JSON válido con {len(parsed_data)} secciones")
            print(f"  • Posts en JSON: {len(parsed_data.get('posts', []))}")
            print(f"  • Charts data: {'✅' if 'charts_data' in parsed_data else '❌'}")

        except (ValueError, json.JSONDecodeError) as e:
            print(f"❌ Error en JSON embebido: {e}")

        # Estadísticas finales
        success_rate = (checks_passed / len(verificaciones)) * 100
        print(f"\n📈 Estadísticas de la prueba:")
        print(
            f"  • Verificaciones pasadas: {checks_passed}/{len(verificaciones)} ({success_rate:.1f}%)"
        )
        print(f"  • Tamaño del reporte: {file_size_kb:.1f} KB")
        print(f"  • Posts procesados: {len(datos_reporte['posts'])}")
        print(f"  • Engagement rate: {datos_reporte['overview']['engagement_rate']}")

        return success_rate >= 90

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Función principal"""
    start_time = datetime.now()

    success = test_exportador_completo()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n⏱️  Tiempo total: {duration:.2f} segundos")

    if success:
        print("\n🎉 ¡Prueba del exportador completada exitosamente!")
        print("\n💡 Para visualizar el reporte:")
        print("  1. Abrir VS Code Explorer")
        print("  2. Navegar a prueba_exportador_output/reporte_instagram_completo.html")
        print("  3. Click derecho → 'Open with Live Server'")
        print("  4. ¡Disfrutar del reporte interactivo!")
        return 0
    else:
        print("\n💥 La prueba del exportador falló!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
