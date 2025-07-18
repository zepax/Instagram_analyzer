#!/usr/bin/env python3
"""
Ejemplo de script para ejecutar un análisis completo de Instagram,
incluyendo posts, historias, reels y conversaciones.
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

# Añadir el directorio src al path para poder importar instagram_analyzer
# Esto es necesario si el paquete no está instalado en modo editable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from instagram_analyzer.core.analyzer import InstagramAnalyzer
    from instagram_analyzer.exceptions import InstagramAnalyzerError
except ImportError as e:
    print("Error: No se pudo importar el módulo 'instagram_analyzer'.")
    print("Asegúrate de que el paquete está instalado (ej. 'pip install -e .')")
    print(f"Detalle del error: {e}")
    sys.exit(1)


def ejecutar_analisis_completo() -> None:
    """
    Ejecuta un análisis completo de un export de datos de Instagram
    y genera un reporte HTML.
    """
    console = Console()
    console.print(
        Panel(
            "[bold cyan]📊 Instagram Analyzer - Análisis Completo 📊[/bold cyan]",
            expand=False,
            border_style="blue",
        )
    )

    # --- CONFIGURACIÓN ---
    # 1. Ruta a tu export de datos de Instagram (la carpeta extraída del ZIP)
    data_path = Path("data/sample_exports/instagram-pcFuHXmB/")

    # 2. Ruta donde se guardará el reporte generado
    output_path = Path("output/analisis_completo/")
    # --- FIN DE LA CONFIGURACIÓN ---

    if not data_path.exists() or not data_path.is_dir():
        console.print(
            f"[bold red]Error:[/bold red] El directorio de datos '{data_path}' no existe."
        )
        console.print(
            "Por favor, descarga tus datos de Instagram y actualiza la ruta en este script."
        )
        return

    console.print(f"▶️  [bold]Directorio de datos:[/bold] {data_path}")
    console.print(f"▶️  [bold]Directorio de salida:[/bold] {output_path}")
    console.print("-" * 50)

    try:
        # 1. Inicializar el analizador
        console.print("⏳ [yellow]Inicializando analizador...[/yellow]")
        analyzer = InstagramAnalyzer(data_path)

        # 2. Cargar y parsear los datos
        console.print(
            "⏳ [yellow]Cargando y parseando datos... (esto puede tardar unos minutos)[/yellow]"
        )
        analyzer.load_data()
        console.print("✅ [green]Datos cargados y parseados.[/green]")

        # 3. Validar los datos cargados
        validation_results = analyzer.validate_data()
        if not validation_results.get("data_loaded", {}).get("valid", False):
            console.print(
                "[bold yellow]Advertencia:[/bold yellow] Algunos archivos de datos no se encontraron o están vacíos."
            )
            console.print(
                "El análisis continuará, pero los resultados pueden ser incompletos."
            )

        # 4. Ejecutar el análisis
        console.print(
            "⏳ [yellow]Ejecutando análisis de engagement, contenido y más...[/yellow]"
        )
        analysis_results = analyzer.analyze(
            include_media=True,  # Analiza metadatos de imágenes/videos
        )
        console.print("✅ [green]Análisis completado.[/green]")

        # 5. Exportar el reporte a HTML
        console.print(f"⏳ [yellow]Generando reporte HTML en '{output_path}'...[/yellow]")
        report_path = analyzer.export_html(
            output_path,
            anonymize=False,  # Cambiar a True para ocultar nombres de usuario
        )
        console.print(f"✅ [bold green]¡Reporte generado exitosamente![/bold green]")
        console.print(
            f"📄 [bold]Puedes ver tu reporte en:[/bold] file://{report_path.resolve()}"
        )

    except InstagramAnalyzerError as e:
        console.print(f"[bold red]Error durante el análisis:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Ocurrió un error inesperado:[/bold red] {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    ejecutar_analisis_completo()
