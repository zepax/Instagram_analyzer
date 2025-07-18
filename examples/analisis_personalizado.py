#!/usr/bin/env python3
"""Análisis personalizado de Instagram con reporte HTML optimizado."""

from datetime import datetime, timedelta
from pathlib import Path

from instagram_analyzer.core.analyzer import InstagramAnalyzer
from instagram_analyzer.exporters import HTMLExporter
from instagram_analyzer.extractors.conversation_extractor import (
    ConversationExtractor,
    extract_conversations_with_keywords,
)
from instagram_analyzer.models.conversation import Conversation, ConversationAnalysis


def generar_analisis_completo() -> Path:
    """Genera un análisis completo con reporte HTML optimizado."""

    print("🚀 Iniciando análisis completo de Instagram...")

    # ============ CONFIGURACIÓN ============

    # 1. DATASET - Cambiar esta ruta por la tuya
    mi_dataset = Path("data/sample_exports")

    # 2. CONFIGURACIÓN DEL REPORTE
    output_path = Path("mi_analisis_personalizado")
    output_path.mkdir(exist_ok=True)

    anonymize = False  # Cambiar a True si quieres anonimizar datos
    embed_images = True  # True para ver imágenes (recomendado)

    # ============ ANÁLISIS PRINCIPAL ============

    print("📊 Cargando datos de Instagram...")
    analyzer = InstagramAnalyzer(mi_dataset)
    analyzer.load_data()

    # Mostrar estadísticas
    print("✅ Datos cargados:")
    print(f"   📱 Posts: {len(analyzer.posts)}")
    print(f"   📖 Stories: {len(analyzer.stories)}")
    print(f"   🎬 Reels: {len(analyzer.reels)}")

    # Generar reporte HTML
    print("🎨 Generando reporte HTML...")
    html_exporter = HTMLExporter()
    html_path = html_exporter.export(
        analyzer=analyzer,
        output_path=output_path,
        anonymize=anonymize,
        # embed_images parameter removed - no longer supported
    )

    print(f"✨ Reporte HTML generado en: {html_path}")
    return html_path


