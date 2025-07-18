#!/usr/bin/env python3
"""
Prueba completa del exportador HTML con datos REALES de Instagram
Usa datos reales del directorio data/sample_exports.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from instagram_analyzer.core.analyzer import InstagramAnalyzer  # noqa: E402
from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def test_exportador_datos_reales():
    """Test del exportador HTML con datos reales de Instagram"""

    print("🧪 Iniciando prueba del Exportador HTML con DATOS REALES")
    print("=" * 60)

    try:
        # Ruta a los datos reales - usando la carpeta instagram-pcFuHXmB
        data_path = project_root / "data" / "sample_exports" / "instagram-pcFuHXmB"

        if not data_path.exists():
            print(f"❌ No se encontraron datos en: {data_path}")
            return False

        print(f"📂 Usando datos reales de: {data_path}")

        # Verificar que existen archivos de datos
        posts_file = data_path / "your_instagram_activity" / "media" / "posts_1.json"
        stories_file = data_path / "your_instagram_activity" / "media" / "stories.json"

        print(f"  • Posts file: {'✅' if posts_file.exists() else '❌'}")
        print(f"  • Stories file: {'✅' if stories_file.exists() else '❌'}")

        # Crear analizador con datos reales
        print("\n📊 Inicializando analizador con datos reales...")
        analyzer = InstagramAnalyzer(str(data_path))
        print("✅ Analizador creado correctamente")

        # Forzar la carga de datos
        print("\n🔄 Forzando carga de datos...")
        try:
            # Acceder a las propiedades para forzar la carga
            posts_count = len(analyzer.posts)
            stories_count = len(analyzer.stories)
            reels_count = len(analyzer.reels)

            # Intentar cargar explícitamente si están vacíos
            if posts_count == 0:
                print("  • Intentando carga manual de posts...")
                analyzer._load_posts()
                posts_count = len(analyzer.posts)

        except Exception as load_error:
            print(f"⚠️  Error al cargar datos: {load_error}")
            # Continuar de cualquier manera

        # Verificar que hay datos
        print("\n📈 Datos cargados:")
        print(f"  • Posts: {posts_count}")
        print(f"  • Stories: {stories_count}")
        print(f"  • Reels: {reels_count}")

        if posts_count == 0:
            print("⚠️  No hay posts para analizar")
            return False

        # Crear exportador
        print("\n🌐 Creando exportador HTML...")
        exporter = HTMLExporter()
        print("✅ Exportador creado correctamente")

        # Crear directorio de salida
        output_dir = project_root / "prueba_exportador_output"
        output_dir.mkdir(exist_ok=True)

        # Exportar con datos reales
        print("\n📝 Generando reporte HTML con datos reales...")
        output_file = output_dir / "reporte_instagram_datos_reales.html"

        # Generar datos del reporte
        print("  • Generando datos de análisis...")
        report_data = exporter._generate_report_data(
            analyzer, anonymize=False, embed_images=False
        )

        # Renderizar template
        print("  • Renderizando template HTML...")
        html_content = exporter._render_template(report_data)

        # Guardar archivo
        print("  • Guardando archivo HTML...")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_size_kb = output_file.stat().st_size / 1024
        print(f"✅ Reporte generado: {output_file}")
        print(f"📄 Tamaño: {file_size_kb:.1f} KB")

        # Verificaciones del contenido
        print("\n🔍 Verificando contenido del HTML:")
        verificaciones = [
            ("<!DOCTYPE html>", "Declaración DOCTYPE"),
            ("Instagram Analysis Report", "Título del reporte"),
            ("chart.js", "Librería Chart.js"),
            ("d3js.org", "Librería D3.js"),
            ("overview", "Sección overview"),
            ("temporal_analysis", "Análisis temporal"),
            ("engagement_analysis", "Análisis de engagement"),
            ("new Chart(", "Creación de gráficos"),
            ("temporalChart", "Gráfico temporal"),
            ("engagementChart", "Gráfico de engagement"),
            ("posts", "Sección de posts"),
        ]

        checks_passed = 0
        for check, description in verificaciones:
            if check in html_content:
                print(f"  ✅ {description}")
                checks_passed += 1
            else:
                print(f"  ❌ {description}")

        # Estadísticas de los datos reales
        print(f"\n📊 Estadísticas de los datos reales:")
        print(f"  • Posts analizados: {len(analyzer.posts)}")
        if hasattr(report_data, "overview") and report_data["overview"]:
            overview = report_data["overview"]
            print(f"  • Total likes: {overview.get('total_likes', 'N/A')}")
            print(f"  • Total comments: {overview.get('total_comments', 'N/A')}")
            print(f"  • Engagement rate: {overview.get('engagement_rate', 'N/A')}")

        # Resultado final
        success_rate = (checks_passed / len(verificaciones)) * 100
        print(f"\n📈 Resultado de la prueba:")
        print(
            f"  • Verificaciones pasadas: {checks_passed}/{len(verificaciones)} ({success_rate:.1f}%)"
        )
        print(f"  • Tamaño del reporte: {file_size_kb:.1f} KB")

        return success_rate >= 80  # Más flexible para datos reales

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Tip: Asegúrate de que todas las dependencias estén instaladas")
        return False

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
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
        print("\n🎉 ¡Prueba con datos reales completada exitosamente!")
        print("\n💡 Para visualizar el reporte:")
        print("  1. Abrir VS Code Explorer")
        print(
            "  2. Navegar a prueba_exportador_output/reporte_instagram_datos_reales.html"
        )
        print("  3. Click derecho → 'Open with Live Server'")
        print("  4. ¡Ver el análisis de datos reales de Instagram!")
        return 0
    else:
        print("\n💥 La prueba con datos reales falló!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
