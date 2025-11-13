# Local Setup Guide for Google Ads MCP Server

This guide will help you set up the Google Ads MCP server from a local clone.

## Prerequisites

1. **Python 3.10 or higher**
   - Check your version: `python --version` or `python3 --version`
   - Download from [python.org](https://www.python.org/downloads/) if needed

2. **pipx** (recommended for MCP servers)
   - Install: `pip install pipx` or `python -m pip install pipx`
   - Verify: `pipx --version`

3. **Google Cloud SDK (gcloud)** (for authentication)
   - Install from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install)
   - Verify: `gcloud --version`

## Step 1: Install the Package

You have two options:

### Option A: Install with pipx (Recommended for MCP)

```bash
# From the project root directory
pipx install -e .
```

### Option B: Install with pip (for development)

```bash
# From the project root directory
pip install -e .
```

## Step 2: Configure Google Ads Developer Token

1. Follow the instructions for [Obtaining a Developer Token](https://developers.google.com/google-ads/api/docs/get-started/dev-token)
2. Record your developer token - you'll need it in Step 4

## Step 3: Enable Google Ads API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Enable the [Google Ads API](https://console.cloud.google.com/apis/library/googleads.googleapis.com)

## Step 4: Configure Credentials

### Using Application Default Credentials (Recommended)

1. **Set up OAuth Client** (if you haven't already):
   - Go to [Google Cloud Console > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
   - Create an OAuth 2.0 Client ID (Desktop app or Web application)
   - Download the JSON file

2. **Authenticate with gcloud**:
   ```bash
   gcloud auth application-default login \
     --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform \
     --client-id-file=path/to/your/client-credentials.json
   ```

3. **Copy the credentials path** from the output:
   ```
   Credentials saved to file: [PATH_TO_CREDENTIALS_JSON]
   ```

### Alternative: Using google-ads.yaml

If you already have a working `google-ads.yaml` file from the Google Ads API Python client library:

1. Place it in your home directory or a known location
2. Modify `ads_mcp/utils.py` line 66 to use:
   ```python
   client = GoogleAdsClient.load_from_storage()
   ```

## Step 5: Set Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Or manually create .env with:
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_APPLICATION_CREDENTIALS=path\to\your\credentials.json
GOOGLE_PROJECT_ID=your-project-id
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890  # Optional, uncomment if needed
```

**Note:** The `.env` file is for reference. You'll need to set these as environment variables or in your MCP client configuration.

## Step 6: Configure Your MCP Client

### For Cursor/Claude Desktop

Create or edit the MCP settings file:

**Windows:** `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**macOS:** `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Linux:** `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

Add the following configuration:

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
        "GOOGLE_ADS_DEVELOPER_TOKEN": "your_developer_token_here",
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\YourName\\AppData\\Roaming\\gcloud\\application_default_credentials.json",
        "GOOGLE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

**For local development with pip install -e:**

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "command": "google-ads-mcp"
    },
    "env": {
      "GOOGLE_ADS_DEVELOPER_TOKEN": "your_developer_token_here",
      "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\YourName\\AppData\\Roaming\\gcloud\\application_default_credentials.json",
      "GOOGLE_PROJECT_ID": "your-project-id"
    }
  }
}
```

### For Gemini CLI/Code Assist

Edit `~/.gemini/settings.json`:

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
        "GOOGLE_ADS_DEVELOPER_TOKEN": "your_developer_token_here",
        "GOOGLE_APPLICATION_CREDENTIALS": "path/to/credentials.json",
        "GOOGLE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

## Step 7: Test the Installation

1. **Test the server directly**:
   ```bash
   python -m ads_mcp.server
   ```
   Or if installed:
   ```bash
   google-ads-mcp
   ```

2. **In your MCP client**, try these prompts:
   - "what can the ads-mcp server do?"
   - "what customers do I have access to?"
   - "How many active campaigns do I have for customer id 1234567890?"

## Troubleshooting

### "GOOGLE_ADS_DEVELOPER_TOKEN environment variable not set"
- Make sure you've set the environment variable in your MCP client configuration
- Check that the variable name is exactly `GOOGLE_ADS_DEVELOPER_TOKEN`

### "Credentials not found"
- Verify the path in `GOOGLE_APPLICATION_CREDENTIALS` is correct
- Make sure you've run `gcloud auth application-default login`
- Check that the credentials file exists at the specified path

### "Permission denied" or authentication errors
- Verify your OAuth client has the correct scopes
- Make sure the Google Ads API is enabled in your Google Cloud project
- Check that your user account has access to the Google Ads accounts

### Module not found errors
- Make sure you've installed the package: `pip install -e .`
- Verify you're using the correct Python environment

## Next Steps

- Read the main [README.md](README.md) for more information
- Check out the [Contributing Guide](CONTRIBUTING.md) if you want to contribute

