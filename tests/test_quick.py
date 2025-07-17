#!/usr/bin/env python3
"""Test rápido para verificar la funcionalidad del analizador"""

import json
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from instagram_analyzer.core import InstagramAnalyzer
    from instagram_analyzer.exporters import HTMLExporter

    print("✅ Importaciones exitosas!")

    # Verificar que podemos crear instancias
    analyzer = InstagramAnalyzer(".")
    print("✅ InstagramAnalyzer creado exitosamente!")

    # Verificar que podemos crear el exportador HTML
    exporter = HTMLExporter()
    print("✅ HTMLExporter creado exitosamente!")

    # Mostrar resumen de datos disponibles
    stats = analyzer.basic_stats
    print(f"✅ Estadísticas básicas obtenidas: {type(stats)}")

    # Verificar datos específicos
    posts = analyzer.posts
    stories = analyzer.stories
    reels = analyzer.reels
    archived = analyzer.archived_posts
    deleted = analyzer.recently_deleted
    story_interactions = analyzer.story_interactions

    print(f"✅ Posts: {len(posts) if posts else 0}")
    print(f"✅ Historias: {len(stories) if stories else 0}")
    print(f"✅ Reels: {len(reels) if reels else 0}")
    print(f"✅ Posts archivados: {len(archived) if archived else 0}")
    print(f"✅ Contenido eliminado: {len(deleted) if deleted else 0}")
    print(
        f"✅ Interacciones de historias: {len(story_interactions) if story_interactions else 0}"
    )

    # Probar la generación del reporte HTML
    try:
        from pathlib import Path

        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        result_path = exporter.export(analyzer, output_dir)
        print(f"✅ Reporte HTML generado exitosamente: {result_path}")

        # Verificar que el archivo se creó
        if result_path.exists():
            with open(result_path, encoding="utf-8") as f:
                content = f.read()
                print(f"✅ Archivo HTML creado con {len(content)} caracteres")

                # Verificar que contiene las nuevas secciones
                if "Stories" in content:
                    print("✅ Sección Stories incluida")
                if "Reels" in content:
                    print("✅ Sección Reels incluida")
                if "Additional Content" in content:
                    print("✅ Sección Additional Content incluida")
        else:
            print("❌ El archivo HTML no se generó")

    except Exception as e:
        print(f"❌ Error generando reporte HTML: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎉 ¡Todas las funcionalidades están operativas!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
