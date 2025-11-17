# Configuration Examples

This directory contains example configuration files for integrating File Search with various LLM agents.

## Files

### MCP Server Configurations

- **gemini-cli-settings.json** - Configuration for Gemini CLI
  - Location: Usually `~/.config/gemini-cli/settings.json` or as specified in Gemini CLI docs
  - Update the path `/absolute/path/to/filesearch-gemini` to your actual project path

- **claude-code-mcp.json** - Configuration for Claude Code
  - Location: `~/.config/claude-code/mcp_servers.json`
  - Or use `claude mcp add` command (see MCP_INTEGRATION.md)

- **codex-mcp-config.json** - Configuration for Codex CLI
  - Location: Varies by Codex version, check Codex documentation
  - Or use `codex mcp-server add` command

### CLI Configuration

- **cli-config.yaml** - Configuration for the filesearch-gemini CLI tool
  - Location: `~/.filesearch-gemini/config.yaml`
  - Create this file manually or use `filesearch-gemini config set-backend` command

## Usage

1. Choose the configuration file for your LLM agent
2. Copy the file to the appropriate location
3. Update any paths to match your system
4. Restart your LLM agent or reload the configuration
5. Test the integration with a simple command

For detailed instructions, see [MCP_INTEGRATION.md](../MCP_INTEGRATION.md).
