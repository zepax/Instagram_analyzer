#!/usr/bin/env python3
"""
Test funcional del exportador HTML
Crea datos de prueba y genera un reporte HTML completo.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import after path setup
from instagram_analyzer.core.analyzer import InstagramAnalyzer  # noqa: E402
from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def create_test_data():
    """Crear datos de prueba mínimos para el exportador"""

    # Crear directorio de datos de prueba
    test_data_dir = project_root / "test_data_export"
    test_data_dir.mkdir(exist_ok=True)

    # Crear posts de prueba
    posts_dir = test_data_dir / "posts"
    posts_dir.mkdir(exist_ok=True)

    test_posts = {
        "posts": [
            {
                "media": [
                    {
                        "uri": "posts/test_post_1.jpg",
                        "creation_timestamp": 1640995200,  # 2022-01-01
                        "title": "Test post 1",
                    }
                ],
                "caption": "Este es un post de prueba #test #exportador",
                "timestamp": 1640995200,
            },
            {
                "media": [
                    {
                        "uri": "posts/test_post_2.jpg",
                        "creation_timestamp": 1641081600,  # 2022-01-02
                        "title": "Test post 2",
                    },
                    {
                        "uri": "posts/test_post_2_2.jpg",
                        "creation_timestamp": 1641081600,
                        "title": "Test post 2 - image 2",
                    },
                ],
                "caption": "Segundo post de prueba #carousel #multiple",
                "timestamp": 1641081600,
            },
            {
                "media": [
                    {
                        "uri": "posts/test_post_3.mp4",
                        "creation_timestamp": 1641168000,  # 2022-01-03
                        "title": "Test video post",
                    }
                ],
                "caption": "Video de prueba #video #content",
                "timestamp": 1641168000,
            },
        ]
    }

    # Crear archivo posts.json
    posts_file = posts_dir / "posts_1.json"
    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(test_posts, f, indent=2, ensure_ascii=False)

    print(f"✅ Datos de prueba creados en: {test_data_dir}")
    return test_data_dir


def test_html_exporter():
    """Test funcional completo del exportador HTML"""

    print("🧪 Iniciando test funcional del exportador HTML...")

    # Crear datos de prueba
    test_data_dir = create_test_data()

    try:
        # Inicializar analizador con datos de prueba
        print("📊 Inicializando analizador...")
        analyzer = InstagramAnalyzer(str(test_data_dir))

        # Crear directorio de salida
        output_dir = project_root / "test_export_output"
        output_dir.mkdir(exist_ok=True)

        # Inicializar exportador HTML
        print("🌐 Inicializando exportador HTML...")
        html_exporter = HTMLExporter()

        # Generar reporte HTML
        print("📝 Generando reporte HTML...")
        output_file = output_dir / "test_instagram_analysis.html"

        # Exportar con el analizador
        success = html_exporter.export(analyzer, str(output_file))

        if success:
            print(f"✅ Reporte HTML generado exitosamente: {output_file}")
            print(f"📄 Tamaño del archivo: {output_file.stat().st_size / 1024:.1f} KB")

            # Verificar contenido del HTML
            with open(output_file, encoding="utf-8") as f:
                html_content = f.read()

            # Verificaciones básicas
            checks = [
                ("DOCTYPE html", "DOCTYPE declaration"),
                ("Instagram Analysis Report", "Report title"),
                ("Chart.js", "Chart.js library"),
                ("d3.js", "D3.js library"),
                ("overview", "Overview section"),
                ("temporal", "Temporal section"),
                ("engagement", "Engagement section"),
                ("posts", "Posts section"),
                ("test_post", "Test data"),
            ]

            print("\n🔍 Verificando contenido del HTML:")
            for check, description in checks:
                if check in html_content:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description}")

            # Mostrar estadísticas
            print("\n📊 Estadísticas del reporte:")
            print(f"  • Tamaño total: {len(html_content):,} caracteres")
            print(f"  • Líneas: {html_content.count(chr(10)):,}")
            print("  • Posts procesados: 3")

            return True

        else:
            print("❌ Error al generar el reporte HTML")
            return False

    except (FileNotFoundError, ImportError, ValueError) as e:
        print(f"❌ Error durante el test: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Limpiar datos de prueba
        import shutil

        if test_data_dir.exists():
            shutil.rmtree(test_data_dir)
            print(f"🧹 Datos de prueba limpiados: {test_data_dir}")


def main():
    """Función principal"""
    print("🎯 Test Funcional del Exportador HTML")
    print("=" * 50)

    start_time = datetime.now()

    success = test_html_exporter()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n⏱️  Tiempo de ejecución: {duration:.2f} segundos")

    if success:
        print("🎉 Test completado exitosamente!")
        print("\n💡 Para visualizar el reporte:")
        print("  1. Abrir VS Code Explorer")
        print("  2. Navegar a test_export_output/test_instagram_analysis.html")
        print("  3. Click derecho → 'Open with Live Server'")
        return 0
    else:
        print("💥 Test falló!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