def analizar_mis_conversaciones() -> tuple[list[Conversation], ConversationAnalysis]:
    """Ejecuta análisis de conversaciones (opcional)."""

    # ============ CONFIGURACIÓN DE CONVERSACIONES ============

    # 1. TU DATASET - Cambiar esta ruta por la tuya
    mi_dataset = Path("data/sample_exports/instagram-pcFuHXmB/")

    # 2. TUS PALABRAS CLAVE - Personaliza según tus intereses
    # Cargar palabras clave desde archivo
    keywords_file = Path("keywords.txt")  # Cambiar por la ruta a tu archivo
    if keywords_file.exists():
        with open(keywords_file, encoding="utf-8") as f:
            mis_palabras_clave = [line.strip() for line in f if line.strip()]
        print(
            f"✅ Cargadas {len(mis_palabras_clave)} palabras clave desde {keywords_file}"
        )
    else:
        print(f"❌ No se encontró el archivo {keywords_file}")
        print("📝 Creando archivo de ejemplo...")
        # Crear archivo de ejemplo con algunas palabras
        with open(keywords_file, "w", encoding="utf-8") as f:
            f.write("amor\ncariño\ngracias\nhola\n")
        mis_palabras_clave = ["amor", "cariño", "gracias", "hola"]
        print(f"✅ Archivo {keywords_file} creado con palabras de ejemplo")

    # 3. TUS FILTROS PERSONALIZADOS
    filtros_personalizados = {
        "min_messages": 5,  # Solo conversaciones activas (reducido)
        "exclude_empty": True,  # Sin conversaciones vacías
        # 'max_messages': 500,     # Opcional: limitar conversaciones largas
    }

    # 4. RANGO DE FECHAS (opcional)
    meses_atras = 140  # Analizar últimos 12 meses
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30 * meses_atras)

    # ============ EJECUCIÓN DEL ANÁLISIS ============

    print("🔍 Iniciando análisis personalizado de conversaciones")
    print(f"📁 Dataset: {mi_dataset}")
    print(f"🔤 Palabras clave: {', '.join(mis_palabras_clave)}")
    print(
        f"📅 Período: {fecha_inicio.strftime('%Y-%m-%d')} a "
        f"{fecha_fin.strftime('%Y-%m-%d')}"
    )

    # Inicializar extractor
    extractor = ConversationExtractor(mi_dataset, max_workers=4)
    extractor.set_filters(**filtros_personalizados)

    # ANÁLISIS 1: Conversaciones con palabras clave
    print("\n🎯 Buscando conversaciones con palabras clave...")
    conversaciones_palabras = extract_conversations_with_keywords(
        mi_dataset, mis_palabras_clave
    )

    print(
        f"✅ Encontradas {len(conversaciones_palabras)} "
        "conversaciones con tus palabras"
    )

    # Mostrar top 10 más activas
    conversaciones_ordenadas = sorted(
        conversaciones_palabras, key=lambda c: len(c.messages), reverse=True
    )

    print("\n🔥 Top 10 conversaciones más activas con tus palabras:")
    for i, conv in enumerate(conversaciones_ordenadas[:10], 1):
        # Buscar cuáles palabras se encontraron
        palabras_encontradas = []
        for palabra in mis_palabras_clave:
            if any(
                msg.content and palabra.lower() in msg.content.lower()
                for msg in conv.messages
                if msg.content
            ):
                palabras_encontradas.append(palabra)

        print(f"   {i}. {conv.title[:35]}... ({len(conv.messages)} msgs)")
        print(f"      Palabras: {', '.join(palabras_encontradas[:5])}")

    # ANÁLISIS 2: Conversaciones por período de tiempo
    print(
        f"\n📅 Analizando conversaciones del período "
        f"{fecha_inicio.strftime('%Y-%m-%d')} al "
        f"{fecha_fin.strftime('%Y-%m-%d')}..."
    )

    conversaciones_periodo = extractor.extract_conversations_by_criteria(
        date_range=(fecha_inicio, fecha_fin),
        min_message_count=filtros_personalizados["min_messages"],
    )

    print(
        f"✅ Encontradas {len(conversaciones_periodo)} conversaciones "
        "activas en el período"
    )

    # ANÁLISIS 3: Análisis completo y exportación
    print("\n🧠 Ejecutando análisis completo...")

    output_dir = Path("mi_analisis_personalizado/analisis_completo")
    conversaciones_completas, analisis_completo = extractor.extract_and_analyze(
        export_path=output_dir,
        include_advanced_analytics=True,
        anonymize=False,  # Cambia a True si quieres anonimizar
    )

    print("✅ Análisis completo terminado:")
    print(f"   • Total conversaciones: {len(conversaciones_completas)}")
    print(f"   • Total mensajes: {analisis_completo.total_messages}")
    print(f"   • Contactos únicos: {analisis_completo.unique_contacts}")

    # ANÁLISIS 4: Estadísticas personalizadas
    print("\n📊 Estadísticas de tu análisis:")
    # Análisis de palabras más frecuentes
    contador_palabras: dict[str, int] = {}
    # Este bucle itera sobre las conversaciones que ya tienen el análisis de frecuencia de palabras clave.
    # El análisis se realiza dentro de `extractor.extract_and_analyze` si `include_advanced_analytics=True`.
    for conv in conversaciones_completas:
        if hasattr(conv, "keyword_frequency") and conv.keyword_frequency:
            for palabra, freq in conv.keyword_frequency.items():
                if palabra.lower() in [p.lower() for p in mis_palabras_clave]:
                    contador_palabras[palabra] = contador_palabras.get(palabra, 0) + freq

    if contador_palabras:
        print("   Frecuencia de tus palabras clave:")
        palabras_ordenadas = sorted(
            contador_palabras.items(), key=lambda x: x[1], reverse=True
        )
        for palabra, freq in palabras_ordenadas[:10]:
            print(f"      • {palabra}: {freq} veces")

    # Conversaciones más largas
    conv_largas = sorted(
        conversaciones_completas, key=lambda c: len(c.messages), reverse=True
    )[:5]
    print("   Top 5 conversaciones más largas:")
    for i, conv in enumerate(conv_largas, 1):
        print(f"      {i}. {conv.title[:30]}... - {len(conv.messages)} " "mensajes")

    print(f"\n💾 Resultados guardados en: {output_dir}")
    print("   • conversation_extraction_results.json - Análisis completo")
    print("   • conversations/ - Detalles de conversaciones individuales")

    return conversaciones_completas, analisis_completo


