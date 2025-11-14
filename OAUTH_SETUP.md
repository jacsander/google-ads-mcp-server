# OAuth 2.0 Setup for Google Ads API

## ⚠️ Important: Authentication Requirement

**Google Ads API requires OAuth 2.0 user credentials, NOT service accounts.**

The error you're seeing (`NOT_ADS_USER`, `UNAUTHENTICATED`) occurs because Cloud Run is trying to use Application Default Credentials (service account), which Google Ads API doesn't support.

## Solution: Set Up OAuth 2.0 Credentials

You have two options:

### Option 1: Environment Variables (Simpler, but less secure)

Store OAuth credentials as environment variables in Cloud Run.

### Option 2: Secret Manager (More secure, recommended for production)

Store OAuth credentials in Google Cloud Secret Manager.

---

## Step 1: Create OAuth 2.0 Credentials

### 1.1 Create OAuth Client in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `mimetic-perigee-290610`
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - User Type: **Internal** (if using Google Workspace) or **External**
   - App name: "Google Ads MCP Server"
   - Scopes: Add `https://www.googleapis.com/auth/adwords`
   - Save and continue
6. Application type: **Desktop app** or **Web application**
7. Name: "Google Ads MCP Server"
8. Click **Create**
9. **Save the Client ID and Client Secret** - you'll need these!

### 1.2 Get Refresh Token

You need to generate a refresh token for a user account that has access to your Google Ads accounts.

#### Method A: Using gcloud (Recommended)

```bash
# Set your OAuth client ID and secret
export GOOGLE_ADS_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_ADS_CLIENT_SECRET="your-client-secret"

# Authenticate and get refresh token
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform \
  --client-id-file=<(echo "{\"installed\":{\"client_id\":\"$GOOGLE_ADS_CLIENT_ID\",\"client_secret\":\"$GOOGLE_ADS_CLIENT_SECRET\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://oauth2.googleapis.com/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"redirect_uris\":[\"urn:ietf:wg:oauth:2.0:oob\",\"http://localhost\"]}}")

# After authentication, the refresh token will be in:
# ~/.config/gcloud/application_default_credentials.json (Linux/Mac)
# C:\Users\YourName\AppData\Roaming\gcloud\application_default_credentials.json (Windows)
```

#### Method B: Using Python Script

Create a file `get_refresh_token.py`:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/adwords']

# Your OAuth client credentials
CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "client_secret": "YOUR_CLIENT_SECRET",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
creds = flow.run_local_server(port=0)

print(f"Refresh Token: {creds.refresh_token}")
print(f"Client ID: {CLIENT_CONFIG['installed']['client_id']}")
print(f"Client Secret: {CLIENT_CONFIG['installed']['client_secret']}")
```

Run it:
```bash
python get_refresh_token.py
```

This will open a browser for authentication. After you authenticate, it will print your refresh token.

---

## Step 2: Configure Credentials in Cloud Run

### Option A: Environment Variables

```bash
gcloud run services update google-ads-mcp \
  --region us-central1 \
  --update-env-vars \
    "GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com,\
     GOOGLE_ADS_CLIENT_SECRET=your-client-secret,\
     GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token"
```

### Option B: Secret Manager (Recommended)

1. Create a secret with your OAuth credentials:

```bash
# Create a JSON file with your credentials
cat > oauth-credentials.json << EOF
{
  "client_id": "your-client-id.apps.googleusercontent.com",
  "client_secret": "your-client-secret",
  "refresh_token": "your-refresh-token"
}
EOF

# Create the secret
gcloud secrets create google-ads-oauth-credentials \
  --data-file=oauth-credentials.json \
  --project=mimetic-perigee-290610

# Grant Cloud Run service account access to the secret
PROJECT_NUMBER=$(gcloud projects describe mimetic-perigee-290610 --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding google-ads-oauth-credentials \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project=mimetic-perigee-290610

# Clean up the local file
rm oauth-credentials.json
```

2. The application will automatically load credentials from Secret Manager.

---

## Step 3: Verify the Setup

After deploying with OAuth credentials, check the logs:

```bash
gcloud run services logs read google-ads-mcp --region us-central1 --limit 20
```

You should see:
```
Using OAuth credentials from environment variables
Successfully refreshed OAuth credentials
```

If you see errors, check:
1. Client ID and secret are correct
2. Refresh token is valid and not expired
3. The user account has access to Google Ads accounts
4. The OAuth consent screen is properly configured

---

## Troubleshooting

### Error: "Invalid client"
- Check that your Client ID and Client Secret are correct
- Make sure you're using the credentials from the OAuth client you created

### Error: "Invalid grant"
- The refresh token may have been revoked
- Generate a new refresh token using the steps above

### Error: "NOT_ADS_USER"
- The Google account used to generate the refresh token doesn't have access to any Google Ads accounts
- Use a different Google account that has access to Google Ads, or add the account to a Google Ads account

### Error: "Access blocked"
- The OAuth consent screen may need to be configured
- Make sure the `https://www.googleapis.com/auth/adwords` scope is added

---

## Security Notes

- **Never commit OAuth credentials to version control**
- **Use Secret Manager for production deployments**
- **Rotate refresh tokens periodically**
- **Limit access to the secret to only the Cloud Run service account**

---

## Quick Reference

**Environment Variables:**
- `GOOGLE_ADS_CLIENT_ID` - Your OAuth client ID
- `GOOGLE_ADS_CLIENT_SECRET` - Your OAuth client secret  
- `GOOGLE_ADS_REFRESH_TOKEN` - Your OAuth refresh token

**Secret Manager:**
- Secret name: `google-ads-oauth-credentials`
- Format: JSON with `client_id`, `client_secret`, `refresh_token`

