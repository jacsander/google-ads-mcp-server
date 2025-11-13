# Cloud Run Deployment - Ready to Deploy! 🚀

Your Google Ads MCP server is now ready to be deployed to Google Cloud Run!

## What's Been Created

✅ **HTTP Server** (`ads_mcp/http_server.py`)
- FastAPI-based HTTP server
- `/health` endpoint for health checks
- `/sse` endpoint for MCP Server-Sent Events
- `/messages` endpoint for HTTP POST (alternative)

✅ **Docker Configuration**
- `Dockerfile` - Container image definition
- `.dockerignore` - Excludes unnecessary files

✅ **Deployment Scripts**
- `deploy.sh` - Automated deployment script
- `cloudbuild.yaml` - Google Cloud Build configuration

✅ **Documentation**
- `CLOUD_RUN_DEPLOYMENT.md` - Complete deployment guide

## Quick Start

### 1. Set Environment Variables

```bash
export GOOGLE_ADS_DEVELOPER_TOKEN="your-token-here"
export GOOGLE_PROJECT_ID="your-project-id"
```

### 2. Deploy

```bash
# Make script executable (if on Linux/Mac)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

Or manually:

```bash
# Build and push
docker build -t gcr.io/${GOOGLE_PROJECT_ID}/google-ads-mcp .
docker push gcr.io/${GOOGLE_PROJECT_ID}/google-ads-mcp

# Deploy
gcloud run deploy google-ads-mcp \
  --image gcr.io/${GOOGLE_PROJECT_ID}/google-ads-mcp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_ADS_DEVELOPER_TOKEN=${GOOGLE_ADS_DEVELOPER_TOKEN},GOOGLE_PROJECT_ID=${GOOGLE_PROJECT_ID}"
```

### 3. Get Your Server URL

```bash
gcloud run services describe google-ads-mcp \
  --region us-central1 \
  --format 'value(status.url)'
```

Your MCP server URL will be: `https://google-ads-mcp-xxxxx.run.app`

## Configure Copilot

Add to your Copilot MCP configuration:

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "url": "https://google-ads-mcp-xxxxx.run.app/sse"
    }
  }
}
```

## Important Notes

### MCP HTTP/SSE Implementation

The current HTTP server implementation provides a basic framework for MCP over HTTP/SSE. The `/sse` endpoint is set up, but you may need to:

1. **Verify MCP Protocol Compatibility**: Ensure the implementation matches your Copilot's expected MCP protocol format
2. **Test the Connection**: After deployment, test that Copilot can connect successfully
3. **Refine if Needed**: The SSE endpoint may need adjustments based on actual MCP protocol requirements

### Authentication

The deployment uses Application Default Credentials from Google Cloud. Make sure:

- The Cloud Run service account has access to Google Ads API
- Google Ads API is enabled in your project
- The service account has the necessary IAM roles

### Next Steps

1. **Deploy** using the script or manual commands above
2. **Test** the health endpoint: `curl https://your-url.run.app/health`
3. **Configure Copilot** with the server URL
4. **Verify** the connection works

## Troubleshooting

If you encounter issues:

1. **Check logs**: `gcloud run services logs read google-ads-mcp --region us-central1`
2. **Verify environment variables**: Check they're set correctly in Cloud Run
3. **Test locally first**: Run `python -m ads_mcp.http_server` to test the server

## Documentation

- See `CLOUD_RUN_DEPLOYMENT.md` for detailed deployment instructions
- See `README.md` for general server information

Good luck with your deployment! 🎉

