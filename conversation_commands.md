# Comandos para Probar Análisis de Conversaciones

## 🚀 Comandos Rápidos

### 1. Probar todas las funcionalidades nuevas
```bash
# Ejecutar script completo de pruebas
poetry run python test_conversations.py
```

### 2. Análisis básico con CLI existente (si se integra)
```bash
# Información general del dataset (incluye conversaciones)
poetry run python -m instagram_analyzer.cli info examples/instagram-florenescobar-2025-07-13-pcFuHXmB

# Validar integridad de datos
poetry run python -m instagram_analyzer.cli validate examples/instagram-florenescobar-2025-07-13-pcFuHXmB
```

## 📊 Comandos Detallados de Prueba

### 3. Análisis completo de conversaciones
```python
# En Python interactivo o script
from pathlib import Path
from instagram_analyzer.analyzers.conversation_analyzer import ConversationAnalyzer

# Configurar analizador
data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
analyzer = ConversationAnalyzer(data_root)

# Cargar y analizar
conversations = analyzer.load_conversations()
analysis = analyzer.analyze_conversation_patterns()

print(f"Total conversaciones: {len(conversations)}")
print(f"Total mensajes: {analysis.total_messages}")
print(f"Contactos únicos: {analysis.unique_contacts}")
```

### 4. Análisis de conversación específica
```python
# Parsear una conversación individual
from instagram_analyzer.parsers.conversation_parser import ConversationParser

data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
parser = ConversationParser(data_root)

# Analizar conversación específica
conv_file = data_root / "your_instagram_activity/messages/inbox/paolacastillo_513456650044931/message_1.json"
conversation = parser.parse_conversation_file(conv_file)

print(f"Conversación: {conversation.title}")
print(f"Mensajes: {len(conversation.messages)}")
print(f"Hilos: {len(conversation.threads)}")
```

### 5. Búsqueda en conversaciones
```python
# Buscar conversaciones por contenido
matches = analyzer.search_conversations("gracias")
print(f"Encontradas {len(matches)} conversaciones con 'gracias'")

# Buscar por participante
matches = analyzer.search_conversations("Paola", search_participants=True)
print(f"Conversaciones con Paola: {len(matches)}")
```

## 🔍 Comandos de Exploración

### 6. Explorar hilos de conversación
```python
# Obtener conversación específica
conversation = analyzer.get_conversation_by_id("paolacastillo_513456650044931")

if conversation:
    print(f"Hilos en la conversación:")
    for i, thread in enumerate(conversation.threads):
        print(f"  Hilo {i+1}: {len(thread.messages)} mensajes")
        print(f"    Duración: {thread.duration_minutes:.1f} minutos")
        print(f"    Tópico: {thread.topic}")
```

### 7. Análisis temporal detallado
```python
# Patrones de actividad
if analysis.messaging_by_hour:
    print("Actividad por hora:")
    for hour, count in sorted(analysis.messaging_by_hour.items()):
        print(f"  {hour:02d}:00 - {count} mensajes")

# Períodos pico
for period in analysis.peak_messaging_periods:
    print(f"Pico {period['type']}: {period['description']}")
```

### 8. Exportar y revisar resultados
```python
# Exportar análisis completo
output_dir = Path("conversation_analysis")
summary_file = analyzer.export_conversation_summary(output_dir)
print(f"Análisis exportado a: {summary_file}")

# El archivo contiene:
# - Estadísticas generales
# - Lista de todas las conversaciones
# - Métricas detalladas
# - Patrones temporales
```

## 📁 Estructura de Archivos Generados

```
conversation_analysis/
└── conversation_analysis_summary.json  # Resumen completo del análisis
```

## 🛠️ Comandos de Desarrollo/Debug

### 9. Probar parser individual
```python
# Listar todas las conversaciones disponibles
conv_dir = data_root / "your_instagram_activity/messages/inbox"
conversations = list(conv_dir.iterdir())
print(f"Conversaciones encontradas: {len(conversations)}")

# Probar parser en la primera conversación
if conversations:
    first_conv = conversations[0]
    message_files = list(first_conv.glob("message_*.json"))
    if message_files:
        conv = parser.parse_conversation_file(message_files[0])
        print(f"Parseada: {conv.title} con {len(conv.messages)} mensajes")
```

### 10. Verificar tipos de mensaje
```python
# Analizar tipos de mensaje en una conversación
message_types = {}
for msg in conversation.messages:
    msg_type = msg.message_type.value
    message_types[msg_type] = message_types.get(msg_type, 0) + 1

print("Tipos de mensaje encontrados:")
for msg_type, count in message_types.items():
    print(f"  {msg_type}: {count}")
```

## ⚠️ Solución de Problemas

### Si no encuentra conversaciones:
```bash
# Verificar estructura de archivos
ls -la examples/instagram-florenescobar-2025-07-13-pcFuHXmB/your_instagram_activity/messages/inbox/
```

### Si hay errores de importación:
```bash
# Reinstalar dependencias
poetry install

# Verificar instalación
poetry run python -c "from instagram_analyzer.analyzers.conversation_analyzer import ConversationAnalyzer; print('OK')"
```

### Para debugging detallado:
```python
# Activar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Ejecutar análisis con más información
analyzer = ConversationAnalyzer(data_root)
conversations = analyzer.load_conversations()
```

## 📈 Interpretación de Resultados

Los comandos generarán información sobre:

- **Estadísticas básicas**: Total de conversaciones, mensajes, contactos
- **Patrones temporales**: Horas/días más activos, períodos pico
- **Análisis de contenido**: Tipos de mensaje, tópicos populares
- **Métricas de interacción**: Tiempos de respuesta, hilos de conversación
- **Análisis social**: Contactos frecuentes, distribución grupal vs directa

¡Ejecuta `python test_conversations.py` para empezar!