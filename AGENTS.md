# 🤖 AI Coding Agent Instructions

> **COMPLIANCE CONFIRMED:** Priorizaré la reutilización del código existente antes de proponer creación de nuevos artefactos.

---

## 1. Proceso Obligatorio de Cumplimiento

1. **Contextualizar**
   - Leer y entender los **requisitos de la tarea** antes de interactuar.
   - Revisar la **estructura del repositorio** y los **archivos pertinentes**.

2. **Planificar**
   - Identificar dónde **extender** o **refactorizar** código existente.
   - Si es estrictamente necesario un nuevo archivo, justificar por qué **no es viable** extender módulos actuales.
   - Definir puntos de integración (clases, funciones, rutas de archivos).

3. **Implementar y Validar**
   - Proponer cambios concretos con **referencia a rutas y nombres de archivos**.
   - Incluir **checkpoints de validación** automáticos y/o manuales:
     - Linting: Black / Isort / Flake8
     - Tipado: Mypy
     - Pruebas: Pytest (cobertura mínima del 80%)
   - Finalizar siempre con: **COMPLIANCE CONFIRMED**

---

## 2. Reglas Fundamentales (Cualquier violación invalida la respuesta)

- ❌ **No** crear archivos nuevos sin un análisis exhaustivo de reutilización.
- ❌ **No** reescribir código cuando sea posible **refactorizar**.
- ❌ **No** dar consejos genéricos: siempre incluir **implementaciones específicas**.
- ❌ **No** ignorar la **arquitectura** y la **convención de rutas** del proyecto.

- ✅ Extender servicios y componentes existentes.
- ✅ Consolidar código duplicado.
- ✅ Referenciar **rutas exactas** de los archivos modificados.
- ✅ Proporcionar estrategias de migración cuando se cambien APIs o módulos.

> **Excepción Justificada**
> Solo se permite crear un nuevo archivo si:
> 1. Romper la cohesión de un módulo existente.
> 2. Se documenta claramente el **motivo** y la **estrategia de migración**.

---

## 3. Pasos Secuenciales (Obligatorio)

1. 📋 **Leer requisitos**
   - Confirmar comprensión de la tarea y las reglas de este documento.

2. 🔍 **Analizar código**
   - Ubicar los archivos y funciones relevantes.
   - Identificar duplicados o puntos de extensión.

3. 📝 **Plan de implementación**
   - Detallar el **alcance** de los cambios.
   - Enumerar las **rutas de los archivos** y las **funciones/clases** a modificar.

4. 🔧 **Detalles técnicos**
   - Mostrar fragmentos de código antes/después con rutas exactas.
   - Incluir comandos de prueba y **checkpoints de validación**.

5. ✅ **Verificación y cierre**
   - Confirmar que pasan **linting**, **tipado** y **tests**.
   - Finalizar con **COMPLIANCE CONFIRMED**.

---

> **NOTA:** Todo lo relativo a **comandos de instalación**, **entorno de desarrollo** y **arquitectura detallada** debería permanecer en el `README.md` o en la documentación interna del repositorio, no en este `agents.md`.
