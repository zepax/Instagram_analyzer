#!/usr/bin/env python3
"""
Script para generar análisis completo de Instagram con configuraciones optimizadas.
"""

from pathlib import Path

from instagram_analyzer.core.analyzer import InstagramAnalyzer
from instagram_analyzer.exporters import HTMLExporter


def generate_full_analysis(
    data_path: str = "data/sample_exports",
    output_path: str = "output",
    anonymize: bool = False,
    embed_images: bool = True,
    open_result: bool = True,
):
    """
    Generar análisis completo de Instagram con configuraciones optimizadas.

    Args:
        data_path: Ruta a los datos de Instagram
        output_path: Ruta donde guardar el reporte
        anonymize: Si anonimizar datos personales
        embed_images: Si embeber imágenes en el HTML (recomendado: True)
        open_result: Si abrir el resultado automáticamente
    """
    print("🚀 Iniciando análisis completo de Instagram...")

    # Configurar rutas
    data_path = Path(data_path)
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True)

    # Inicializar analyzer
    print("📊 Cargando datos...")
    analyzer = InstagramAnalyzer(data_path)
    analyzer.load_data()

    # Mostrar estadísticas de carga
    print(f"✅ Datos cargados:")
    print(f"   📱 Posts: {len(analyzer.posts)}")
    print(f"   📖 Stories: {len(analyzer.stories)}")
    print(f"   🎬 Reels: {len(analyzer.reels)}")
    print(f"   📁 Archived: {len(analyzer.archived_posts)}")
    print(f"   🗑️ Recently deleted: {len(analyzer.recently_deleted)}")

    # Generar reporte HTML
    print("🎨 Generando reporte HTML...")
    html_exporter = HTMLExporter()
    html_path = html_exporter.export(
        analyzer=analyzer,
        output_path=output_path,
        anonymize=anonymize,
        # embed_images parameter removed - no longer supported
    )

    print(f"✨ Reporte generado exitosamente:")
    print(f"   📄 Archivo: {html_path}")
    print(f"   🔗 URL: file://{html_path.absolute()}")

    if open_result:
        # Abrir el resultado en el navegador
        import os
        import subprocess

        try:
            if os.environ.get("BROWSER"):
                subprocess.run([os.environ["BROWSER"], str(html_path)], check=False)
            else:
                print("💡 Tip: Abre el archivo HTML en tu navegador para ver el reporte")
        except Exception:
            print("💡 Tip: Abre el archivo HTML en tu navegador para ver el reporte")

    return html_path


if __name__ == "__main__":
    import sys

    # Configurar valores por defecto
    data_path = "data/sample_exports"
    output_path = "output"
    anonymize = False
    embed_images = True

    # Procesar argumentos simples
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    if "--anonymize" in sys.argv:
        anonymize = True
    if "--no-images" in sys.argv:
        embed_images = False

    # Generar análisis
    try:
        result_path = generate_full_analysis(
            data_path=data_path,
            output_path=output_path,
            anonymize=anonymize,
            # embed_images parameter removed - no longer supported
            open_result=True,
        )
        print(f"\n🎉 ¡Análisis completado! Archivo disponible en: {result_path}")

    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
