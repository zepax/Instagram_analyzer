# 📚 Development Guidelines & Best Practices

## 🎯 **RECORDATORIO FUNDAMENTAL**

**SIEMPRE seguir el TODO.md y la estructura de carpetas organizada para mantener las mejores prácticas de desarrollo.**

---

## 📁 **Estructura de Directorios (OBLIGATORIA)**

### **Estructura Principal**

```
Instagram_analyzer/
├── src/
│   └── instagram_analyzer/          # 🔹 PAQUETE PRINCIPAL
│       ├── analyzers/               # 🔸 Análisis y estadísticas
│       ├── cache/                   # 🔸 Sistema de caché
│       ├── core/                    # 🔸 Funcionalidad central
│       ├── exporters/               # 🔸 Exportación de datos
│       ├── extractors/              # 🔸 Extracción de datos
│       ├── models/                  # 🔸 Modelos Pydantic
│       ├── parsers/                 # 🔸 Parseo de archivos
│       ├── templates/               # 🔸 Plantillas HTML/CSS
│       ├── utils/                   # 🔸 Utilidades compartidas
│       ├── cli.py                   # 🔸 Interfaz de línea de comandos
│       ├── exceptions.py            # 🔸 Excepciones personalizadas
│       └── logging_config.py        # 🔸 Configuración de logging
├── tests/                           # 🔹 TESTS CONSOLIDADOS
│   ├── integration/                 # 🔸 Tests de integración
│   ├── unit/                        # 🔸 Tests unitarios
│   └── test_*.py                    # 🔸 Tests adicionales
├── config/                          # 🔹 CONFIGURACIÓN CENTRALIZADA
│   ├── .flake8                      # 🔸 Configuración linting
│   ├── .pre-commit-config.yaml      # 🔸 Pre-commit hooks
│   └── pytest.ini                   # 🔸 Configuración pytest
├── backup/                          # 🔹 ARCHIVO HISTÓRICO
│   ├── analysis_results/            # 🔸 Resultados archivados
│   └── sessions/                    # 🔸 Sesiones archivadas
├── output/                          # 🔹 SALIDAS ORGANIZADAS
│   ├── htmlcov/                     # 🔸 Coverage HTML
│   └── coverage.xml                 # 🔸 Coverage XML
├── data/                            # 🔹 DATOS DE EJEMPLO
├── docs/                            # 🔹 DOCUMENTACIÓN
├── scripts/                         # 🔹 SCRIPTS UTILITARIOS
├── tools/                           # 🔹 HERRAMIENTAS DESARROLLO
└── .devcontainer/                   # 🔹 DESARROLLO CONTAINERIZADO
```

---

## 📋 **TODO.md - Prioridades Actuales**

### **🚀 SIGUIENTES TAREAS PRIORITARIAS:**

#### **Phase 1: Foundation & Quality (Sprint 1-2)**

- [ ] **HIGH**: Aumentar cobertura de tests a >80%
  - [ ] Tests para `EngagementParser`
  - [ ] Tests para `JSONParser` enrichment methods
  - [ ] Tests para exporters (HTML, PDF)
  - [ ] Tests para conversation analyzer
- [ ] **HIGH**: Documentación API completa con Sphinx
- [ ] **MEDIUM**: README mejorado con badges y ejemplos

#### **Phase 2: Performance & Scalability (Sprint 3-4)**

- [ ] **HIGH**: Implementar parallel processing
- [ ] **HIGH**: Streaming data processing
- [ ] **MEDIUM**: Background tasks con Celery

#### **Phase 3: Advanced Analytics (Sprint 5-6)**

- [ ] **HIGH**: Sentiment analysis
- [ ] **HIGH**: Topic modeling
- [ ] **MEDIUM**: Behavioral analysis

---

## 🛠️ **Mejores Prácticas de Desarrollo**

### **📂 Organización de Archivos**

