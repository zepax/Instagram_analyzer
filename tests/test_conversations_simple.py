import json
from pathlib import Path

import pytest


# --- Pytest fixture para preparar datos de prueba ---
@pytest.fixture(scope="module")
def conversations_dir(tmp_path_factory):
    """
    Crea un directorio temporal con una estructura mínima de conversaciones para pruebas.
    """
    import json

    base = tmp_path_factory.mktemp("ig_testdata")
    inbox = base / "your_instagram_activity" / "messages" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    # Crear un archivo de conversación válido
    conv_dir = inbox / "conv1"
    conv_dir.mkdir()
    msg_file = conv_dir / "message_1.json"
    test_data = {
        "participants": [{"name": "John Doe"}, {"name": "Alice Doe"}],
        "messages": [
            {
                "sender_name": "Alice Doe",
                "timestamp_ms": 1701879445369,
                "content": "Por los colores",
                "is_geoblocked_for_viewer": False,
                "is_unsent_image_by_messenger_kid_parent": False,
            }
        ],
        "title": "John & Alice",
        "is_still_participant": True,
        "thread_path": "inbox/1295475635182545",
        "magic_words": [],
    }
    msg_file.write_text(
        json.dumps(test_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return base


@pytest.mark.unit
def test_conversation_parser_only(conversations_dir):
    """
    Prueba solo el parser de conversaciones sin dependencias del core.
    Valida que se pueda parsear una conversación mínima.
    """
    from instagram_analyzer.parsers.conversation_parser import ConversationParser

    data_root = conversations_dir
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"
    conversation_files = []
    for conv_dir in inbox_dir.iterdir():
        if conv_dir.is_dir():
            message_files = list(conv_dir.glob("message_*.json"))
            conversation_files.extend(message_files)
    assert conversation_files, "No se encontraron archivos de conversación"
    parser = ConversationParser(data_root)
    test_file = conversation_files[0]
    try:
        conversation = parser.parse_conversation_file(test_file)
        assert conversation is not None, "Error en parsing - conversation es None"
        assert hasattr(conversation, "messages"), "Conversación sin campo 'messages'"
        assert isinstance(
            conversation.messages, list
        ), "El campo 'messages' no es una lista"
        assert len(conversation.messages) > 0, "Conversación sin mensajes"
    except Exception as e:
        raise AssertionError(f"Error durante parsing: {e}") from e


@pytest.mark.integration
def test_multiple_conversations(conversations_dir):
    """
    Prueba parsing de múltiples conversaciones.
    Valida que se puedan cargar varias conversaciones y obtener estadísticas básicas.
    """
    from instagram_analyzer.models.conversation import ConversationType
    from instagram_analyzer.parsers.conversation_parser import ConversationParser

    data_root = conversations_dir
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"
    parser = ConversationParser(data_root)
    try:
        conversations = parser.parse_all_conversations(inbox_dir)
        assert conversations, "No se cargaron conversaciones"
        total_messages = sum(len(conv.messages) for conv in conversations)
        assert total_messages > 0
        direct_convs = len(
            [c for c in conversations if c.conversation_type == ConversationType.DIRECT]
        )
        group_convs = len(
            [c for c in conversations if c.conversation_type == ConversationType.GROUP]
        )
        assert direct_convs + group_convs == len(conversations)
    except Exception as e:
        raise AssertionError(f"Error durante carga múltiple: {e}") from e


# --- Test de error: directorio inexistente ---
@pytest.mark.unit
def test_conversation_parser_dir_inexistente():
    """
    Valida que el parser lance FileNotFoundError si el directorio de conversaciones no existe.
    """

    from instagram_analyzer.parsers.conversation_parser import ConversationParser

    data_root = Path("/tmp/dir_que_no_existe_1234567890")
    parser = ConversationParser(data_root)
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"
    with pytest.raises(FileNotFoundError):
        parser.parse_all_conversations(inbox_dir)


@pytest.mark.integration
def test_analysis_generation(conversations_dir):
    """Prueba la generación de análisis usando datos temporales del fixture."""

    from instagram_analyzer.parsers.conversation_parser import ConversationParser

    data_root = conversations_dir
    inbox_dir = data_root / "your_instagram_activity" / "messages" / "inbox"
    parser = ConversationParser(data_root)

    try:
        # Cargar conversaciones
        conversations = parser.parse_all_conversations(inbox_dir)
        assert conversations, "No se cargaron conversaciones"

        # Generar análisis
        analysis = parser.generate_conversation_analysis(conversations)
        assert analysis.total_conversations > 0
        assert analysis.total_messages > 0
        assert isinstance(analysis.unique_contacts, int)

        # Exportar a JSON en un directorio temporal
        output_dir = Path("conversation_analysis")
        output_dir.mkdir(exist_ok=True)
        analysis_file = output_dir / "simple_analysis.json"
        analysis_data = analysis.model_dump()
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise AssertionError(f"Error durante análisis: {e}") from e
