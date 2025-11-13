#!/usr/bin/env python
"""
Helper script to find your MCP client configuration file location.
"""

import os
from pathlib import Path


def find_cursor_config():
    """Find Cursor MCP configuration file."""
    appdata = os.getenv("APPDATA")
    if not appdata:
        return None
    
    config_path = Path(appdata) / "Cursor" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
    return config_path


def find_claude_desktop_config():
    """Find Claude Desktop MCP configuration file."""
    appdata = os.getenv("APPDATA")
    if not appdata:
        return None
    
    config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    return config_path


def main():
    print("=" * 70)
    print("MCP Client Configuration File Locations")
    print("=" * 70)
    print()
    
    # Cursor
    cursor_config = find_cursor_config()
    if cursor_config:
        exists = "✓ EXISTS" if cursor_config.exists() else "✗ NOT FOUND (will be created)"
        print(f"Cursor MCP Config: {cursor_config}")
        print(f"  Status: {exists}")
        print()
    else:
        print("Cursor: Could not determine path (APPDATA not set)")
        print()
    
    # Claude Desktop
    claude_config = find_claude_desktop_config()
    if claude_config:
        exists = "✓ EXISTS" if claude_config.exists() else "✗ NOT FOUND (will be created)"
        print(f"Claude Desktop Config: {claude_config}")
        print(f"  Status: {exists}")
        print()
    else:
        print("Claude Desktop: Could not determine path (APPDATA not set)")
        print()
    
    print("=" * 70)
    print()
    print("To add your developer token:")
    print("1. Open the config file above (create it if it doesn't exist)")
    print("2. Add the configuration from 'mcp_config_example.json'")
    print("3. Replace 'YOUR_DEVELOPER_TOKEN_HERE' with your actual token")
    print("4. Save and restart your MCP client")
    print()
    print("See 'WHERE_TO_PASTE_TOKEN.md' for detailed instructions.")


if __name__ == "__main__":
    main()

