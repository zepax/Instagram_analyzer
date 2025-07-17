#!/bin/bash
set -e

echo "🚀 Configurando entorno de desarrollo Instagram Data Analyzer..."

# Asegurarse que pip está actualizado
echo "🔧 Actualizando pip y herramientas base..."
python -m pip install --upgrade pip

# Instalar y configurar Poetry
echo "📦 Instalando y configurando Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
poetry config virtualenvs.in-project true

# Verificar que estamos en el directorio correcto
cd /workspaces/Instagram_analyzer

# Verificar y configurar Poetry
if [ -f "pyproject.toml" ]; then
    echo "📦 Verificando dependencias de Poetry..."

    # Verificar si poetry.lock está sincronizado
    if ! poetry check; then
        echo "⚠️  Lock file desactualizado, regenerando..."
        poetry lock --no-update
    fi

    # Instalar dependencias del proyecto
    echo "📥 Instalando dependencias del proyecto..."
    poetry install

    # Actualizar herramientas de desarrollo
    echo "🔄 Actualizando herramientas de desarrollo..."
    poetry run pip install --upgrade \
        ruff>=0.5.3 \
        black>=23.0.0 \
        isort>=5.12.0 \
        mypy>=1.0.0 \
        pytest>=7.0.0 \
        pytest-cov>=4.0.0 \
        pre-commit>=3.0.0 \
        jupyterlab>=4.0.0 \
        ipykernel>=6.0.0

    # Configurar pre-commit
    echo "🔧 Configurando pre-commit..."
    poetry run pre-commit install

    # Verificar entorno virtual
    poetry env info

    echo "✅ Poetry configurado correctamente"
else
    echo "⚠️  pyproject.toml no encontrado, creando proyecto básico..."
    poetry init --no-interaction \
        --name instagram-data-analyzer \
        --version 0.2.1 \
        --description "Instagram Data Mining & Analysis Platform"
fi

# Mostrar versiones instaladas
echo "📦 Versiones instaladas:"
poetry run ruff --version
poetry run black --version
poetry run isort --version
poetry run mypy --version
poetry run pytest --version
poetry run pre-commit --version

# Crear estructura de proyecto si no existe
echo "📁 Creando estructura del proyecto..."
mkdir -p {src/instagram_analyzer,tests,docs,scripts/tools,examples,data}

# Crear __init__.py files
touch src/instagram_analyzer/__init__.py
touch tests/__init__.py

# Crear herramientas personalizadas
echo "🔧 Configurando herramientas personalizadas..."

# Herramienta de análisis de base de datos
cat > scripts/tools/db_analyzer.py << 'EOF'
#!/usr/bin/env python3
"""Herramienta para analizar bases de datos SQLite de Instagram"""
import sqlite3
import json
import sys
from pathlib import Path

def analyze_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        analysis = {"database": str(db_path), "tables": {}}

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]

            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()

            analysis["tables"][table] = {
                "row_count": count,
                "columns": [{"name": col[1], "type": col[2]} for col in columns]
            }

        conn.close()
        return analysis
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: db_analyzer.py <database.sqlite>")
        sys.exit(1)

    result = analyze_db(sys.argv[1])
    print(json.dumps(result, indent=2))
EOF

chmod +x scripts/tools/db_analyzer.py

# Crear archivo CLAUDE.md para contexto
if [ ! -f "CLAUDE.md" ]; then
    echo "📝 Creando archivo de contexto para Claude Code..."
    cat > CLAUDE.md << 'EOF'
# Instagram Data Mining & Analysis Platform

## Herramientas Disponibles
- **Python con Poetry**: Entorno completo de desarrollo
- **SQLite**: Análisis de bases de datos
- **Claude Code**: Asistencia de IA para desarrollo
- **Jupyter**: Análisis interactivo

## Comandos Útiles
```bash
# Activar entorno Poetry
poetry shell

# Analizar base de datos SQLite
python scripts/tools/db_analyzer.py data/instagram.db

# Iniciar Jupyter Lab
jupyter lab --ip=0.0.0.0 --port=8888 --allow-root

# Ejecutar tests
poetry run pytest

# Formatear código
poetry run black .
poetry run ruff check .
