# Where to Set Environment Variables

This guide shows you exactly where to set environment variables for different scenarios.

## 🖥️ For Local Testing (Before Deployment)

### Windows PowerShell

```powershell
# Set for current session
$env:GOOGLE_ADS_DEVELOPER_TOKEN = "your-token-here"
$env:GOOGLE_PROJECT_ID = "your-project-id"

# Verify they're set
echo $env:GOOGLE_ADS_DEVELOPER_TOKEN
echo $env:GOOGLE_PROJECT_ID
```

### Windows Command Prompt (CMD)

```cmd
set GOOGLE_ADS_DEVELOPER_TOKEN=your-token-here
set GOOGLE_PROJECT_ID=your-project-id
```

### Linux/Mac (Bash)

```bash
export GOOGLE_ADS_DEVELOPER_TOKEN="your-token-here"
export GOOGLE_PROJECT_ID="your-project-id"

# Verify
echo $GOOGLE_ADS_DEVELOPER_TOKEN
echo $GOOGLE_PROJECT_ID
```

**Note:** These only last for the current terminal session. Close the terminal and they're gone.

---

## ☁️ For Cloud Run Deployment

You have **3 options** for setting environment variables in Cloud Run:

### Option 1: In the Deployment Command (Recommended)

Set them directly in the `gcloud run deploy` command:

```bash
gcloud run deploy google-ads-mcp \
  --image gcr.io/YOUR_PROJECT_ID/google-ads-mcp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_ADS_DEVELOPER_TOKEN=your-actual-token-here,GOOGLE_PROJECT_ID=your-project-id"
```

**Replace:**
- `your-actual-token-here` → Your actual developer token
- `your-project-id` → Your Google Cloud project ID

### Option 2: Using the Deployment Script

The `deploy.sh` script reads environment variables from your terminal:

```bash
# First, set them in your terminal (see "For Local Testing" above)
export GOOGLE_ADS_DEVELOPER_TOKEN="your-token-here"
export GOOGLE_PROJECT_ID="your-project-id"

# Then run the script
./deploy.sh
```

The script will automatically pass these to Cloud Run.

### Option 3: Via Google Cloud Console (After Deployment)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Run** → Your service (`google-ads-mcp`)
3. Click **Edit & Deploy New Revision**
4. Go to **Variables & Secrets** tab
5. Click **Add Variable**
6. Add:
   - Name: `GOOGLE_ADS_DEVELOPER_TOKEN`, Value: `your-token-here`
   - Name: `GOOGLE_PROJECT_ID`, Value: `your-project-id`
7. Click **Deploy**

---

## 🔄 Updating Environment Variables After Deployment

### Using gcloud CLI

```bash
# Update existing variables
gcloud run services update google-ads-mcp \
  --region us-central1 \
  --update-env-vars "GOOGLE_ADS_DEVELOPER_TOKEN=new-token,GOOGLE_PROJECT_ID=project-id"

# Add a new variable (e.g., for manager accounts)
gcloud run services update google-ads-mcp \
  --region us-central1 \
  --update-env-vars "GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890"
```

### Using Google Cloud Console

1. Go to Cloud Run → Your service
2. Click **Edit & Deploy New Revision**
3. **Variables & Secrets** tab
4. Modify or add variables
5. Click **Deploy**

---

## 📋 Complete Example: Full Deployment Process

### Step-by-Step for Windows PowerShell

```powershell
# 1. Set environment variables in your terminal
$env:GOOGLE_ADS_DEVELOPER_TOKEN = "ABC123XYZ"
$env:GOOGLE_PROJECT_ID = "my-google-ads-project"

# 2. Verify they're set
echo "Token: $env:GOOGLE_ADS_DEVELOPER_TOKEN"
echo "Project: $env:GOOGLE_PROJECT_ID"

# 3. Deploy (the script will use these variables)
./deploy.sh
```

Or manually:

```powershell
# Set variables
$env:GOOGLE_ADS_DEVELOPER_TOKEN = "ABC123XYZ"
$env:GOOGLE_PROJECT_ID = "my-google-ads-project"

# Deploy with variables in the command
gcloud run deploy google-ads-mcp `
  --image gcr.io/$env:GOOGLE_PROJECT_ID/google-ads-mcp `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars "GOOGLE_ADS_DEVELOPER_TOKEN=$env:GOOGLE_ADS_DEVELOPER_TOKEN,GOOGLE_PROJECT_ID=$env:GOOGLE_PROJECT_ID"
```

### Step-by-Step for Linux/Mac

```bash
# 1. Set environment variables
export GOOGLE_ADS_DEVELOPER_TOKEN="ABC123XYZ"
export GOOGLE_PROJECT_ID="my-google-ads-project"

# 2. Verify
echo "Token: $GOOGLE_ADS_DEVELOPER_TOKEN"
echo "Project: $GOOGLE_PROJECT_ID"

# 3. Deploy
./deploy.sh
```

---

## 🔍 Verify Environment Variables in Cloud Run

### Using gcloud CLI

```bash
gcloud run services describe google-ads-mcp \
  --region us-central1 \
  --format 'value(spec.template.spec.containers[0].env)'
```

### Using Google Cloud Console

1. Go to Cloud Run → Your service
2. Click on the service name
3. Go to **Revisions** tab
4. Click on the latest revision
5. Scroll to **Container** section
6. View **Environment variables**

---

## ⚠️ Security Best Practices

### ❌ DON'T Do This

```bash
# Don't hardcode tokens in scripts
echo "export GOOGLE_ADS_DEVELOPER_TOKEN=abc123" >> ~/.bashrc  # BAD!
```

### ✅ DO This Instead

1. **Use environment variables** (they're not saved to disk)
2. **Use Google Secret Manager** for production:
   ```bash
   # Create a secret
   echo -n "your-token" | gcloud secrets create google-ads-token --data-file=-
   
   # Use it in Cloud Run
   gcloud run services update google-ads-mcp \
     --region us-central1 \
     --update-secrets GOOGLE_ADS_DEVELOPER_TOKEN=google-ads-token:latest
   ```

---

## 📝 Summary

| Scenario | Where to Set | How Long It Lasts |
|----------|-------------|-------------------|
| **Local Testing** | Terminal session (`export` or `$env:`) | Until terminal closes |
| **Cloud Run Deployment** | In `--set-env-vars` flag | Permanently stored in Cloud Run |
| **Update After Deployment** | Cloud Console or `gcloud run update` | Permanently stored |

**For your deployment, you need to set them in the `gcloud run deploy` command using `--set-env-vars`.**

