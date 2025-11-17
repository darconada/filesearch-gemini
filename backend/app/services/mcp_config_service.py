"""Servicio para gestionar configuración MCP y CLI"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.mcp_config import (
    MCPConfig, CLIConfig, MCPConfigUpdate, CLIConfigUpdate,
    MCPStatus, CLIStatus, IntegrationGuide
)

logger = logging.getLogger(__name__)

# Directorio para almacenar configuración
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)

MCP_CONFIG_FILE = CONFIG_DIR / "mcp_config.json"
CLI_CONFIG_FILE = CONFIG_DIR / "cli_config.json"


class MCPConfigService:
    """Servicio para gestionar configuración MCP y CLI"""

    def __init__(self):
        self._mcp_config: Optional[MCPConfig] = None
        self._cli_config: Optional[CLIConfig] = None
        self._load_configs()

    def _load_configs(self) -> None:
        """Cargar configuraciones desde archivos"""
        # Cargar MCP config
        if MCP_CONFIG_FILE.exists():
            try:
                with open(MCP_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self._mcp_config = MCPConfig(**data)
            except Exception as e:
                logger.warning(f"Error loading MCP config: {e}")
                self._mcp_config = MCPConfig()
        else:
            self._mcp_config = MCPConfig()

        # Cargar CLI config
        if CLI_CONFIG_FILE.exists():
            try:
                with open(CLI_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self._cli_config = CLIConfig(**data)
            except Exception as e:
                logger.warning(f"Error loading CLI config: {e}")
                self._cli_config = CLIConfig()
        else:
            self._cli_config = CLIConfig()

    def _save_mcp_config(self) -> None:
        """Guardar configuración MCP"""
        try:
            with open(MCP_CONFIG_FILE, 'w') as f:
                json.dump(self._mcp_config.model_dump(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving MCP config: {e}")
            raise

    def _save_cli_config(self) -> None:
        """Guardar configuración CLI"""
        try:
            with open(CLI_CONFIG_FILE, 'w') as f:
                json.dump(self._cli_config.model_dump(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving CLI config: {e}")
            raise

    # MCP Config methods
    def get_mcp_config(self) -> MCPConfig:
        """Obtener configuración MCP actual"""
        return self._mcp_config

    def update_mcp_config(self, update: MCPConfigUpdate) -> MCPConfig:
        """Actualizar configuración MCP"""
        if update.backend_url is not None:
            self._mcp_config.backend_url = update.backend_url
        if update.enabled is not None:
            self._mcp_config.enabled = update.enabled

        self._mcp_config.last_updated = datetime.now()
        self._save_mcp_config()

        logger.info(f"MCP config updated: {self._mcp_config}")
        return self._mcp_config

    def get_mcp_status(self) -> MCPStatus:
        """Obtener estado y ejemplos del servidor MCP"""
        # Obtener ruta absoluta del proyecto
        project_root = Path(__file__).parent.parent.parent.parent

        return MCPStatus(
            configured=self._mcp_config is not None,
            backend_url=self._mcp_config.backend_url,
            enabled=self._mcp_config.enabled,
            example_commands={
                "gemini_cli": {
                    "description": "Configuración para Gemini CLI",
                    "config": {
                        "mcpServers": {
                            "filesearch-gemini": {
                                "type": "stdio",
                                "command": "python",
                                "args": [f"{project_root}/backend/mcp_server.py"],
                                "env": {
                                    "FILESEARCH_BACKEND_URL": self._mcp_config.backend_url
                                }
                            }
                        }
                    }
                },
                "claude_code": {
                    "description": "Comando para Claude Code",
                    "command": f'claude mcp add filesearch-gemini --transport stdio --command "python" --args "backend/mcp_server.py"',
                    "config": {
                        "mcpServers": {
                            "filesearch-gemini": {
                                "command": "python",
                                "args": [f"{project_root}/backend/mcp_server.py"],
                                "env": {
                                    "FILESEARCH_BACKEND_URL": self._mcp_config.backend_url
                                }
                            }
                        }
                    }
                },
                "codex_cli": {
                    "description": "Comando para Codex CLI",
                    "command": f'codex mcp-server add filesearch-gemini --command "python" --args "{project_root}/backend/mcp_server.py"',
                    "config": {
                        "servers": {
                            "filesearch-gemini": {
                                "command": "python",
                                "args": [f"{project_root}/backend/mcp_server.py"],
                                "transport": "stdio",
                                "env": {
                                    "FILESEARCH_BACKEND_URL": self._mcp_config.backend_url
                                }
                            }
                        }
                    }
                }
            }
        )

    # CLI Config methods
    def get_cli_config(self) -> CLIConfig:
        """Obtener configuración CLI actual"""
        return self._cli_config

    def update_cli_config(self, update: CLIConfigUpdate) -> CLIConfig:
        """Actualizar configuración CLI"""
        if update.backend_url is not None:
            self._cli_config.backend_url = update.backend_url
        if update.default_store_id is not None:
            self._cli_config.default_store_id = update.default_store_id

        self._cli_config.last_updated = datetime.now()
        self._save_cli_config()

        logger.info(f"CLI config updated: {self._cli_config}")
        return self._cli_config

    def get_cli_status(self) -> CLIStatus:
        """Obtener estado y ejemplos del CLI"""
        project_root = Path(__file__).parent.parent.parent.parent
        cli_path = project_root / "filesearch-gemini"

        return CLIStatus(
            configured=self._cli_config is not None,
            backend_url=self._cli_config.backend_url,
            default_store_id=self._cli_config.default_store_id,
            executable_path=str(cli_path),
            example_commands=[
                f"{cli_path} config status",
                f"{cli_path} config set-backend {self._cli_config.backend_url}",
                f"{cli_path} stores list",
                f"{cli_path} docs upload --store-id STORE_ID --file /path/to/file.pdf",
                f'{cli_path} query --question "Your question?" --stores STORE_ID'
            ]
        )

    def get_integration_guide(self) -> IntegrationGuide:
        """Obtener guía completa de integración"""
        mcp_status = self.get_mcp_status()
        cli_status = self.get_cli_status()

        return IntegrationGuide(
            gemini_cli={
                "title": "Gemini CLI Integration",
                "description": "Configure Gemini CLI to use File Search via MCP",
                "steps": [
                    "1. Locate your Gemini CLI settings.json file",
                    "2. Add the filesearch-gemini MCP server configuration",
                    "3. Restart Gemini CLI",
                    "4. Use: 'Use filesearch-gemini to create a store...'"
                ],
                "config": mcp_status.example_commands["gemini_cli"]["config"],
                "documentation": "/MCP_INTEGRATION.md#integration-with-gemini-cli"
            },
            claude_code={
                "title": "Claude Code Integration",
                "description": "Configure Claude Code to use File Search via MCP",
                "steps": [
                    "1. Open your terminal in the project directory",
                    "2. Run the claude mcp add command below",
                    "3. Reload Claude Code MCP servers",
                    "4. Start using File Search tools in your conversations"
                ],
                "command": mcp_status.example_commands["claude_code"]["command"],
                "config": mcp_status.example_commands["claude_code"]["config"],
                "documentation": "/MCP_INTEGRATION.md#integration-with-claude-code"
            },
            codex_cli={
                "title": "Codex CLI Integration",
                "description": "Configure Codex CLI to use File Search via MCP",
                "steps": [
                    "1. Ensure Codex CLI is installed and configured",
                    "2. Run the codex mcp-server add command below",
                    "3. Verify with: codex mcp-server list",
                    "4. Start using File Search in Codex"
                ],
                "command": mcp_status.example_commands["codex_cli"]["command"],
                "config": mcp_status.example_commands["codex_cli"]["config"],
                "documentation": "/MCP_INTEGRATION.md#integration-with-codex-cli"
            },
            cli_local={
                "title": "Local CLI Usage",
                "description": "Use File Search directly from your terminal",
                "steps": [
                    "1. Make the CLI executable: chmod +x filesearch-gemini",
                    "2. Optionally add to PATH for global access",
                    "3. Configure with: ./filesearch-gemini config set-backend URL",
                    "4. Start using: ./filesearch-gemini --help"
                ],
                "executable": str(cli_status.executable_path),
                "examples": cli_status.example_commands,
                "documentation": "/MCP_INTEGRATION.md#method-2-cli-tool-integration"
            }
        )


# Instancia global del servicio
mcp_config_service = MCPConfigService()
