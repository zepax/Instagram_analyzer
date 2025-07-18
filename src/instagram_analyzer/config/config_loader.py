"""Config loader for Instagram Analyzer.

- Loads settings from YAML file
- Supports environment variable overrides
- Allows runtime reload/update
- Validates configuration structure
"""

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.yaml"


class ConfigLoader:
    _config: dict[str, Any] = {}
    _config_path: Path = CONFIG_PATH

    @classmethod
    def load_config(cls) -> dict[str, Any]:
        """Load config from YAML and apply environment variable overrides."""
        if not cls._config_path.exists():
            raise FileNotFoundError(f"Config file not found: {cls._config_path}")
        with open(cls._config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        config = cls._apply_env_overrides(config)
        if not isinstance(config, dict):
            raise TypeError("Config file must contain a dictionary at the top level")
        cls._config = config
        return config

    @classmethod
    def get_config(cls) -> dict[str, Any]:
        """Get current config, loading if necessary."""
        if not cls._config:
            return cls.load_config()
        return cls._config

    @classmethod
    def reload_config(cls) -> dict[str, Any]:
        """Reload config from file and environment."""
        return cls.load_config()

    @classmethod
    def update_config(cls, updates: dict[str, Any]) -> None:
        """Update config at runtime (in-memory only)."""
        cls._config.update(updates)

    @staticmethod
    def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
        """Override config values with environment variables if present."""
        for section, values in config.items():
            if isinstance(values, dict):
                for key in values:
                    env_var = f"IGAN_{section.upper()}_{key.upper()}"
                    if env_var in os.environ:
                        values[key] = os.environ[env_var]
        return config

    @classmethod
    def validate_config(cls) -> None:
        """Basic validation of required config sections and types."""
        config = cls.get_config()
        required_sections = ["app", "cache", "export", "ml"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
        # Example: check types
        if not isinstance(config["app"].get("name"), str):
            raise TypeError("app.name must be a string")
        if not isinstance(config["cache"].get("memory_limit_mb"), int):
            raise TypeError("cache.memory_limit_mb must be an integer")


# Usage example:
# config = ConfigLoader.get_config()
# ConfigLoader.validate_config()
