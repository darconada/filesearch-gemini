"""Configuration management for File Search CLI"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class CLIConfig:
    """Manage CLI configuration from env vars and config file"""

    def __init__(self):
        self.config_dir = Path.home() / ".filesearch-gemini"
        self.config_file = self.config_dir / "config.yaml"
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file if exists"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                self._config = {}

    def save_config(self) -> None:
        """Save current configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    @property
    def backend_url(self) -> str:
        """Get backend URL from env or config"""
        return os.getenv(
            "FILESEARCH_BACKEND_URL",
            self._config.get("backend_url", "http://localhost:8000")
        )

    @backend_url.setter
    def backend_url(self, value: str) -> None:
        """Set backend URL in config"""
        self._config["backend_url"] = value
        self.save_config()

    @property
    def api_key(self) -> Optional[str]:
        """Get API key from env or config"""
        return os.getenv(
            "GOOGLE_API_KEY",
            self._config.get("api_key")
        )

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set API key in config"""
        self._config["api_key"] = value
        self.save_config()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a config value"""
        self._config[key] = value
        self.save_config()


# Global config instance
config = CLIConfig()
