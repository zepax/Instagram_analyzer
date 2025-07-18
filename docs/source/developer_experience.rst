.. _developer_experience:

========================
Developer Experience (DX)
========================

Esta sección documenta las mejores prácticas, herramientas y flujos de trabajo para contribuir y desarrollar en la plataforma Instagram Analyzer/Data Mining Platform.

.. contents:: Tabla de Contenidos
   :local:
   :depth: 2

Introducción
============

El objetivo es ofrecer una experiencia de desarrollo fluida, productiva y profesional, siguiendo estándares enterprise y facilitando la colaboración.

README Mejorado
===============

- Badges de estado: build, coverage, versión, seguridad.
- Ejemplos de uso CLI y API reales.
- Sección de instalación y primeros pasos ampliada.
- Enlaces directos a documentación, tutoriales y guías de contribución.

CONTRIBUTING.md
===============

- Guía detallada para contribuir: branching, PRs, code style, checklist de PR.
- Ejemplos de buenas prácticas y convenciones.
- Política de issues y soporte.

Docker Containerization
=======================

- Dockerfile optimizado para desarrollo y producción.
- Instrucciones de build y uso en README.
- Soporte para Poetry y entorno reproducible.

VS Code Dev Container
=====================

- `.devcontainer/` con configuración completa.
- Extensiones recomendadas y settings predefinidos.
- Script de setup automatizado.
- Documentación de uso en README y docs.

Flujo de Trabajo Recomendado
============================

1. Clona el repositorio y entra al directorio raíz.
2. Usa el contenedor de desarrollo VS Code o Docker para entorno reproducible.
3. Instala dependencias con Poetry: `poetry install && poetry shell`.
4. Ejecuta los tests y quality checks: `make quality`.
5. Sigue las guías de CONTRIBUTING.md para nuevas features o fixes.
6. Actualiza la documentación y el TODO.md tras cada contribución.

Herramientas y Extensiones
==========================

- Pre-commit hooks: black, isort, flake8, mypy, bandit, safety.
- VS Code: Python, Docker, Markdown All in One, GitLens, Live Server.
- Integración CI/CD: GitHub Actions para tests, lint y releases automáticos.

Preguntas Frecuentes (FAQ)
==========================

- ¿Cómo inicio el entorno de desarrollo? → Usa el dev container o Docker, luego `poetry install`.
- ¿Cómo ejecuto los tests? → `PYTHONPATH=src poetry run pytest`.
- ¿Cómo contribuyo? → Lee CONTRIBUTING.md y sigue el flujo de PR.
- ¿Dónde reporto bugs? → Abre un issue en GitHub siguiendo la plantilla.

Para más detalles, consulta el README y la documentación técnica.