def ejemplo_busqueda_rapida() -> None:
    """Ejemplo de búsqueda rápida por palabras clave."""

    print("\n" + "=" * 50)
    print("🚀 EJEMPLO DE BÚSQUEDA RÁPIDA")
    print("=" * 50)

    # Configuración rápida
    dataset = Path("data/sample_exports/instagram-pcFuHXmB")
    palabras_buscar = ["gracias", "hola", "jaja"]

    print(f"Buscando: {', '.join(palabras_buscar)}")

    # Búsqueda rápida
    busqueda_rapida_conversaciones = extract_conversations_with_keywords(
        dataset, palabras_buscar
    )

    print(f"✅ Encontradas {len(busqueda_rapida_conversaciones)} conversaciones")

    for i, conv in enumerate(busqueda_rapida_conversaciones[:5], 1):
        print(f"   {i}. {conv.title[:40]}... ({len(conv.messages)} mensajes)")


def ejemplo_filtros_avanzados() -> None:
    """Ejemplo con filtros avanzados."""

    print("\n" + "=" * 50)
    print("🎯 EJEMPLO DE FILTROS AVANZADOS")
    print("=" * 50)

    dataset = Path("data/sample_exports/instagram-pcFuHXmB")
    extractor = ConversationExtractor(dataset)

    # Configurar filtros específicos
    extractor.set_filters(
        min_messages=50,  # Solo conversaciones con 10+ mensajes
    )

    # Extraer con filtros
    conversaciones_filtradas = extractor.extract_all_conversations()
    print(f"✅ Conversaciones filtradas: {len(conversaciones_filtradas)}")

    # Estadísticas
    stats = extractor.get_extraction_statistics()
    print(f"📊 Tasa de éxito: {stats.get('success_rate', 0):.1f}%")
    velocidad = stats.get("processing_rate_conversations_per_second", 0)
    print(f"⚡ Velocidad: {velocidad:.1f} conv/seg")


if __name__ == "__main__":
    try:
        print("🔍 ANÁLISIS PERSONALIZADO DE CONVERSACIONES")
        print("=" * 60)

        # Ejecutar análisis completo
        conversaciones_resultado, analisis_resultado = analizar_mis_conversaciones()

        # Ejecutar ejemplos adicionales
        # ejemplo_busqueda_rapida()
        ejemplo_filtros_avanzados()

        print("\n" + "=" * 60)
        print("✅ TODOS LOS ANÁLISIS COMPLETADOS EXITOSAMENTE")
        print("=" * 60)

        print("\n💡 Para personalizar tu análisis:")
        print("   1. Cambia mi_dataset por la ruta a tu dataset")
        print("   2. Modifica mis_palabras_clave con tus palabras de interés")
        print("   3. Ajusta filtros_personalizados según tus necesidades")
        print("   4. Ejecuta: python examples/analisis_personalizado.py")

    except (FileNotFoundError, ValueError) as e:
        print(f"\n❌ Error de configuración o datos: {e}")
        print("   Asegúrate de que la ruta a 'mi_dataset' es correcta.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado durante el análisis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Genera análisis completo por defecto
    print("🎯 Generando análisis completo de Instagram...")
    try:
        html_path = generar_analisis_completo()
        print(f"\n🎉 ¡Análisis completado!")
        print(f"📄 Abre el archivo: {html_path}")
        print(f"🔗 URL: file://{html_path.absolute()}")

        # Opcional: también ejecutar análisis de conversaciones
        respuesta = input("\n❓ ¿También quieres analizar conversaciones? (y/N): ")
        if respuesta.lower() in ["y", "yes", "sí", "si"]:
            print("\n📱 Ejecutando análisis de conversaciones...")
            analizar_mis_conversaciones()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
