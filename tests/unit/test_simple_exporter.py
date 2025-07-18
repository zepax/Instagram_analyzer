#!/usr/bin/env python3
"""
Test simple del exportador HTML
Test directo de la funcionalidad de exportación.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import after path setup
from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def test_html_template():
    """Test básico del template HTML"""

    print("🧪 Test simple del exportador HTML...")

    try:
        # Crear exportador
        exporter = HTMLExporter()

        # Verificar que se puede instanciar
        print("✅ HTMLExporter instanciado correctamente")

        # Crear directorio de salida
        output_dir = project_root / "test_simple_output"
        output_dir.mkdir(exist_ok=True)

        # Test básico de template
        template_content = exporter.template

        if template_content:
            print("✅ Template cargado correctamente")
            print(f"📄 Tamaño del template: {len(template_content)} caracteres")

            # Verificar elementos básicos del template
            checks = [
                ("<!DOCTYPE html>", "DOCTYPE declaration"),
                ("<html", "HTML tag"),
                ("Chart.js", "Chart.js library"),
                ("overview", "Overview section"),
                ("temporal", "Temporal section"),
                ("engagement", "Engagement section"),
            ]

            print("\n🔍 Verificando elementos del template:")
            for check, description in checks:
                if check in template_content:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description}")

            # Crear HTML de prueba básico
            test_html = template_content.replace(
                "{{DATA_JSON}}",
                '{"test": "success", "timestamp": "' + str(datetime.now()) + '"}',
            )

            output_file = output_dir / "test_simple.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(test_html)

            print(f"\n✅ HTML de prueba generado: {output_file}")
            print(f"📄 Tamaño: {output_file.stat().st_size / 1024:.1f} KB")

            return True
        else:
            print("❌ Error: Template no encontrado")
            return False

    except (ImportError, FileNotFoundError, AttributeError) as e:
        print(f"❌ Error durante el test: {e}")
        return False


def main():
    """Función principal"""
    print("🎯 Test Simple del Exportador HTML")
    print("=" * 40)

    start_time = datetime.now()

    success = test_html_template()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n⏱️  Tiempo de ejecución: {duration:.2f} segundos")

    if success:
        print("🎉 Test completado exitosamente!")
        print("\n💡 Para visualizar el HTML:")
        print("  1. Abrir VS Code Explorer")
        print("  2. Navegar a test_simple_output/test_simple.html")
        print("  3. Click derecho → 'Open with Live Server'")
        return 0
    else:
        print("💥 Test falló!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
