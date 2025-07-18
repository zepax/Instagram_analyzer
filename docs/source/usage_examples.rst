========================================
Ejemplos de Uso por Módulo (Python API)
========================================

Parsers: DataDetector, JSONParser, EngagementParser
---------------------------------------------------

.. code-block:: python

    from instagram_analyzer.parsers.data_detector import DataDetector
    from instagram_analyzer.parsers.json_parser import JSONParser
    from instagram_analyzer.parsers.engagement_parser import EngagementParser

    # Detecta archivos relevantes en el export de Instagram
    detector = DataDetector("/path/to/export/")
    detected = detector.detect()
    print("Archivos detectados:", detected)

    # Parseo de posts, stories, reels, etc.
    parser = JSONParser()
    posts = parser.parse_posts(detected['posts'])
    stories = parser.parse_stories(detected['stories'])
    reels = parser.parse_reels(detected['reels'])

    # Engagement: likes, comentarios, etc.
    engagement_parser = EngagementParser()
    liked_posts = engagement_parser.parse_liked_posts(detected['liked_posts'])
    post_comments = engagement_parser.parse_post_comments(detected['post_comments'])

Modelos (Pydantic)
------------------

.. code-block:: python

    from instagram_analyzer.models import ConversationMessage, Media, Profile
    from datetime import datetime

    msg = ConversationMessage(
        content="¡Hola!",
        timestamp=datetime.now(),
        sender_name="Usuario"
    )
    print(msg.json())

    profile = Profile(username="usuario", full_name="Nombre Apellido")
    print(profile)

Análisis: InstagramAnalyzer y Analyzers
---------------------------------------

.. code-block:: python

    from instagram_analyzer.core.analyzer import InstagramAnalyzer

    analyzer = InstagramAnalyzer("/path/to/export/")
    analyzer.load_data()
    stats = analyzer.analyze()
    print(stats['basic_stats'])

    # Análisis avanzado con ML
    ml_results = analyzer.analyze_with_ml()
    print(ml_results['sentiment'])

Exportadores: HTML, PDF, JSON
-----------------------------

.. code-block:: python

    from instagram_analyzer.exporters.html_exporter import HTMLExporter
    from instagram_analyzer.exporters.pdf_exporter import PDFExporter
    from instagram_analyzer.exporters.json_exporter import JSONExporter

    exporter = HTMLExporter()
    exporter.export(stats, output_path="output/report.html")

    pdf_exporter = PDFExporter()
    pdf_exporter.export(stats, output_path="output/report.pdf")

    json_exporter = JSONExporter()
    json_exporter.export(stats, output_path="output/report.json")

Caching (Memory & Disk)
-----------------------

.. code-block:: python

    from instagram_analyzer.cache import cache_result

    @cache_result(cache_key_func=lambda path: f"posts_{hash(str(path))}")
    def expensive_parse(path):
        # parsing logic
        pass

    posts = expensive_parse("path/to/posts.json")

    # Uso directo de CacheManager
    from instagram_analyzer.cache.memory_cache import MemoryCache
    cache = MemoryCache()
    cache.set("key", "value")
    print(cache.get("key"))

Errores y Retry
---------------

.. code-block:: python

    from instagram_analyzer.exceptions import DataParsingError
    from instagram_analyzer.utils.retry_utils import with_retry

    @with_retry(max_attempts=3)
    def load_data(path):
        # load logic
        pass

    try:
        load_data("missing.json")
    except DataParsingError as e:
        print("Error al parsear datos:", e)

NetworkAnalyzer (Análisis de Red)
---------------------------------

.. code-block:: python

    from instagram_analyzer.analyzers.network_analyzer import NetworkAnalyzer

    network = NetworkAnalyzer(posts)
    graph_data = network.get_network_graph()
    print(graph_data)

Feature Engineering y ML
------------------------

.. code-block:: python

    from instagram_analyzer.analyzers.feature_engineer import FeatureEngineer
    from instagram_analyzer.ml.sentiment_analyzer import SentimentAnalyzer
    from instagram_analyzer.ml.engagement_predictor import EngagementPredictor

    features = FeatureEngineer().extract_features(posts)
    sentiments = SentimentAnalyzer().analyze(posts)
    engagement = EngagementPredictor().predict(posts)
    print(features, sentiments, engagement)

Parallel Processing
-------------------

.. code-block:: python

    from instagram_analyzer.utils.parallel_processor import ParallelProcessor

    def process_post(post):
        # procesamiento pesado
        return post['id']

    processor = ParallelProcessor()
    results = processor.run(posts, process_post)
    print(results)

Configuración y Utilidades
--------------------------

.. code-block:: python

    from instagram_analyzer.config import load_config

    config = load_config("config/config.yaml")
    print(config)

    # Privacy utils
    from instagram_analyzer.utils.privacy_utils import anonymize_text
    print(anonymize_text("Nombre Real"))
