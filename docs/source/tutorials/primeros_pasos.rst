==========================
Tutorial: Primeros Pasos
==========================

Este tutorial te guía desde la instalación hasta la generación de reportes avanzados usando la CLI y la API de Python.

1. Instalación y entorno de desarrollo
--------------------------------------

.. code-block:: bash

    # Instala dependencias y activa el entorno virtual
    poetry install
    poetry shell

    # Ejecuta tests rápidos y verifica calidad de código
    PYTHONPATH=src poetry run pytest
    make quality

2. Análisis básico desde la CLI
------------------------------

.. code-block:: bash

    # Analiza un export de Instagram y genera un reporte HTML anonimizado
    poetry run instagram-analyzer analyze /ruta/al/export --format html --anonymize

    # Exporta en PDF o JSON
    poetry run instagram-analyzer analyze /ruta/al/export --format pdf
    poetry run instagram-analyzer analyze /ruta/al/export --format json

    # Muestra información resumida del export
    poetry run instagram-analyzer info /ruta/al/export

    # Valida la estructura del export
    poetry run instagram-analyzer validate /ruta/al/export

3. Análisis avanzado y opciones útiles
--------------------------------------

.. code-block:: bash

    # Análisis con barra de progreso y sin cache
    poetry run instagram-analyzer analyze /ruta/al/export --format html --show-progress --no-cache

    # Branding personalizado en el reporte HTML
    poetry run instagram-analyzer analyze /ruta/al/export --format html --brand "MiEmpresa" --logo /ruta/logo.png

    # Procesamiento paralelo para datasets grandes
    poetry run instagram-analyzer analyze /ruta/al/export --format html --parallel

    # Ayuda y listado de comandos
    poetry run instagram-analyzer --help
    poetry run instagram-analyzer analyze --help

4. Uso programático desde Python (API)
--------------------------------------

.. code-block:: python

    from instagram_analyzer.core.analyzer import InstagramAnalyzer
    from instagram_analyzer.exporters.html_exporter import HTMLExporter

    analyzer = InstagramAnalyzer("/ruta/al/export")
    analyzer.load_data()
    results = analyzer.analyze()
    print(results['basic_stats'])

    # Exporta resultados a HTML
    exporter = HTMLExporter()
    exporter.export(results, output_path="output/report.html")

5. Integración de Machine Learning y análisis de red
----------------------------------------------------

.. code-block:: python

    from instagram_analyzer.ml.sentiment_analyzer import SentimentAnalyzer
    from instagram_analyzer.analyzers.network_analyzer import NetworkAnalyzer

    sentiments = SentimentAnalyzer().analyze(results['posts'])
    network = NetworkAnalyzer(results['posts'])
    graph_data = network.get_network_graph()
    print(sentiments, graph_data)

6. Personalización y configuración avanzada
------------------------------------------

.. code-block:: python

    from instagram_analyzer.config import load_config

    config = load_config("config/config.yaml")
    analyzer = InstagramAnalyzer("/ruta/al/export", config=config)
    analyzer.load_data()
    # ...continúa con el análisis...

7. Recursos adicionales
----------------------

- Consulta la documentación API para detalles de cada módulo.
- Revisa los ejemplos de uso en `usage_examples.rst`.
- Usa `make quality` y los pre-commit hooks para mantener la calidad del código.
