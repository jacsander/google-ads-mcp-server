# Setting Up Google Ads MCP Server with Copilot

This guide will help you configure the Google Ads MCP server to work with Microsoft Copilot.

## ✅ Project Folder Status

Your project folder is **ready**! All necessary files are in place:
- ✅ Python packages installed (`google-ads`, `mcp`)
- ✅ Server code ready
- ✅ Setup scripts and documentation created

## 📋 Pre-Copilot Checklist

Before connecting to Copilot, you need to complete these steps:

### 1. ✅ Google Ads Developer Token
- [ ] You have your developer token (you mentioned you have it!)
- [ ] You know where to paste it (in Copilot's MCP config - see below)

### 2. ⚠️ Google Cloud Authentication (REQUIRED)
You need to set up authentication before the server can run:

```bash
# Install gcloud CLI if you haven't:
# Download from: https://cloud.google.com/sdk/docs/install

# Then authenticate:
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
```

**Important:** After running this command, copy the credentials file path from the output!

### 3. ⚠️ Enable Google Ads API (REQUIRED)
- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Select your project
- [ ] Enable the [Google Ads API](https://console.cloud.google.com/apis/library/googleads.googleapis.com)

### 4. ⚠️ Get Your Google Cloud Project ID
- [ ] Note your Google Cloud Project ID (you'll need it for the config)

## 🔧 Copilot MCP Configuration

Microsoft Copilot uses MCP configuration files. The location depends on your setup:

### Option 1: Copilot Desktop/App

If you're using Copilot as a desktop application, the config file is typically at:

**Windows:**
```
%APPDATA%\Microsoft\Copilot\mcp_settings.json
```
or
```
%LOCALAPPDATA%\Microsoft\Copilot\mcp_settings.json
```

### Option 2: VS Code Copilot Extension

If using VS Code with Copilot, check:
```
%APPDATA%\Code\User\globalStorage\mcp_settings.json
```

### Option 3: Check Copilot Documentation

The exact location may vary. Check:
- Copilot settings/preferences
- Look for "MCP" or "Model Context Protocol" settings
- Check Copilot's documentation for MCP server configuration

### Configuration Format

Once you find the config file, add this configuration:

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
        "GOOGLE_ADS_DEVELOPER_TOKEN": "YOUR_DEVELOPER_TOKEN_HERE",
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\jsander\\AppData\\Roaming\\gcloud\\application_default_credentials.json",
        "GOOGLE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

**Replace:**
- `YOUR_DEVELOPER_TOKEN_HERE` → Your actual developer token
- `C:\\Users\\jsander\\...` → Your actual credentials path (from step 2)
- `your-project-id` → Your Google Cloud project ID

### Alternative: Using Installed Command

If you've installed the package with `pip install -e .`, you can use:

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "command": "google-ads-mcp"
    },
    "env": {
      "GOOGLE_ADS_DEVELOPER_TOKEN": "YOUR_DEVELOPER_TOKEN_HERE",
      "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\jsander\\AppData\\Roaming\\gcloud\\application_default_credentials.json",
      "GOOGLE_PROJECT_ID": "your-project-id"
    }
  }
}
```

## 🧪 Test Before Connecting to Copilot

Test the server directly to make sure everything works:

```bash
# Set environment variables temporarily (Windows PowerShell)
$env:GOOGLE_ADS_DEVELOPER_TOKEN = "your-token-here"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\jsander\AppData\Roaming\gcloud\application_default_credentials.json"
$env:GOOGLE_PROJECT_ID = "your-project-id"

# Test the server
python -m ads_mcp.server
```

If it starts without errors, you're ready to connect to Copilot!

## 🚀 After Configuration

1. **Restart Copilot** completely
2. **Verify connection** - Copilot should show the MCP server is connected
3. **Test with a query** like:
   - "What customers do I have access to?"
   - "List my Google Ads accounts"

## ❓ Finding Copilot's Config Location

If you can't find the config file:

1. **Check Copilot Settings:**
   - Look for "MCP", "Model Context Protocol", or "Servers" in settings
   - There may be a UI to add MCP servers

2. **Search for config files:**
   ```powershell
   # Search for MCP config files
   Get-ChildItem -Path $env:APPDATA -Recurse -Filter "*mcp*.json" -ErrorAction SilentlyContinue
   Get-ChildItem -Path $env:LOCALAPPDATA -Recurse -Filter "*mcp*.json" -ErrorAction SilentlyContinue
   ```

3. **Check Copilot Documentation:**
   - Microsoft's Copilot documentation
   - MCP integration guides

## 🆘 Troubleshooting

### "Module not found" errors
- Make sure you've run: `pip install -e .`
- Verify Python path in Copilot config matches your Python installation

### "Credentials not found" errors
- Verify the `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Make sure you've run `gcloud auth application-default login`

### "Developer token not set" errors
- Double-check the token is in the `env` section of your config
- Verify there are no extra quotes or spaces

## 📚 Additional Resources

- [SETUP_LOCAL.md](SETUP_LOCAL.md) - Detailed setup guide
- [WHERE_TO_PASTE_TOKEN.md](WHERE_TO_PASTE_TOKEN.md) - Token configuration details
- [QUICKSTART.md](QUICKSTART.md) - Quick reference

