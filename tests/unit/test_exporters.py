import importlib


def test_exporters_module_import():
    """Ensure exporters package can be imported without errors."""
    module = importlib.import_module("instagram_analyzer.exporters")
    assert hasattr(module, "__all__")

