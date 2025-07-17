#!/usr/bin/env python3
"""Script para probar las nuevas funcionalidades de análisis de conversaciones."""

from pathlib import Path

from instagram_analyzer.analyzers.conversation_analyzer import ConversationAnalyzer
from instagram_analyzer.parsers.conversation_parser import ConversationParser


def test_conversation_analysis():
    """Prueba el análisis completo de conversaciones."""

    # Configurar rutas
    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")

    print("🔍 Iniciando análisis de conversaciones de Instagram...")
    print(f"📁 Ruta de datos: {data_root}")

    # Inicializar analizador
    analyzer = ConversationAnalyzer(data_root)

    # Cargar conversaciones
    print("\n📥 Cargando conversaciones...")
    conversations = analyzer.load_conversations()
    print(f"✅ Conversaciones cargadas: {len(conversations)}")

    if not conversations:
        print("❌ No se encontraron conversaciones para analizar")
        return

    # Mostrar algunas estadísticas básicas
    print("\n📊 Estadísticas básicas:")
    total_messages = sum(len(conv.messages) for conv in conversations)
    print(f"   • Total de mensajes: {total_messages:,}")
    print(f"   • Promedio mensajes/conversación: {total_messages/len(conversations):.1f}")

    # Conversaciones más activas
    active_convs = sorted(conversations, key=lambda c: len(c.messages), reverse=True)[:5]
    print(f"\n🔥 Top 5 conversaciones más activas:")
    for i, conv in enumerate(active_convs, 1):
        print(f"   {i}. {conv.title[:50]}... - {len(conv.messages)} mensajes")

    # Análisis por tipo de conversación
    direct_convs = [c for c in conversations if c.conversation_type.value == "direct"]
    group_convs = [c for c in conversations if c.conversation_type.value == "group"]
    print(f"\n👥 Tipos de conversación:")
    print(f"   • Conversaciones directas: {len(direct_convs)}")
    print(f"   • Conversaciones grupales: {len(group_convs)}")

    # Realizar análisis completo
    print("\n🧠 Realizando análisis avanzado...")
    analysis = analyzer.analyze_conversation_patterns()

    print(f"\n📈 Resultados del análisis:")
    print(f"   • Contactos únicos: {analysis.unique_contacts}")
    if analysis.date_range:
        start_date = analysis.date_range.get("start", "N/A")
        end_date = analysis.date_range.get("end", "N/A")
        print(f"   • Período de actividad: {start_date} - {end_date}")
    else:
        print("   • Período de actividad: N/A")

    # Patrones temporales
    if analysis.messaging_by_hour:
        peak_hour = max(analysis.messaging_by_hour.items(), key=lambda x: x[1])
        print(f"   • Hora más activa: {peak_hour[0]}:00 ({peak_hour[1]} mensajes)")

    if analysis.messaging_by_day:
        peak_day = max(analysis.messaging_by_day.items(), key=lambda x: x[1])
        print(f"   • Día más activo: {peak_day[0]} ({peak_day[1]} mensajes)")

    # Contactos más frecuentes
    if analysis.most_frequent_contacts:
        print(f"\n💬 Contactos más frecuentes:")
        for i, contact in enumerate(analysis.most_frequent_contacts[:5], 1):
            print(
                f"   {i}. {contact['name'][:30]} - {contact['total_messages']} mensajes"
            )

    # Tipos de mensaje
    if analysis.message_type_distribution:
        print(f"\n📱 Distribución de tipos de mensaje:")
        for msg_type, count in list(analysis.message_type_distribution.items())[:5]:
            print(f"   • {msg_type}: {count}")

    # Análisis de hilos
    if analysis.thread_analysis:
        thread_info = analysis.thread_analysis
        print(f"\n🧵 Análisis de hilos:")
        print(f"   • Total de hilos: {thread_info.get('total_threads', 0)}")
        print(
            f"   • Promedio mensajes/hilo: {thread_info.get('avg_thread_length', 0):.1f}"
        )
        print(
            f"   • Duración promedio: {thread_info.get('avg_thread_duration_minutes', 0):.1f} minutos"
        )

    # Tópicos populares
    if analysis.popular_topics:
        print(f"\n🏷️ Tópicos más populares:")
        for i, topic in enumerate(analysis.popular_topics[:5], 1):
            print(
                f"   {i}. {topic['topic']} (en {topic['conversations']} conversaciones)"
            )

    # Tiempos de respuesta
    if analysis.response_time_analysis:
        resp_analysis = analysis.response_time_analysis
        print(f"\n⏱️ Análisis de tiempos de respuesta:")
        print(
            f"   • Tiempo promedio: {resp_analysis.get('avg_response_time_minutes', 0):.1f} minutos"
        )
        print(
            f"   • Respuestas rápidas (<5min): {resp_analysis.get('fast_response_percentage', 0):.1f}%"
        )
        print(
            f"   • Respuestas lentas (>1h): {resp_analysis.get('slow_response_percentage', 0):.1f}%"
        )

    # Exportar resumen
    output_dir = Path("conversation_analysis")
    output_dir.mkdir(exist_ok=True)

    print(f"\n💾 Exportando análisis...")
    summary_file = analyzer.export_conversation_summary(output_dir)
    print(f"✅ Resumen exportado: {summary_file}")

    return analyzer, analysis


