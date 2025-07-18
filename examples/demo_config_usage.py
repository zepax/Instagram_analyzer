"""Demo: Uso general del sistema de configuración centralizada.

Este script muestra cómo cargar la configuración, validar, actualizar en tiempo de ejecución y usar variables de entorno para override.
"""

import os

from instagram_analyzer.config.config_loader import ConfigLoader


def main():
    # Cargar configuración inicial
    config = ConfigLoader.get_config()
    print("Configuración inicial:")
    print(config)

    # Validar configuración
    try:
        ConfigLoader.validate_config()
        print("Validación exitosa.")
    except Exception as e:
        print(f"Error de validación: {e}")

    # Override con variable de entorno
    os.environ["IGAN_APP_DEBUG"] = "true"
    ConfigLoader.reload_config()
    print("\nConfiguración tras override por variable de entorno IGAN_APP_DEBUG=true:")
    print(ConfigLoader.get_config())

    # Actualización en tiempo de ejecución
    ConfigLoader.update_config({"app": {"version": "0.2.99-demo"}})
    print("\nConfiguración tras update_config en runtime:")
    print(ConfigLoader.get_config())


if __name__ == "__main__":
    main()
