#!/bin/bash
# Deployment script for Google Cloud Run

set -e

# Configuration
PROJECT_ID=${GOOGLE_PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="google-ads-mcp"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if developer token is set
if [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ]; then
    echo "Error: GOOGLE_ADS_DEVELOPER_TOKEN environment variable is not set"
    echo "Please set it before deploying:"
    echo "  export GOOGLE_ADS_DEVELOPER_TOKEN='your-token-here'"
    exit 1
fi

echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

echo "Pushing image to Container Registry..."
docker push ${IMAGE_NAME}

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_ADS_DEVELOPER_TOKEN=${GOOGLE_ADS_DEVELOPER_TOKEN},GOOGLE_PROJECT_ID=${PROJECT_ID}" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10

echo "Deployment complete!"
echo "Getting service URL..."
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'

