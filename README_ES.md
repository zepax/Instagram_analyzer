# Analizador de Instagram

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/gestión%20de%20dependencias-poetry-blue)](https://python-poetry.org/)
[![Code Style](https://img.shields.io/badge/estilo%20de%20código-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-aprobados-brightgreen)](#testing)
[![Coverage](https://img.shields.io/badge/cobertura-80%2B%25-brightgreen)](#testing)

Una herramienta completa de análisis para exportaciones de datos de Instagram. Analiza tu actividad de Instagram, genera insights y crea reportes detallados sobre tus patrones de uso en redes sociales.

## ✨ Características Principales

### 📊 Procesamiento de Datos
- **Soporte Multi-Formato**: Maneja el formato de exportación JSON de Instagram con detección automática de estructura
- **Análisis de Contenido**: Posts, historias, reels, comentarios, likes e información de perfil
- **Validación de Datos**: Validación exhaustiva y reporte de errores
- **Protección de Privacidad**: Procesamiento local con opciones de anonimización
- **Optimizado para Rendimiento**: Carga perezosa y almacenamiento en caché para uso eficiente de memoria

### 🔍 Capacidades de Análisis
- **Estadísticas Básicas**: Conteos de contenido, métricas de engagement y resúmenes de actividad
- **Análisis Temporal**: Patrones de actividad, horarios de publicación y análisis de tendencias
- **Análisis de Engagement**: Ratios de likes/comentarios, patrones de interacción y métricas de rendimiento
- **Insights de Contenido**: Análisis de hashtags, distribución de tipos de media y patrones de contenido
- **Análisis de Perfil**: Actividad de cuenta, interacciones de seguidores y estadísticas de uso

### 📈 Características Avanzadas
- **Aprendizaje Automático**: Análisis de sentimiento, predicción de engagement y categorización de contenido
- **Sistema de Caché**: Almacenamiento en caché de tres niveles (memoria, disco, base de datos) para mejor rendimiento
- **Opciones de Exportación**: Reportes HTML, datos JSON y resúmenes PDF
- **Interfaz CLI**: Herramientas de línea de comandos para procesamiento por lotes y automatización
- **Integración API**: Acceso programático para flujos de trabajo de análisis personalizados

## 🚀 Instalación

### Requisitos Previos
- Python 3.9 o superior
- Poetry (recomendado) o pip

### Configuración Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/instagram-data-mining.git
cd instagram-data-mining

# Instalar dependencias con Poetry (recomendado)
poetry install

# Activar el entorno virtual
poetry shell
```

### Instalación Alternativa

```bash
# Instalar con pip
pip install -e .

# O instalar grupos específicos de dependencias
poetry install --with dev,ml
```

## 🔧 Uso

### Interfaz de Línea de Comandos

La herramienta CLI principal es `instagram-miner` con los siguientes comandos:

#### 1. Validar Exportación de Datos

```bash
# Validar la estructura de exportación de datos de Instagram
instagram-miner validate /ruta/a/exportacion/instagram

# Con salida detallada
instagram-miner validate /ruta/a/exportacion/instagram -v
```

#### 2. Obtener Información Básica

```bash
# Mostrar información básica sobre la exportación de datos
instagram-miner info /ruta/a/exportacion/instagram
```

#### 3. Analizar Datos

```bash
# Análisis básico con reporte HTML
instagram-miner analyze /ruta/a/exportacion/instagram

# Especificar directorio de salida y formato
instagram-miner analyze /ruta/a/exportacion/instagram -o ./output -f html

# Incluir análisis de medios (más lento pero más completo)
instagram-miner analyze /ruta/a/exportacion/instagram --include-media

# Anonimizar datos sensibles en reportes
instagram-miner analyze /ruta/a/exportacion/instagram --anonymize

# Generar reporte PDF
instagram-miner analyze /ruta/a/exportacion/instagram -f pdf -o ./reportes
```

#### Opciones Globales

```bash
# Habilitar logging detallado
instagram-miner -v analyze /ruta/a/datos

# Establecer nivel de log específico
instagram-miner --log-level DEBUG analyze /ruta/a/datos

# Habilitar logging a archivo
instagram-miner --log-file ./logs analyze /ruta/a/datos
```

### API Programática

#### Uso Básico

```python
from instagram_analyzer import InstagramAnalyzer

# Inicializar el analizador
analyzer = InstagramAnalyzer("/ruta/a/exportacion/instagram")

# Cargar datos (opcional - usa carga perezosa por defecto)
analyzer.load_data()

# Validar datos
validation = analyzer.validate_data()
print(f"Datos cargados: {validation['data_loaded']['valid']}")

# Realizar análisis
results = analyzer.analyze()

# Exportar resultados
analyzer.export_html("./output")
analyzer.export_json("./output/data.json")
```

#### Uso Avanzado

```python
from instagram_analyzer import InstagramAnalyzer

# Inicializar con opciones personalizadas
analyzer = InstagramAnalyzer(
    data_path="/ruta/a/exportacion",
    lazy_loading=True  # Habilitar carga perezosa para datasets grandes
)

# Acceder a tipos de datos específicos
posts = analyzer.posts  # Retorna posts con carga perezosa
stories = analyzer.stories  # Retorna historias con carga perezosa
profile = analyzer.profile  # Retorna información del perfil

# Generar análisis específicos
stats = analyzer.basic_stats
temporal = analyzer.temporal_analysis
engagement = analyzer.engagement_analysis

# Exportar con opciones
analyzer.export_html(
    output_path="./reportes",
    anonymize=True,
    include_media=True
)
```

### Tipos de Datos Soportados

El analizador soporta los siguientes tipos de datos de Instagram:

- ✅ **Posts**: Posts individuales y carruseles con metadata
- ✅ **Historias**: Historias regulares y archivadas
- ✅ **Reels**: Contenido de video de formato corto
- ✅ **Comentarios**: Comentarios en posts y reels
- ✅ **Likes**: Posts y comentarios con like
- ✅ **Perfil**: Información de cuenta y configuraciones
- ✅ **Seguidores/Siguiendo**: Listas de conexiones
- ✅ **Interacciones de Historias**: Visualizaciones de historias, encuestas, preguntas
- ✅ **Contenido Archivado**: Posts previamente archivados
- ✅ **Eliminados Recientemente**: Contenido eliminado (si está disponible)

## 📁 Estructura de Datos

### Formato de Exportación de Instagram

La herramienta espera datos de Instagram en el formato oficial de exportación JSON:

```
instagram-export/
├── your_instagram_activity/
│   ├── media/
│   │   ├── posts_1.json
│   │   ├── stories.json
│   │   └── archived_posts.json
│   ├── comments/
│   │   ├── post_comments_1.json
│   │   └── reels_comments.json
│   └── likes/
│       ├── liked_posts.json
│       └── liked_comments.json
├── media/
│   ├── posts/
│   │   └── YYYYMM/
│   │       └── *.jpg
│   └── stories/
│       └── YYYYMM/
│           └── *.jpg
└── personal_information/
    └── personal_information/
        └── personal_information.json
```

### Validación de Datos

El analizador realiza validación exhaustiva:

```python
validation = analyzer.validate_data()

# Verificar resultados de validación
if validation["data_loaded"]["valid"]:
    print(f"Cargado: {validation['data_loaded']['details']}")
    
if validation["profile_data"]["valid"]:
    print("Información de perfil encontrada")
    
if validation["content_found"]["valid"]:
    print(f"Contenido total: {validation['content_found']['count']}")
```

## 🔒 Privacidad y Seguridad

### Procesamiento Local
- **Sin Conexiones Externas**: Todo el procesamiento de datos ocurre localmente
- **Sin Transmisión de Datos**: Tus datos nunca salen de tu máquina
- **Operación Offline**: Funciona sin conexión a internet

### Características de Anonimización
- **Eliminación de Datos Personales**: Elimina nombres de usuario, nombres mostrados e identificadores
- **Limpieza de Metadata**: Remueve datos de ubicación e información del dispositivo
- **Sanitización de Reportes**: Genera reportes compartibles sin datos sensibles

### Seguridad de Datos
- **Procesamiento Seguro**: Usa archivos temporales seguros y manejo de memoria
- **Protección de Caché**: Almacenamiento en caché encriptado para datos sensibles
- **Auditoría**: Logging exhaustivo de todas las actividades de procesamiento de datos

## 📊 Resultados del Análisis

### Estadísticas Básicas
```python
stats = analyzer.basic_stats
print(f"Posts: {stats.posts_count}")
print(f"Historias: {stats.stories_count}")
print(f"Tasa de engagement: {stats.engagement_rate:.2%}")
```

### Análisis Temporal
```python
temporal = analyzer.temporal_analysis
print(f"Hora más activa: {temporal.peak_hour}")
print(f"Día más activo: {temporal.peak_day}")
print(f"Consistencia de actividad: {temporal.consistency_score:.2f}")
```

### Análisis de Contenido
```python
content = analyzer.content_analysis
print(f"Hashtags principales: {content.top_hashtags}")
print(f"Tipos de media: {content.media_distribution}")
print(f"Longitud promedio de descripción: {content.avg_caption_length}")
```

## 🛠️ Desarrollo

### Configurar Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
poetry install --with dev

# Instalar hooks de pre-commit
poetry run pre-commit install

# Ejecutar tests
poetry run pytest

# Ejecutar con cobertura
poetry run pytest --cov=src/instagram_analyzer
```

### Calidad de Código

```bash
# Formatear código
poetry run black src/instagram_analyzer/ tests/

# Ordenar imports
poetry run isort src/instagram_analyzer/ tests/

# Verificación de tipos
poetry run mypy src/instagram_analyzer/

# Linter de código
poetry run flake8 src/instagram_analyzer/

# Ejecutar todas las verificaciones de calidad
make quality
```

### Pruebas

```bash
# Ejecutar todas las pruebas
PYTHONPATH=src poetry run pytest

# Ejecutar archivo de prueba específico
PYTHONPATH=src poetry run pytest tests/unit/test_models.py

# Ejecutar con reporte de cobertura
PYTHONPATH=src poetry run pytest --cov=src/instagram_analyzer --cov-report=html
```

## 🏗️ Arquitectura

### Componentes Principales

- **`core/analyzer.py`**: Clase principal `InstagramAnalyzer`
- **`parsers/`**: Módulos de parseo y validación de datos
- **`models/`**: Modelos de datos Pydantic para todos los tipos de contenido de Instagram
- **`analyzers/`**: Módulos de análisis para estadísticas e insights
- **`exporters/`**: Generación de reportes (HTML, JSON, PDF)
- **`cache/`**: Sistema de caché de tres niveles
- **`ml/`**: Modelos de aprendizaje automático y características
- **`utils/`**: Funciones de utilidad y helpers

### Flujo de Datos

1. **Detección de Datos**: Detecta automáticamente la estructura de exportación de Instagram
2. **Validación**: Valida la integridad y formato de los datos
3. **Parseo**: Convierte JSON a objetos Python tipados
4. **Análisis**: Genera estadísticas e insights
5. **Exportación**: Crea reportes en múltiples formatos

## 🤝 Contribuyendo

¡Damos la bienvenida a las contribuciones! Por favor consulta nuestras [Guías de Contribución](CONTRIBUTING.md) para más detalles.

### Flujo de Trabajo de Desarrollo

1. Hacer fork del repositorio
2. Crear una rama de características
3. Hacer tus cambios
4. Agregar pruebas para nueva funcionalidad
5. Asegurar que todas las pruebas pasen
6. Enviar un pull request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Construido para usuarios de Instagram conscientes de la privacidad
- Gracias a todos los contribuyentes y beta testers
- Agradecimiento especial a la comunidad de ciencia de datos de Python

## 📞 Soporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/instagram-data-mining/issues)
- 💬 **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/instagram-data-mining/discussions)
- 📖 **Documentación**: [Documentación Completa](docs/README.md)

---

**Descargo de responsabilidad**: Esta herramienta no está afiliada con Meta/Instagram. Está diseñada para ayudar a los usuarios a analizar sus propios datos exportados para insights personales y conciencia de privacidad.