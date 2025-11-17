#!/usr/bin/env python3
"""
Entry point for File Search MCP Server

Usage:
    python mcp_server.py              # Run in stdio mode (default)
    python mcp_server.py --help       # Show help
"""

if __name__ == "__main__":
    from app.mcp.server import mcp
    mcp.run()
