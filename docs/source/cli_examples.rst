==========================
Ejemplos de Uso CLI
==========================

Análisis Básico de Export de Instagram
--------------------------------------

.. code-block:: bash

    poetry run instagram-analyzer analyze /ruta/al/export --format html --anonymize

- Analiza un export de Instagram y genera un reporte HTML anonimizado.

Exportar en Diferentes Formatos
-------------------------------

.. code-block:: bash

    poetry run instagram-analyzer analyze /ruta/al/export --format pdf

    poetry run instagram-analyzer analyze /ruta/al/export --format json

- Exporta el análisis en PDF o JSON.

Mostrar Información Básica del Export
-------------------------------------

.. code-block:: bash

    poetry run instagram-analyzer info /ruta/al/export

- Muestra información resumida del export (posts, stories, reels, perfil, etc).

Validar Estructura de Export
----------------------------

.. code-block:: bash

    poetry run instagram-analyzer validate /ruta/al/export

- Valida que la estructura del export de Instagram sea correcta y compatible.

Análisis Avanzado con Opciones
------------------------------

.. code-block:: bash

    poetry run instagram-analyzer analyze /ruta/al/export --format html --show-progress --no-cache

- Muestra barra de progreso, fuerza análisis sin cache y exporta a HTML.

Exportar Reporte con Branding Personalizado
-------------------------------------------

.. code-block:: bash

    poetry run instagram-analyzer analyze /ruta/al/export --format html --brand "MiEmpresa" --logo /ruta/logo.png

- Añade branding y logo personalizado al reporte HTML.

Análisis Paralelo (datasets grandes)
------------------------------------

.. code-block:: bash

    poetry run instagram-analyzer analyze /ruta/al/export --format html --parallel

- Usa procesamiento paralelo para acelerar el análisis de grandes volúmenes de datos.

Ayuda y Listado de Comandos
---------------------------

.. code-block:: bash

    poetry run instagram-analyzer --help

    poetry run instagram-analyzer analyze --help

- Muestra ayuda detallada y todas las opciones disponibles.