def test_single_conversation():
    """Prueba el análisis de una conversación específica."""

    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS DE CONVERSACIÓN INDIVIDUAL")
    print("=" * 60)

    # Ruta a un archivo de conversación específico
    conv_file = Path(
        "examples/instagram-florenescobar-2025-07-13-pcFuHXmB/your_instagram_activity/messages/inbox/paolacastillo_513456650044931/message_1.json"
    )

    if not conv_file.exists():
        print(f"❌ Archivo no encontrado: {conv_file}")
        # Intentar encontrar cualquier archivo de conversación
        inbox_dir = Path(
            "examples/instagram-florenescobar-2025-07-13-pcFuHXmB/your_instagram_activity/messages/inbox"
        )
        if inbox_dir.exists():
            for conv_dir in inbox_dir.iterdir():
                if conv_dir.is_dir():
                    message_files = list(conv_dir.glob("message_*.json"))
                    if message_files:
                        conv_file = message_files[0]
                        print(f"📁 Usando en su lugar: {conv_file}")
                        break
            else:
                print(f"❌ No se encontraron archivos de conversación en {inbox_dir}")
                return
        else:
            print(f"❌ Directorio inbox no encontrado: {inbox_dir}")
            return

    # Parsear conversación individual
    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    parser = ConversationParser(data_root)

    print(f"📁 Analizando: {conv_file.name}")
    conversation = parser.parse_conversation_file(conv_file)

    if not conversation:
        print("❌ Error al parsear la conversación")
        return

    print(f"\n📊 Información de la conversación:")
    print(f"   • ID: {conversation.conversation_id}")
    print(f"   • Título: {conversation.title}")
    print(f"   • Tipo: {conversation.conversation_type.value}")
    print(f"   • Participantes: {len(conversation.participants)}")
    print(f"   • Mensajes: {len(conversation.messages)}")
    print(f"   • Hilos: {len(conversation.threads)}")

    # Mostrar participantes
    print(f"\n👥 Participantes:")
    for p in conversation.participants:
        status = " (yo)" if p.is_self else ""
        print(f"   • {p.name}{status}")

    # Mostrar métricas
    if conversation.metrics:
        metrics = conversation.metrics
        print(f"\n📈 Métricas:")
        print(f"   • Duración: {metrics.conversation_duration_days} días")
        print(f"   • Mensajes/día: {metrics.avg_messages_per_day:.1f}")
        print(f"   • Participante más activo: {metrics.most_active_participant}")
        print(
            f"   • Hora más activa: {metrics.most_active_hour}:00"
            if metrics.most_active_hour
            else ""
        )

        if metrics.media_counts:
            print(f"   • Medios compartidos: {sum(metrics.media_counts.values())}")

    # Mostrar algunos mensajes recientes
    print(f"\n💬 Últimos 5 mensajes:")
    recent_messages = (
        conversation.messages[-5:]
        if len(conversation.messages) >= 5
        else conversation.messages
    )
    for msg in recent_messages:
        timestamp = (
            msg.timestamp.strftime("%Y-%m-%d %H:%M") if msg.timestamp else "Sin fecha"
        )
        content = (
            msg.content[:50] + "..."
            if msg.content and len(msg.content) > 50
            else msg.content or "[Sin contenido]"
        )
        print(f"   • {timestamp} - {msg.sender_name}: {content}")

    # Mostrar hilos
    if conversation.threads:
        print(f"\n🧵 Hilos de conversación:")
        for i, thread in enumerate(conversation.threads[:3], 1):
            duration = (
                f" ({thread.duration_minutes:.0f}min)" if thread.duration_minutes else ""
            )
            topic = f" - {thread.topic}" if thread.topic else ""
            print(f"   {i}. {len(thread.messages)} mensajes{duration}{topic}")

    return conversation


def test_search_functionality():
    """Prueba la funcionalidad de búsqueda."""

    print("\n" + "=" * 60)
    print("🔍 PRUEBA DE FUNCIONALIDADES DE BÚSQUEDA")
    print("=" * 60)

    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    analyzer = ConversationAnalyzer(data_root)

    # Cargar conversaciones
    conversations = analyzer.load_conversations()

    if not conversations:
        print("❌ No hay conversaciones para buscar")
        return

    # Ejemplos de búsqueda
    search_terms = ["gracias", "hola", "jaja", "foto"]

    print(f"📊 Total de conversaciones: {len(conversations)}")

    for term in search_terms:
        matches = analyzer.search_conversations(term)
        print(f"\n🔍 Búsqueda: '{term}' - {len(matches)} coincidencias")

        for match in matches[:3]:  # Mostrar primeras 3
            total_msgs = len(match.messages)
            print(f"   • {match.title[:40]}... ({total_msgs} mensajes)")


if __name__ == "__main__":
    try:
        # Prueba análisis completo
        analyzer, analysis = test_conversation_analysis()

        # Prueba conversación individual
        conversation = test_single_conversation()

        # Prueba búsqueda
        test_search_functionality()

        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print("\n📁 Archivos generados:")
        print("   • conversation_analysis/conversation_analysis_summary.json")
        print("\n💡 Comandos útiles para continuar:")
        print("   • Revisar el archivo JSON generado")
        print("   • Explorar conversaciones individuales")
        print("   • Realizar búsquedas personalizadas")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback

        traceback.print_exc()
