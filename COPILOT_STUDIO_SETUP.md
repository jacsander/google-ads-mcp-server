# Configuring Google Ads MCP Server in Copilot Studio

## ⚠️ Important: Authentication Setting

**You should select "None" for authentication** - the server already has your developer token configured via environment variables in Cloud Run.

## Correct Configuration Steps

### 1. Server Path
Enter your server URL:
```
https://google-ads-mcp-404988868020.us-central1.run.app
```

### 2. Authentication
**Select: "None"** ✅

**Do NOT select "API key"** - the server already has authentication configured.

### Why "None"?

- Your developer token (`LU9JLTXv0fWRIfh6jjXZ4Q`) is already set as an environment variable in Cloud Run
- The server uses Application Default Credentials from Google Cloud
- No additional API key authentication is needed from Copilot Studio

## If You Must Use API Key Authentication

If Copilot Studio requires API key authentication (which it shouldn't for this setup), you would need to:

1. **Header name:** Use a standard header name like `X-API-Key` or `Authorization`
2. **Header value:** Use your developer token `LU9JLTXv0fWRIfh6jjXZ4Q`

**However, this won't work** because our server doesn't read the developer token from request headers - it reads it from environment variables.

## The Error You're Seeing

The error occurs because:
1. You selected "API key" authentication
2. You put the developer token in the "Header name" field
3. The header name field has validation that doesn't allow certain characters
4. More importantly, the server doesn't expect authentication via headers

## Solution

**Change authentication to "None"** and try again. The server URL should be:
```
https://google-ads-mcp-404988868020.us-central1.run.app
```

## Alternative: If Copilot Studio Requires Authentication

If Copilot Studio absolutely requires some form of authentication, we would need to modify the server to accept the developer token via headers. However, this is not recommended for security reasons.

Instead, verify that:
1. The server URL is correct
2. Authentication is set to "None"
3. The server is accessible (test with the health endpoint)

## Test the Server First

Before configuring in Copilot Studio, verify the server is working:

```bash
# Test health endpoint
curl https://google-ads-mcp-404988868020.us-central1.run.app/health

# Should return: {"status":"healthy","service":"google-ads-mcp"}
```

## Troubleshooting

If "None" authentication doesn't work:

1. **Check server logs:**
   ```bash
   gcloud run services logs read google-ads-mcp --region us-central1 --limit 50
   ```

2. **Verify environment variables are set:**
   ```bash
   gcloud run services describe google-ads-mcp \
     --region us-central1 \
     --format 'value(spec.template.spec.containers[0].env)'
   ```

3. **Test the SSE endpoint directly:**
   ```bash
   curl -N https://google-ads-mcp-404988868020.us-central1.run.app/sse
   ```

## Summary

✅ **Use:** Authentication = "None"  
❌ **Don't use:** API key authentication  
✅ **Server URL:** `https://google-ads-mcp-404988868020.us-central1.run.app`

The server already has all the authentication it needs configured in Cloud Run!

