# Pre-Copilot Setup Checklist

Use this checklist to ensure everything is ready before connecting to Copilot.

## ✅ Project Folder (COMPLETE)
- [x] Python packages installed
- [x] Server code ready
- [x] Setup documentation created
- [x] Configuration examples provided

## ⚠️ Required Before Connecting to Copilot

### 1. Google Cloud Authentication
- [ ] Install Google Cloud SDK (gcloud CLI)
  - Download: https://cloud.google.com/sdk/docs/install
- [ ] Run authentication:
  ```bash
  gcloud auth application-default login --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
  ```
- [ ] **Copy the credentials file path** from the output
  - Example: `C:\Users\jsander\AppData\Roaming\gcloud\application_default_credentials.json`

### 2. Enable Google Ads API
- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Select your project (or create one)
- [ ] Enable [Google Ads API](https://console.cloud.google.com/apis/library/googleads.googleapis.com)
- [ ] Note your **Project ID** (not Project Name)

### 3. Developer Token
- [x] You have your developer token ✅
- [ ] You know where to paste it (Copilot MCP config)

### 4. Copilot Configuration
- [ ] Find Copilot's MCP configuration file location
  - Check: `%APPDATA%\Microsoft\Copilot\`
  - Check: `%LOCALAPPDATA%\Microsoft\Copilot\`
  - Or check Copilot settings/preferences
- [ ] Add the MCP server configuration (see `COPILOT_SETUP.md`)
- [ ] Replace placeholder values:
  - Developer token
  - Credentials file path
  - Project ID

### 5. Test the Server
- [ ] Test server directly (optional but recommended):
  ```bash
  # Set env vars temporarily
  $env:GOOGLE_ADS_DEVELOPER_TOKEN = "your-token"
  $env:GOOGLE_APPLICATION_CREDENTIALS = "path-to-credentials"
  $env:GOOGLE_PROJECT_ID = "your-project-id"
  
  # Test
  python -m ads_mcp.server
  ```

## 🎯 Ready to Connect?

Once all items above are checked, you can:
1. Configure Copilot with the MCP server
2. Restart Copilot
3. Start using the Google Ads MCP server!

## 📖 Next Steps

- See [COPILOT_SETUP.md](COPILOT_SETUP.md) for detailed Copilot configuration
- See [SETUP_LOCAL.md](SETUP_LOCAL.md) for comprehensive setup guide

