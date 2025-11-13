# Deploying Google Ads MCP Server to Google Cloud Run

This guide will help you deploy the MCP server to Google Cloud Run so you can use it with Copilot or other MCP clients that require a server URL.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Google Cloud SDK (gcloud)** installed and authenticated
3. **Docker** installed (for local builds, optional)
4. **Google Ads Developer Token** (you already have this!)

## Quick Deployment

### Option 1: Using the Deployment Script (Recommended)

1. **Set environment variables:**
   ```bash
   export GOOGLE_ADS_DEVELOPER_TOKEN="your-token-here"
   export GOOGLE_PROJECT_ID="your-project-id"
   ```

2. **Make the script executable and run:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Note the service URL** from the output - you'll need this for Copilot!

### Option 2: Manual Deployment

#### Step 1: Build and Push Docker Image

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Build the image
docker build -t gcr.io/${PROJECT_ID}/google-ads-mcp .

# Push to Container Registry
docker push gcr.io/${PROJECT_ID}/google-ads-mcp
```

#### Step 2: Deploy to Cloud Run

**Set environment variables directly in the command** (replace the placeholder values):

```bash
gcloud run deploy google-ads-mcp \
  --image gcr.io/${PROJECT_ID}/google-ads-mcp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_ADS_DEVELOPER_TOKEN=your-actual-token-here,GOOGLE_PROJECT_ID=${PROJECT_ID}" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

**Important:** Replace `your-actual-token-here` with your real developer token in the command above!

#### Step 3: Get the Service URL

```bash
gcloud run services describe google-ads-mcp \
  --region us-central1 \
  --format 'value(status.url)'
```

## Configuration for Copilot

Once deployed, configure Copilot to use the MCP server URL:

### For Copilot (MCP Configuration)

Add to your Copilot MCP settings:

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "url": "https://google-ads-mcp-xxxxx-uc.a.run.app/sse"
    }
  }
}
```

Replace the URL with your actual Cloud Run service URL + `/sse` endpoint.

## Environment Variables

The following environment variables are set in Cloud Run:

- `GOOGLE_ADS_DEVELOPER_TOKEN` - Your Google Ads developer token
- `GOOGLE_PROJECT_ID` - Your Google Cloud project ID
- `PORT` - Automatically set by Cloud Run (8080)

### Setting Additional Variables

If you need to set `GOOGLE_ADS_LOGIN_CUSTOMER_ID` (for manager accounts):

```bash
gcloud run services update google-ads-mcp \
  --region us-central1 \
  --update-env-vars "GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890"
```

## Authentication

The server uses **Application Default Credentials (ADC)** from Google Cloud. Make sure:

1. The Cloud Run service has the necessary IAM permissions
2. The service account has access to Google Ads API
3. You've enabled the Google Ads API in your project

### Granting Permissions

```bash
# Get the service account email
SERVICE_ACCOUNT=$(gcloud run services describe google-ads-mcp \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')

# Grant necessary roles (if using a custom service account)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/run.invoker"
```

## Testing the Deployment

### Health Check

```bash
curl https://your-service-url.run.app/health
```

Should return:
```json
{"status": "healthy", "service": "google-ads-mcp"}
```

### Test SSE Endpoint

```bash
curl -N https://your-service-url.run.app/sse
```

## Updating the Deployment

To update the server after making changes:

```bash
# Rebuild and push
docker build -t gcr.io/${PROJECT_ID}/google-ads-mcp .
docker push gcr.io/${PROJECT_ID}/google-ads-mcp

# Update Cloud Run service
gcloud run services update google-ads-mcp \
  --region us-central1 \
  --image gcr.io/${PROJECT_ID}/google-ads-mcp
```

## Troubleshooting

### Check Logs

```bash
gcloud run services logs read google-ads-mcp --region us-central1
```

### Common Issues

1. **"Module not found" errors**
   - Make sure all dependencies are in `pyproject.toml`
   - Rebuild the Docker image

2. **"Credentials not found" errors**
   - Verify the service account has proper permissions
   - Check that Google Ads API is enabled

3. **"Developer token not set" errors**
   - Verify environment variables in Cloud Run:
     ```bash
     gcloud run services describe google-ads-mcp \
       --region us-central1 \
       --format 'value(spec.template.spec.containers[0].env)'
     ```

## Cost Considerations

Cloud Run charges based on:
- **CPU and memory** allocated
- **Request count**
- **Request duration**

The default configuration (512Mi memory, 1 CPU) should be sufficient for most use cases. You can adjust these in the deployment command.

## Security Notes

- The deployment uses `--allow-unauthenticated` for simplicity
- For production, consider using authentication:
  ```bash
  gcloud run services update google-ads-mcp \
    --region us-central1 \
    --no-allow-unauthenticated
  ```
- Then use IAM or API keys for authentication

## Next Steps

1. Deploy the server using one of the methods above
2. Get the service URL
3. Configure Copilot with the URL
4. Test the connection!

For more information, see:
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)

