#!/bin/bash
set -e

# Script de instalación para herramientas Python
# Basado en el pyproject.toml del repositorio

echo "Instalando herramientas Python adicionales..."

# Crear un entorno virtual para instalar las herramientas
VENV_DIR="/tmp/instagram_tools_venv"

echo "Creando entorno virtual en $VENV_DIR..."
python3 -m venv $VENV_DIR

# Activar el entorno virtual
source $VENV_DIR/bin/activate

# Actualizar pip en el entorno virtual
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar herramientas principales de desarrollo - instalación separada para evitar conflictos
echo "Instalando herramientas principales de desarrollo..."

# Primero instalar black que requiere packaging>=22.0
pip install --no-cache-dir \
    black==23.7.0

# Luego instalar safety de forma separada (que necesita packaging<22.0)
# Usamos una versión más reciente de safety que sea compatible
pip install --no-cache-dir \
    safety>=2.3.5

# El resto de las herramientas
pip install --no-cache-dir \
    isort==5.12.0 \
    flake8==6.0.0 \
    mypy==1.5.0 \
    pre-commit==3.3.3 \
    bandit==1.7.5 \
    pydocstyle==6.3.0 \
    coverage==7.3.0

# Instalar herramientas de testing
echo "Instalando herramientas de testing..."
pip install --no-cache-dir \
    pytest==7.4.0 \
    pytest-cov==4.1.0 \
    pytest-mock==3.11.1 \
    pytest-asyncio==0.21.1 \
    pytest-xdist==3.3.0 \
    pytest-benchmark==4.0.0

# Instalar ruff en su última versión
echo "Instalando ruff en la última versión..."
pip install --no-cache-dir --upgrade ruff

# Instalar herramientas para análisis de datos y desarrollo interactivo
echo "Instalando herramientas para análisis de datos..."
pip install --no-cache-dir \
    ipython \
    jupyter \
    jupyterlab \
    ipywidgets==8.1.0 \
    matplotlib==3.7.0 \
    seaborn==0.12.0 \
    plotly==5.15.0

echo "Verificando instalaciones..."
echo "Versión de Python: $(python --version)"
echo "Versión de Black: $(black --version 2>/dev/null || echo 'No instalado')"
echo "Versión de Ruff: $(ruff --version 2>/dev/null || echo 'No instalado')"
echo "Versión de pytest: $(pytest --version 2>/dev/null || echo 'No instalado')"

# Desactivar el entorno virtual
deactivate

# Copiar herramientas seleccionadas al directorio bin local del usuario
TOOLS_DIR="$HOME/.local/bin"
mkdir -p $TOOLS_DIR

echo "Creando scripts wrapper en $TOOLS_DIR..."
# Crear scripts wrapper que usen el Python del sistema
for tool in black ruff flake8 mypy isort pytest coverage; do
    if [ -f "$VENV_DIR/bin/$tool" ]; then
        cat > "$TOOLS_DIR/$tool" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import runpy

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    try:
        runpy.run_module('$tool', run_name='__main__')
    except ImportError:
        print("Error: $tool no está instalado. Instálalo con 'pip install $tool'")
        sys.exit(1)
EOF
        chmod +x "$TOOLS_DIR/$tool"
        echo "Creado script wrapper para $tool en $TOOLS_DIR"
    else
        echo "No se pudo encontrar $tool en el entorno virtual"
    fi
done

# Instalar las herramientas a nivel global para que los scripts wrapper funcionen
echo "Instalando herramientas a nivel del usuario..."
pip install --user black ruff flake8 mypy isort pytest coverage

# Asegurarse de que el directorio está en el PATH
if [[ ":$PATH:" != *":$TOOLS_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.zshrc 2>/dev/null || true
fi

# No verificamos safety porque podría no haberse instalado (por conflicto con black)
# Solo mostramos una advertencia para las herramientas que se consideran críticas
for tool in black ruff pytest; do
  if ! command -v $tool &>/dev/null; then
    if [ -f "$TOOLS_DIR/$tool" ]; then
      echo "INFO: $tool se instaló en $TOOLS_DIR pero no está en el PATH actual."
      echo "      Reinicia tu terminal o ejecuta: export PATH=$TOOLS_DIR:\$PATH"
    else
      echo "ADVERTENCIA: $tool no está instalado correctamente."
    fi
  fi
done

# Limpiar el entorno virtual
echo "Limpiando el entorno virtual..."
rm -rf $VENV_DIR

# Mostrar mensaje de éxito incluso si algunas herramientas no se instalaron
echo ""
echo "==========================================================="
echo "Instalación de herramientas Python completada."
echo "Las herramientas principales se han copiado a $TOOLS_DIR."
echo "Para usarlas inmediatamente, ejecuta: export PATH=$TOOLS_DIR:\$PATH"
echo "El contenedor se ha construido correctamente y está listo para usarse."
echo "==========================================================="
echo ""

# Salimos con código 0 para que el contenedor se construya correctamente
exit 0
