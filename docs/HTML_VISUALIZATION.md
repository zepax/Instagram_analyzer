# HTML Visualization with VS Code Extensions

Este documento explica cómo visualizar los reportes HTML generados por Instagram Analyzer usando las extensiones de Microsoft Edge y Live Server directamente en VS Code.

## 🎯 Overview

El entorno de desarrollo incluye estas extensiones de VS Code:
- **Microsoft Edge Tools** (`ms-edgedevtools.vscode-edge-devtools`): Integración con Edge DevTools
- **Live Server** (`ms-vscode.live-server`): Servidor local para archivos HTML con auto-refresh
- **Configuración automática**: Tasks y settings pre-configurados para visualización HTML

## 🚀 Quick Start

### 1. Generar Análisis

```bash
# Generar análisis de Instagram
poetry run python examples/analisis_personalizado.py
```

### 2. Visualizar con Live Server (Método Recomendado)

1. **En VS Code Explorer**: Navegar al archivo HTML generado (ej: `output/instagram_analysis.html`)
2. **Click derecho** en el archivo HTML
3. **Seleccionar** "Open with Live Server"
4. **Visualizar** en la pestaña integrada de VS Code en `http://localhost:5500`

### 3. Visualizar con Edge DevTools

1. **Abrir archivo** HTML en VS Code
2. **Comando Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. **Buscar** "Microsoft Edge Tools: Open Source in Microsoft Edge"
4. **Visualizar** en el panel de Edge DevTools

## 🛠️ Comandos Disponibles

### Comandos Bash

```bash
# Ver análisis automáticamente (busca y selecciona archivos)
view-html

# Ver análisis específico por directorio
view-analysis output

# Generar y visualizar en un comando
analyze-and-view

# Configurar VS Code tasks
setup-html
```

### VS Code Tasks

Acceder via `Ctrl+Shift+P` → "Tasks: Run Task":

- **View Latest Analysis**: Busca y abre el análisis más reciente
- **Generate and View Analysis**: Ejecuta análisis completo
- **Setup HTML Viewing**: Configura tasks y settings

## 📁 Directorios de Análisis

Búsqueda automática en estos directorios:

- `output/` - Directorio principal de salida
- `final_analysis/` - Análisis finales
- `debug_analysis*/` - Directorios de debug
- `mi_analisis_personalizado/` - Análisis personalizados
- `test_output/` - Salida de pruebas

## 🔧 Configuración

### Extensiones Auto-instaladas

```json
{
  "ms-edgedevtools.vscode-edge-devtools": "Microsoft Edge Tools",
  "ms-vscode.live-server": "Live Server"
}
```

### Settings Configurados

```json
{
  "liveServer.settings.port": 5500,
  "liveServer.settings.donotShowInfoMsg": true,
  "vscode-edge-devtools.mirrorEdits": true
}
```

### Puerto Configurado

- **5500**: Live Server (reenvío automático en VS Code)

## 📋 Workflows

### Workflow Básico

1. **Generar**:
   ```bash
   poetry run python examples/analisis_personalizado.py
   ```

2. **Visualizar**:
   - Click derecho en `output/instagram_analysis.html`
   - "Open with Live Server"

3. **Desarrollar**:
   - Cambios en HTML se reflejan automáticamente
   - Live reload habilitado

### Workflow Avanzado (Con Edge DevTools)

1. **Generar análisis**
2. **Abrir archivo** en VS Code editor
3. **Edge DevTools** (`Ctrl+Shift+P` → "Microsoft Edge Tools")
4. **Debug HTML/CSS/JS** en panel integrado

### Workflow de Desarrollo

```bash
# Terminal integrado de VS Code
cd /workspaces/Instagram_analyzer

# Desarrollo iterativo
analyze-and-view  # Genera y abre automáticamente

# Editar archivos HTML si necesario
# Live Server refresca automáticamente
```

## 🐛 Troubleshooting

### Live Server No Inicia

```bash
# Verificar puerto
netstat -tulnp | grep 5500

# Reiniciar Live Server
# Ctrl+Shift+P → "Live Server: Stop Live Server"
# Ctrl+Shift+P → "Live Server: Open with Live Server"
```

### Extensiones No Disponibles

```bash
# Verificar extensiones instaladas
code --list-extensions | grep -E "(edge|live-server)"

# Reinstalar si necesario
code --install-extension ms-edgedevtools.vscode-edge-devtools
code --install-extension ms-vscode.live-server
```

### Archivos No Encontrados

```bash
# Buscar archivos HTML
view-html  # Busca automáticamente

# Verificar análisis generado
ls -la output/
ls -la */instagram_analysis.html
```

## 💡 Tips y Trucos

### 1. Acceso Rápido con Keyboard Shortcuts

- `Ctrl+Shift+P` → "Live Server" (acceso rápido)
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Generate and View Analysis"

### 2. Múltiples Análisis

```bash
# Ver menú de selección
view-html

# Comparar análisis
# Abrir múltiples en pestañas diferentes de Live Server
```

### 3. Desarrollo de Templates

- **Live reload**: Cambios en HTML se ven inmediatamente
- **Edge DevTools**: Debug completo de CSS/JavaScript
- **Console integrada**: Para debugging en tiempo real

### 4. Automatización con Tasks

```json
// En .vscode/tasks.json (ya configurado)
{
  "label": "Quick Analysis View",
  "type": "shell",
  "command": "poetry run python examples/analisis_personalizado.py && view-analysis"
}
```

## 🔗 Recursos

### VS Code Extensions

- [Microsoft Edge Tools](https://marketplace.visualstudio.com/items?itemName=ms-edgedevtools.vscode-edge-devtools)
- [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)

### Documentación

- [VS Code HTML Support](https://code.visualstudio.com/docs/languages/html)
- [Live Server Documentation](https://github.com/ritwickdey/vscode-live-server)

## 🎨 Ventajas del Approach con VS Code

✅ **Integrado**: Todo en VS Code, sin ventanas externas
✅ **Live Reload**: Cambios se ven instantáneamente
✅ **DevTools**: Debugging completo integrado
✅ **Sin Configuración**: Auto-setup en dev container
✅ **Performance**: Ligero comparado con navegador completo
✅ **Portable**: Funciona en cualquier entorno con VS Code

---

**¡Disfruta visualizando tus análisis de Instagram directamente en VS Code! 🎨📊**
