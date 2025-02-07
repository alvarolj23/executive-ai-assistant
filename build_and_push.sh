#!/bin/bash

# Exit on error
set -e

# Azure Container Registry credentials and configuration
ACR_NAME="acrstockanalysis"
RESOURCE_GROUP="rg-crypto-analysis"
LOCATION="West Europe"

# Application version and container name (adjust version as needed)
APP="executive-ai-assistant:v1.0.1"

# Set Azure subscription (using Visual Studio Enterprise Subscription)
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
docker buildx create --use --name mybuilder || true
docker buildx inspect mybuilder --bootstrap

# Build and push multi-architecture image directly
echo "Building and pushing multi-architecture image..."
docker buildx build --platform linux/amd64,linux/arm64 \
  --tag "${SERVER}/${APP}" \
  --push \
  .

echo "Build and push completed successfully!" 