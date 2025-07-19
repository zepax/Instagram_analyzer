import pytest

from instagram_analyzer.core import InstagramAnalyzer
from instagram_analyzer.exporters.html_exporter import HTMLExporter


@pytest.fixture
def empty_analysis_data(tmp_path):
    # Simula datos mínimos para exportar (sin posts, stories, reels)
    return {
        "stats": {},
        "charts_data": "{}",
        "network_data": "{}",
        "posts": [],
        "stories": [],
        "reels": [],
        "profile": {},
    }


@pytest.fixture
def dummy_analyzer(tmp_path, empty_analysis_data):
    # Crea un InstagramAnalyzer apuntando a un directorio temporal vacío
    analyzer = InstagramAnalyzer(data_path=tmp_path)
    # Monkeypatch para devolver datos vacíos en los métodos requeridos
    analyzer.analyze = lambda *args, **kwargs: empty_analysis_data
    analyzer._profile = None  # Tipo correcto para evitar error de tipo
    return analyzer


@pytest.mark.parametrize(
    "compact,max_items",
    [
        (False, 100),
        (True, 0),
        (True, 1000),
    ],
)
def test_html_exporter_empty_dataset(tmp_path, dummy_analyzer, compact, max_items):
    output_file = tmp_path / f"report_compact_{compact}_max_{max_items}.html"
    exporter = HTMLExporter()
    # No debe lanzar excepción ni generar HTML inválido
    exporter.export(
        analyzer=dummy_analyzer,
        output_path=output_file,
        compact=compact,
        max_items=max_items,
    )
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "<html" in content.lower()
    assert "No data" not in content  # El template debe manejar vacío de forma elegante
    # Puede agregarse más validaciones según el template


@pytest.mark.parametrize(
    "corrupt_field,corrupt_value,expected_exception",
    [
        ("stats", None, None),  # Campo stats como None
        ("charts_data", 123, None),  # charts_data no es string
        ("posts", "notalist", None),  # posts no es lista
        ("profile", None, None),  # profile como None
        ("network_data", "{notjson}", None),  # network_data malformado
    ],
)
def test_html_exporter_corrupt_data(
    tmp_path,
    dummy_analyzer,
    empty_analysis_data,
    corrupt_field,
    corrupt_value,
    expected_exception,
):
    # Crea una copia de los datos y corrompe el campo indicado
    corrupt_data = dict(empty_analysis_data)
    corrupt_data[corrupt_field] = corrupt_value
    dummy_analyzer.analyze = lambda *args, **kwargs: corrupt_data
    output_file = tmp_path / f"report_corrupt_{corrupt_field}.html"
    exporter = HTMLExporter()
    if expected_exception:
        with pytest.raises(expected_exception):
            exporter.export(
                analyzer=dummy_analyzer,
                output_path=output_file,
                compact=False,
                max_items=100,
            )
    else:
        # No debe lanzar excepción, solo debe manejar el error gracefully
        exporter.export(
            analyzer=dummy_analyzer,
            output_path=output_file,
            compact=False,
            max_items=100,
        )
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "<html" in content.lower()
        # El template debe manejar el campo corrupto sin romper el HTML


@pytest.mark.parametrize(
    "media_field,media_value",
    [
        ("thumbnail_url", "/non/existent/path.jpg"),
        ("media_url", "/ruta/falsa/video.mp4"),
    ],
)
def test_html_exporter_media_inexistente(
    tmp_path, dummy_analyzer, empty_analysis_data, media_field, media_value
):
    # Simula un post con media que apunta a una ruta inexistente
    post = {
        "id": "1",
        "caption": "Test post",
        media_field: media_value,
        "timestamp": "2025-01-01T00:00:00Z",
    }
    corrupt_data = dict(empty_analysis_data)
    corrupt_data["posts"] = [post]
    dummy_analyzer.analyze = lambda *args, **kwargs: corrupt_data
    output_file = tmp_path / f"report_media_{media_field}.html"
    exporter = HTMLExporter()
    exporter.export(
        analyzer=dummy_analyzer,
        output_path=output_file,
        compact=False,
        max_items=100,
    )
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "<html" in content.lower()
    # El HTML debe generarse aunque la media no exista


@pytest.mark.parametrize(
    "compact,max_items",
    [
        (True, 0),
        (True, 1),
        (True, 10000),
        (False, 0),
        (False, 10000),
    ],
)
def test_html_exporter_config_extremos(
    tmp_path, dummy_analyzer, empty_analysis_data, compact, max_items
):
    # Prueba el exporter con configuraciones extremas de compact y max_items
    dummy_analyzer.analyze = lambda *args, **kwargs: empty_analysis_data
    output_file = tmp_path / f"report_extremo_{compact}_{max_items}.html"
    exporter = HTMLExporter()
    exporter.export(
        analyzer=dummy_analyzer,
        output_path=output_file,
        compact=compact,
        max_items=max_items,
    )
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "<html" in content.lower()
    # El HTML debe generarse correctamente en todos los casos
