# .devcontainer/Dockerfile
# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Argumentos de build
ARG VARIANT="3.11"
ARG NODE_VERSION="18"

# Variables de entorno para Poetry y desarrollo
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VENV_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    NODE_OPTIONS="--dns-result-order=ipv4first" \
    ANTHROPIC_REQUEST_TIMEOUT=120000 \
    ANTHROPIC_RETRY_ATTEMPTS=5

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    # Herramientas básicas
    git \
    curl \
    wget \
    unzip \
    # Compilación
    build-essential \
    software-properties-common \
    # Sistema
    sudo \
    zsh \
    # Certificados
    gnupg \
    lsb-release \
    ca-certificates \
    # Base de datos
    sqlite3 \
    sqlite3-doc \
    libsqlite3-dev \
    # Análisis de datos
    jq \
    tree \
    htop \
    # Limpieza
    && rm -rf /var/lib/apt/lists/*

# Copiar script de instalación de herramientas Python
COPY .devcontainer/install-python-tools.sh /tmp/
RUN chmod +x /tmp/install-python-tools.sh && \
    /tmp/install-python-tools.sh && \
    rm /tmp/install-python-tools.sh

# Instalar Node.js (para Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario vscode con privilegios sudo
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /home/vscode/.vscode-server /home/vscode/.vscode-server-insiders \
    && chown -R vscode:vscode /home/vscode

# Instalar Poetry directamente con sus dependencias
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir poetry==$POETRY_VERSION

# Configurar Poetry
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project false \
    && poetry config cache-dir /tmp/poetry_cache \
    && poetry config virtualenvs.path /opt/poetry/venv

# Instalar Claude Code globalmente (antes de cambiar a usuario vscode)
RUN npm install -g @anthropic-ai/claude-code

# Configurar directorio de trabajo
WORKDIR /workspaces/Instagram_analyzer

# Copiar archivos de Poetry
COPY pyproject.toml poetry.lock* ./

# Regenerar lock file si es necesario e instalar dependencias
RUN if [ ! -f poetry.lock ]; then poetry lock; fi \
    && poetry install --with=dev --no-root \
    && rm -rf /tmp/poetry_cache

# Actualizar Ruff a la última versión compatible con VSCode
RUN poetry run pip install --upgrade ruff

# Cambiar ownership del workspace
RUN chown -R vscode:vscode /workspaces

# Cambiar a usuario vscode
USER vscode

# Instalar oh-my-zsh para mejor experiencia de terminal
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" || true

# Configurar git para el container
RUN git config --global --add safe.directory /workspaces/Instagram_analyzer

# Crear directorios necesarios
RUN mkdir -p /home/vscode/.claude \
    && mkdir -p /workspaces/Instagram_analyzer/{scripts/tools,src,tests,docs}

# Verificar instalaciones básicas
RUN echo "=== Verificando instalaciones ===" \
    && python --version \
    && node --version \
    && npm --version \
    && sqlite3 --version \
    && echo "=== Instalaciones básicas exitosas ==="

SHELL ["/bin/bash", "-c"]

# Comando por defecto
CMD ["/bin/bash"]


# Asegurar que los binarios de usuario estén en el PATH
ENV PATH="/home/vscode/.local/bin:${PATH}"
