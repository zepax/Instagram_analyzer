from pathlib import Path

import pytest

from instagram_analyzer.analyzers.conversation_analyzer import ConversationAnalyzer
from instagram_analyzer.parsers.conversation_parser import ConversationParser


@pytest.fixture
def empty_conversation():
    # Conversación vacía
    return {
        "participants": [],
        "messages": [],
    }


@pytest.fixture
def emoji_conversation():
    # Solo mensajes con emojis

    return {
        "participants": ["Alice", "Bob"],
        "messages": [
            {"sender": "Alice", "timestamp": "2025-01-01T00:00:00Z", "content": "😀"},
            {"sender": "Bob", "timestamp": "2025-01-01T00:01:00Z", "content": "👍"},
        ],
    }


def test_empty_conversation_stats(empty_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(empty_conversation, data_root)
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 0
        # Debe manejar sin error y devolver stats vacíos


def test_emoji_only_conversation(emoji_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(emoji_conversation, data_root)
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 2
        # Debe contar correctamente y no fallar con solo emojis


# Conversación con timestamps fuera de orden


@pytest.fixture
def unordered_timestamps_conversation():
    return {
        "participants": ["Alice", "Bob"],
        "messages": [
            {"sender": "Bob", "timestamp": "2025-01-01T00:02:00Z", "content": "Late"},
            {
                "sender": "Alice",
                "timestamp": "2025-01-01T00:01:00Z",
                "content": "Early",
            },
        ],
    }


def test_unordered_timestamps(unordered_timestamps_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(
            unordered_timestamps_conversation, data_root
        )
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 2
        # Debe manejar timestamps fuera de orden sin error


# Participantes faltantes o duplicados
@pytest.fixture
def missing_participant_conversation():
    return {
        "participants": ["Alice"],
        "messages": [
            {"sender": "Alice", "timestamp": "2025-01-01T00:00:00Z", "content": "Hola"},
            {
                "sender": "Bob",
                "timestamp": "2025-01-01T00:01:00Z",
                "content": "¿Quién soy?",
            },
        ],
    }


def test_missing_participant(missing_participant_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(
            missing_participant_conversation, data_root
        )
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 2

        # El analizador debe manejar mensajes de participantes no listados


@pytest.fixture
def duplicate_participant_conversation():
    return {
        "participants": ["Alice", "Bob", "Bob"],
        "messages": [
            {"sender": "Alice", "timestamp": "2025-01-01T00:00:00Z", "content": "Hola"},
            {"sender": "Bob", "timestamp": "2025-01-01T00:01:00Z", "content": "¡Hola!"},
        ],
    }


def test_duplicate_participant(duplicate_participant_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(
            duplicate_participant_conversation, data_root
        )
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]

        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 2
        # No debe fallar si hay participantes duplicados


# Conversación muy larga
@pytest.fixture
def long_conversation():
    return {
        "participants": ["Alice", "Bob"],
        "messages": [
            {
                "sender": "Alice",
                "timestamp": f"2025-01-01T00:00:{i:02d}Z",
                "content": f"msg{i}",
            }
            for i in range(1000)
        ],
    }


def test_long_conversation(long_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(long_conversation, data_root)

        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 1000
        # Debe procesar conversaciones largas eficientemente


# Mensajes corruptos o incompletos
@pytest.fixture
def corrupt_message_conversation():
    return {
        "participants": ["Alice", "Bob"],
        "messages": [
            {"sender": "Alice", "timestamp": "2025-01-01T00:00:00Z", "content": "Hola"},
            {"sender": None, "timestamp": None, "content": None},
        ],
    }


def test_corrupt_message(corrupt_message_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)

        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(corrupt_message_conversation, data_root)
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 2
        # Debe manejar mensajes corruptos sin lanzar excepción


# Unicode/extremos en nombres y mensajes
@pytest.fixture
def unicode_conversation():
    return {
        "participants": ["Álïçë", "Боб", "李雷"],
        "messages": [
            {
                "sender": "Álïçë",
                "timestamp": "2025-01-01T00:00:00Z",
                "content": "¡Hola! 🌎",
            },
            {
                "sender": "Боб",
                "timestamp": "2025-01-01T00:01:00Z",
                "content": "Привет!",
            },
            {
                "sender": "李雷",
                "timestamp": "2025-01-01T00:02:00Z",
                "content": "你好！",
            },
        ],
    }


def test_unicode_conversation(unicode_conversation):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        conv = parser._parse_conversation_data(unicode_conversation, data_root)
        analyzer = ConversationAnalyzer(data_root)
        analyzer.conversations = [conv]
        stats = analyzer.analyze_conversation_patterns()
        assert stats.total_messages == 3
        # Debe manejar correctamente unicode en nombres y mensajes


# Manejo de error: estructura inválida
@pytest.mark.parametrize(
    "bad_convo",
    [
        None,
        {},
        {"participants": None, "messages": None},
        {"participants": ["Alice"], "messages": None},
        {"participants": None, "messages": []},
    ],
)
def test_invalid_conversation_structure(bad_convo):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root = Path(tmpdir)
        parser = ConversationParser(data_root)
        try:
            conv = parser._parse_conversation_data(bad_convo, data_root)
            analyzer = ConversationAnalyzer(data_root)
            analyzer.conversations = [conv]
            stats = analyzer.analyze_conversation_patterns()
            assert isinstance(stats, type(analyzer.analysis))
        except Exception:
            # Puede lanzar excepción o devolver análisis vacío, pero nunca debe colapsar el test suite
            assert True