1. **NUNCA** colocar archivos fuera de su directorio correspondiente
2. **SIEMPRE** usar `src/instagram_analyzer/` para código principal
3. **TODOS** los tests van en `tests/` con estructura `unit/` e `integration/`
4. **CONFIGURACIONES** centralizadas en `config/`
5. **ARCHIVOS TEMPORALES** en `backup/` o `output/`

### **📝 Convenciones de Código**

1. **Import Paths**: `from instagram_analyzer.module import Class`
2. **PYTHONPATH**: `PYTHONPATH=src` para todos los comandos
3. **Tests**: Usar `poetry run pytest` con configuración de pyproject.toml
4. **Linting**: Seguir configuración en `config/.flake8`
5. **Formatting**: Black + isort según configuración

### **🧪 Testing Guidelines**

```bash
# Tests unitarios
poetry run pytest tests/unit/ -v

# Tests de integración
poetry run pytest tests/integration/ -v

# Coverage completo
poetry run pytest --cov=src/instagram_analyzer --cov-report=html:output/coverage_html

# Validación CI
PYTHONPATH=src poetry run pytest tests/test_ci_validation.py -v
```

### **📦 Dependency Management**

1. **Poetry** para gestión de dependencias
2. **pyproject.toml** como fuente de verdad
3. **Lock file** siempre actualizado
4. **Dev dependencies** separadas de producción

### **🔧 Development Tools**

```bash
# Setup desarrollo
make setup-dev

# Quality checks
make quality

# Tests con coverage
make test-cov

# Limpieza
make clean
```

---

## 🚨 **REGLAS OBLIGATORIAS**

### **❌ PROHIBIDO:**

- Crear archivos en el directorio raíz (excepto configuración)
- Mover archivos fuera de la estructura organizada
- Ignorar el TODO.md para prioridades
- Usar imports relativos desde raíz
- Crear tests fuera de `tests/`

### **✅ OBLIGATORIO:**

- Seguir la estructura de `src/instagram_analyzer/`
- Consultar TODO.md antes de cualquier desarrollo
- Usar `PYTHONPATH=src` en comandos
- Tests para todo código nuevo
- Pre-commit hooks activos
- Documentación actualizada

---

## 🎯 **Workflow de Desarrollo**

### **Antes de Programar:**

1. **Revisar TODO.md** para prioridades actuales
2. **Verificar estructura** de directorios
3. **Activar entorno** de desarrollo
4. **Crear branch** desde develop/main

### **Durante el Desarrollo:**

1. **Código en `src/instagram_analyzer/`** únicamente
2. **Tests en `tests/`** correspondientes
3. **Seguir convenciones** de naming
4. **Commits pequeños** y descriptivos

### **Antes de Commit:**

1. **Ejecutar `make quality`** (lint, format, type-check)
2. **Ejecutar `make test-cov`** (tests + coverage)
3. **Verificar CI validation**
4. **Actualizar documentación** si es necesario

### **Pull Request:**

1. **Descripción clara** del cambio
2. **Referencias al TODO.md**
3. **Tests passing**
4. **Coverage mantenida** o mejorada

---

## 📊 **Métricas de Calidad**

### **Objetivos Actuales:**

- **Coverage**: >80% (actualmente 26.87%)
- **Tests**: Todos passing
- **Linting**: Sin errores
- **Type checking**: Sin errores mypy
- **Security**: Sin vulnerabilidades

### **Herramientas Integradas:**

- **Black**: Formatting automático
- **isort**: Import organization
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **pytest**: Testing framework
- **coverage**: Code coverage

---

## 🚀 **Comandos Esenciales**

```bash
# Desarrollo diario
make dev                    # Setup environment
make check                  # Pre-commit checks
make t                      # Run tests
make tc                     # Tests with coverage

# Quality assurance
make quality               # All quality checks
make ci-test              # Simulate CI pipeline

# Información del proyecto
make info                 # Environment info
make help                 # Ver todos los comandos
```

---

**🎯 RECUERDA: Este documento y el TODO.md son la guía maestra para todo el desarrollo. SIEMPRE consultarlos antes de hacer cambios.**
