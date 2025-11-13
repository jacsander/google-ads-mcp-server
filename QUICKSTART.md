# Quick Start Guide

Get your Google Ads MCP server up and running in 5 minutes!

## 1. Install Dependencies

```bash
# Install the package
pip install -e .
```

## 2. Get Your Developer Token

1. Go to [Google Ads API Center](https://ads.google.com/aw/apicenter)
2. Apply for a developer token (or use your existing one)
3. Copy the token

## 3. Set Up Authentication

```bash
# Authenticate with Google Cloud
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
```

**Copy the credentials path** from the output (you'll need it next).

## 4. Configure Your MCP Client

### For Cursor

1. Open Cursor settings
2. Find MCP settings (usually in `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`)
3. Add the configuration from `mcp_config_example.json`
4. Replace the placeholder values:
   - `YOUR_DEVELOPER_TOKEN_HERE` → Your actual developer token
   - `C:\\Users\\YourName\\...` → The credentials path from step 3
   - `your-project-id` → Your Google Cloud project ID

### For Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

## 5. Verify Setup

Run the setup check script:

```bash
python setup_check.py
```

## 6. Test It!

Restart your MCP client and try:

```
What customers do I have access to?
```

## Need Help?

- See [SETUP_LOCAL.md](SETUP_LOCAL.md) for detailed instructions
- See [README.md](README.md) for more information about the server

