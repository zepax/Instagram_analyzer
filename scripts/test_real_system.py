#!/usr/bin/env python3
"""Script de prueba real para validar el sistema reorganizado."""

import sys
from pathlib import Path

# Asegurar que podemos importar desde src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Prueba que todos los imports funcionen."""
    print("🔍 Probando imports...")

    try:
        from instagram_analyzer import InstagramAnalyzer

        print("✅ InstagramAnalyzer importado correctamente")

        from instagram_analyzer.models import Conversation, Post, User

        print("✅ Modelos importados correctamente")

        from instagram_analyzer.parsers import DataDetector, JSONParser

        print("✅ Parsers importados correctamente")

        from instagram_analyzer.analyzers import BasicStatsAnalyzer

        print("✅ Analyzers importados correctamente")

        from instagram_analyzer.extractors import ConversationExtractor

        print("✅ Extractors importados correctamente")

        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False


def test_data_structure():
    """Prueba que los datos estén en la estructura correcta."""
    print("\n📁 Verificando estructura de datos...")

    data_path = Path("data/sample_exports/instagram-pcFuHXmB")
    if not data_path.exists():
        print(f"❌ Datos no encontrados en: {data_path}")
        return False

    print(f"✅ Datos encontrados en: {data_path}")

    # Verificar subdirectorios esperados
    expected_dirs = [
        "messages",
        "your_instagram_activity",
        "personal_information",
        "connections",
    ]

    found_dirs = []
    for dir_name in expected_dirs:
        dir_path = data_path / dir_name
        if dir_path.exists():
            found_dirs.append(dir_name)
            print(f"✅ {dir_name}/ encontrado")
        else:
            print(f"⚠️  {dir_name}/ no encontrado")

    return len(found_dirs) > 0


def test_basic_functionality():
    """Prueba funcionalidad básica del analyzer."""
    print("\n🧪 Probando funcionalidad básica...")

    try:
        from instagram_analyzer.core.analyzer import InstagramAnalyzer

        data_path = Path("data/sample_exports/instagram-pcFuHXmB")
        analyzer = InstagramAnalyzer(data_path)
        print("✅ Analyzer creado correctamente")

        # Verificar que puede detectar datos
        print("🔍 Detectando tipos de datos disponibles...")

        # Basic validation to use the analyzer
        _ = analyzer.validate_data()

        # Este es un test básico sin ejecutar análisis completo
        print("✅ Analyzer inicializado sin errores")

        return True
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_conversation_detection():
    """Prueba detección básica de conversaciones."""
    print("\n💬 Probando detección de conversaciones...")

    try:
        from instagram_analyzer.extractors.conversation_extractor import (
            ConversationExtractor,
        )

        data_path = Path("data/sample_exports/instagram-pcFuHXmB")
        extractor = ConversationExtractor(data_path)
        print("✅ ConversationExtractor creado correctamente")

        # Basic validation to use the extractor
        _ = extractor.validate_data_structure()

        # Verificar que puede leer la estructura básica
        messages_path = data_path / "messages"
        if messages_path.exists():
            print(f"✅ Directorio de mensajes encontrado: {messages_path}")

            # Contar subdirectorios (conversaciones potenciales)
            subdirs = [d for d in messages_path.iterdir() if d.is_dir()]
            print(f"📊 Directorios de conversaciones encontrados: {len(subdirs)}")

            if len(subdirs) > 0:
                print("✅ Datos de conversaciones disponibles")
                return True

        print("⚠️  No se encontraron datos de conversaciones")
        return False

    except Exception as e:
        print(f"❌ Error en detección de conversaciones: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("🚀 PRUEBA REAL DEL SISTEMA REORGANIZADO")
    print("=" * 50)

    results = []

    # Ejecutar todas las pruebas
    results.append(("Imports", test_imports()))
    results.append(("Estructura de datos", test_data_structure()))
    results.append(("Funcionalidad básica", test_basic_functionality()))
    results.append(("Detección conversaciones", test_conversation_detection()))

    # Mostrar resultados
    print("\n📊 RESUMEN DE RESULTADOS:")
    print("=" * 30)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False

    print("=" * 30)
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema está listo para análisis reales")
    else:
        print("⚠️  Algunas pruebas fallaron")
        print("🔧 Revisar los errores arriba para solucionar")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
