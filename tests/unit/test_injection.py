#!/usr/bin/env python3
"""
Test rápido del exportador con inyección de datos corregida
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def test_data_injection():
    """Test rápido de inyección de datos"""

    print("🧪 Test de inyección de datos en HTML")
    print("=" * 40)

    # Crear datos de prueba simple
    test_data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": 3,
            "total_stories": 2,
            "data_source": "test data",
        },
        "overview": {"total_posts": 3, "total_likes": 150, "total_comments": 25},
        "posts": [
            {
                "id": "test1",
                "timestamp": "2024-01-01 12:00:00",
                "caption": "Test post 1",
                "likes": 50,
                "comments": 10,
                "media": [],
            },
            {
                "id": "test2",
                "timestamp": "2024-01-02 15:00:00",
                "caption": "Test post 2",
                "likes": 100,
                "comments": 15,
                "media": [],
            },
        ],
        "charts_data": {"temporal_analysis": {"labels": ["Jan", "Feb"], "data": [1, 2]}},
        "network_graph": {"nodes": [], "edges": []},
    }

    try:
        # Crear exportador y renderizar
        exporter = HTMLExporter()
        html_content = exporter._render_template(test_data)

        # Verificar que los datos se inyectaron
        checks = [
            ("const metadata = {", "Metadata inyectado"),
            ("const overview = {", "Overview inyectado"),
            ("const posts = [", "Posts inyectados"),
            ("Test post 1", "Contenido de posts presente"),
            ("total_posts", "Datos específicos presentes"),
        ]

        print("🔍 Verificando inyección de datos:")
        success_count = 0
        for check, description in checks:
            if check in html_content:
                print(f"  ✅ {description}")
                success_count += 1
            else:
                print(f"  ❌ {description}")

        # Guardar para inspección
        output_file = project_root / "test_injection.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\n📄 HTML guardado en: {output_file}")
        print(f"📊 Verificaciones exitosas: {success_count}/{len(checks)}")

        return success_count == len(checks)

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_data_injection()
    if success:
        print("\n🎉 ¡Test exitoso! Los datos se están inyectando correctamente.")
    else:
        print("\n💥 Test falló. Revisar la inyección de datos.")

    sys.exit(0 if success else 1)
