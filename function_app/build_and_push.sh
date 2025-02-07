#!/bin/bash

# Exit on error
set -e

# Azure Container Registry credentials and configuration
ACR_NAME="acrstockanalysis"
RESOURCE_GROUP="rg-crypto-analysis"
LOCATION="West Europe"

# Application version and container name
APP="email-ingest-function:v1.0.0"

# Set Azure subscription
echo "Setting Azure subscription..."
az account set --subscription "Visual Studio Enterprise Subscription – MPN"

# Get ACR server URL
SERVER="${ACR_NAME}.azurecr.io"
echo "Using ACR server: ${SERVER}"

# Login to Azure Container Registry
echo "Logging into Azure Container Registry..."
az acr login -n ${ACR_NAME}

# Create and use a new builder instance
echo "Setting up Docker buildx..."
docker buildx create --use --name function-builder || true
docker buildx inspect function-builder --bootstrap

# Build and push multi-architecture image directly
echo "Building and pushing multi-architecture image..."
docker buildx build --platform linux/amd64,linux/arm64 \
  --tag "${SERVER}/${APP}" \
  --push \
  .

echo "Build and push completed successfully!"

# Print next steps
echo ""
echo "Next steps:"
echo "1. Create an Azure Function App with container:"
echo "az functionapp create \\"
echo "  --name your-function-app-name \\"
echo "  --resource-group ${RESOURCE_GROUP} \\"
echo "  --storage-account your-storage-account \\"
echo "  --plan your-app-service-plan \\"
echo "  --deployment-container-image-name ${SERVER}/${APP} \\"
echo "  --docker-registry-server-url https://${SERVER}"
echo ""
echo "2. Configure Function App settings:"
echo "az functionapp config appsettings set \\"
echo "  --name your-function-app-name \\"
echo "  --resource-group ${RESOURCE_GROUP} \\"
echo "  --settings \\"
echo "    LANGGRAPH_URL=\"your-langgraph-url\" \\"
echo "    EMAIL_ADDRESS=\"your-email\" \\"
echo "    GMAIL_TOKEN=\"your-gmail-token\" \\"
echo "    GMAIL_SECRET=\"your-gmail-secret\" \\"
echo "    MINUTES_SINCE=\"60\"" 