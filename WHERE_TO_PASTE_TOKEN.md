# Where to Paste Your Developer Token

## ⚠️ Important: Don't paste it in project files!

Your developer token should **NOT** be stored in any project files. It goes in your **MCP client configuration file** (Cursor, Claude Desktop, etc.).

## For Cursor (Windows)

### Step 1: Find Your Cursor MCP Config File

The config file is located at:
```
%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

**Full path example:**
```
C:\Users\YourName\AppData\Roaming\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

### Step 2: Open the Config File

1. Press `Win + R` to open Run dialog
2. Type: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings`
3. Open `cline_mcp_settings.json` (create it if it doesn't exist)

### Step 3: Add Your Configuration

Paste your developer token in the `GOOGLE_ADS_DEVELOPER_TOKEN` field:

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "command": "python",
      "args": [
        "-m",
        "ads_mcp.server"
      ],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "PASTE_YOUR_TOKEN_HERE",
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\YourName\\AppData\\Roaming\\gcloud\\application_default_credentials.json",
        "GOOGLE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

**Replace:**
- `PASTE_YOUR_TOKEN_HERE` → Your actual developer token
- `C:\\Users\\YourName\\...` → Your credentials file path (from `gcloud auth application-default login`)
- `your-project-id` → Your Google Cloud project ID

### Step 4: Save and Restart Cursor

After saving the file, restart Cursor for the changes to take effect.

## For Claude Desktop (Windows)

Edit this file:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Use the same JSON structure as above.

## Quick Test

After configuring, you can test if the token is being read correctly by running:

```bash
python setup_check.py
```

This will verify that the environment variable is set (when running through your MCP client).

## Alternative: Set as System Environment Variable (Not Recommended)

If you want to test the server directly (not through MCP), you can temporarily set it as a system environment variable:

**Windows PowerShell:**
```powershell
$env:GOOGLE_ADS_DEVELOPER_TOKEN = "your-token-here"
```

**Windows Command Prompt:**
```cmd
set GOOGLE_ADS_DEVELOPER_TOKEN=your-token-here
```

But for production use with MCP, always use the MCP client configuration file!

