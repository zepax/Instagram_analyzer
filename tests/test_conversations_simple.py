#!/usr/bin/env python3
"""Script simplificado para probar análisis de conversaciones."""

import json
import sys
from pathlib import Path


def test_conversation_parser_only():
    """Prueba solo el parser de conversaciones sin dependencias del core."""

    print("🔍 Prueba del Parser de Conversaciones")
    print("=" * 50)

    # Importar solo lo necesario
    try:
        from instagram_analyzer.models.conversation import ConversationType
        from instagram_analyzer.parsers.conversation_parser import ConversationParser

        print("✅ Imports exitosos")
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False

    # Configurar rutas
    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"

    print(f"📁 Buscando conversaciones en: {inbox_dir}")

    if not inbox_dir.exists():
        print(f"❌ Directorio no encontrado: {inbox_dir}")
        return False

    # Buscar archivos de conversación
    conversation_files = []
    for conv_dir in inbox_dir.iterdir():
        if conv_dir.is_dir():
            message_files = list(conv_dir.glob("message_*.json"))
            conversation_files.extend(message_files)

    print(f"📊 Archivos de conversación encontrados: {len(conversation_files)}")

    if not conversation_files:
        print("❌ No se encontraron archivos de conversación")
        return False

    # Inicializar parser
    parser = ConversationParser(data_root)

    # Probar parsing de una conversación
    test_file = conversation_files[0]
    print(f"\n🔍 Analizando archivo: {test_file.name}")

    try:
        conversation = parser.parse_conversation_file(test_file)
        if conversation:
            print("✅ Parsing exitoso")
            print(f"   • ID: {conversation.conversation_id}")
            print(f"   • Título: {conversation.title}")
            print(f"   • Tipo: {conversation.conversation_type.value}")
            print(f"   • Participantes: {len(conversation.participants)}")
            print(f"   • Mensajes: {len(conversation.messages)}")
            print(f"   • Hilos: {len(conversation.threads)}")

            # Mostrar algunos mensajes
            if conversation.messages:
                print(f"\n💬 Últimos 3 mensajes:")
                for msg in conversation.messages[-3:]:
                    sender = (
                        msg.sender_name[:20] + "..."
                        if len(msg.sender_name) > 20
                        else msg.sender_name
                    )
                    content = (
                        msg.content[:50] + "..."
                        if msg.content and len(msg.content) > 50
                        else msg.content or "[Sin texto]"
                    )
                    print(f"   • {sender}: {content}")

            # Mostrar métricas si existen
            if conversation.metrics:
                metrics = conversation.metrics
                print(f"\n📈 Métricas:")
                print(f"   • Duración: {metrics.conversation_duration_days} días")
                print(f"   • Participante más activo: {metrics.most_active_participant}")
                if metrics.media_counts:
                    total_media = sum(metrics.media_counts.values())
                    print(f"   • Medios compartidos: {total_media}")

            return True
        else:
            print("❌ Error en parsing - conversation es None")
            return False

    except Exception as e:
        print(f"❌ Error durante parsing: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_multiple_conversations():
    """Prueba parsing de múltiples conversaciones."""

    print("\n" + "=" * 50)
    print("🔍 Prueba de Múltiples Conversaciones")
    print("=" * 50)

    try:
        from instagram_analyzer.models.conversation import ConversationType
        from instagram_analyzer.parsers.conversation_parser import ConversationParser
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False

    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"

    parser = ConversationParser(data_root)

    # Parsear todas las conversaciones
    print("📥 Cargando todas las conversaciones...")
    try:
        conversations = parser.parse_all_conversations(inbox_dir)
        print(f"✅ Conversaciones cargadas: {len(conversations)}")

        if not conversations:
            print("❌ No se cargaron conversaciones")
            return False

        # Estadísticas básicas
        total_messages = sum(len(conv.messages) for conv in conversations)
        direct_convs = len(
            [c for c in conversations if c.conversation_type == ConversationType.DIRECT]
        )
        group_convs = len(
            [c for c in conversations if c.conversation_type == ConversationType.GROUP]
        )

        print(f"\n📊 Estadísticas:")
        print(f"   • Total mensajes: {total_messages:,}")
        print(f"   • Conversaciones directas: {direct_convs}")
        print(f"   • Conversaciones grupales: {group_convs}")
        print(
            f"   • Promedio mensajes/conversación: {total_messages/len(conversations):.1f}"
        )

        # Top 5 conversaciones más activas
        active_convs = sorted(conversations, key=lambda c: len(c.messages), reverse=True)[
            :5
        ]
        print(f"\n🔥 Top 5 conversaciones más activas:")
        for i, conv in enumerate(active_convs, 1):
            title = conv.title[:40] + "..." if len(conv.title) > 40 else conv.title
            print(f"   {i}. {title} - {len(conv.messages)} mensajes")

        # Análisis de participantes únicos
        all_participants = set()
        for conv in conversations:
            for participant in conv.participants:
                if not participant.is_self:
                    all_participants.add(participant.name)

        print(f"\n👥 Contactos únicos: {len(all_participants)}")

        return True

    except Exception as e:
        print(f"❌ Error durante carga múltiple: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_analysis_generation():
    """Prueba la generación de análisis."""

    print("\n" + "=" * 50)
    print("🔍 Prueba de Generación de Análisis")
    print("=" * 50)

    try:
        from instagram_analyzer.parsers.conversation_parser import ConversationParser
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False

    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"

    parser = ConversationParser(data_root)

    try:
        # Cargar conversaciones
        conversations = parser.parse_all_conversations(inbox_dir)
        print(f"📥 Conversaciones cargadas: {len(conversations)}")

        # Generar análisis
        print("🧠 Generando análisis...")
        analysis = parser.generate_conversation_analysis(conversations)

        print(f"✅ Análisis generado exitosamente")
        print(f"\n📈 Resultados:")
        print(f"   • Total conversaciones: {analysis.total_conversations}")
        print(f"   • Total mensajes: {analysis.total_messages:,}")
        print(f"   • Contactos únicos: {analysis.unique_contacts}")

        # Patrones temporales
        if analysis.messaging_by_hour:
            peak_hour = max(analysis.messaging_by_hour.items(), key=lambda x: x[1])
            print(f"   • Hora más activa: {peak_hour[0]}:00 ({peak_hour[1]} mensajes)")

        if analysis.messaging_by_day:
            peak_day = max(analysis.messaging_by_day.items(), key=lambda x: x[1])
            print(f"   • Día más activo: {peak_day[0]} ({peak_day[1]} mensajes)")

        # Contactos frecuentes
        if analysis.most_frequent_contacts:
            print(f"\n💬 Top 3 contactos más frecuentes:")
            for i, contact in enumerate(analysis.most_frequent_contacts[:3], 1):
                name = (
                    contact["name"][:25] + "..."
                    if len(contact["name"]) > 25
                    else contact["name"]
                )
                print(f"   {i}. {name} - {contact['total_messages']} mensajes")

        # Tipos de mensaje
        if analysis.message_type_distribution:
            print(f"\n📱 Tipos de mensaje:")
            for msg_type, count in list(analysis.message_type_distribution.items())[:3]:
                print(f"   • {msg_type}: {count}")

        # Exportar a JSON
        output_dir = Path("conversation_analysis")
        output_dir.mkdir(exist_ok=True)

        analysis_file = output_dir / "simple_analysis.json"
        analysis_data = analysis.model_dump()

        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Análisis exportado: {analysis_file}")

        return True

    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Función principal de pruebas."""

    print("🚀 PRUEBAS DE ANÁLISIS DE CONVERSACIONES")
    print("=" * 60)

    # Lista de pruebas
    tests = [
        ("Parser Individual", test_conversation_parser_only),
        ("Múltiples Conversaciones", test_multiple_conversations),
        ("Generación de Análisis", test_analysis_generation),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        print("-" * 40)

        try:
            success = test_func()
            results[test_name] = success
            if success:
                print(f"✅ {test_name} - EXITOSO")
            else:
                print(f"❌ {test_name} - FALLÓ")
        except Exception as e:
            print(f"💥 {test_name} - ERROR: {e}")
            results[test_name] = False

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    successful = sum(1 for success in results.values() if success)
    total = len(results)

    for test_name, success in results.items():
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        print(f"   {test_name}: {status}")

    print(f"\n🎯 Resultado final: {successful}/{total} pruebas exitosas")

    if successful == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("\n💡 Próximos pasos:")
        print("   • Revisar archivos generados en conversation_analysis/")
        print("   • Explorar análisis más detallados")
        print("   • Implementar visualizaciones")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar errores arriba.")

    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
