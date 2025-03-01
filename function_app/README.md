# Email Ingestion Function App

## Overview

This Azure Function App serves as the email ingestion component for the Executive AI Assistant (EAIA) system. It periodically checks for new emails in a specified Gmail account and forwards them to a LangGraph server for processing by the AI assistant.

## Architecture

The function app consists of a timer-triggered Azure Function that runs on a schedule (every 5 minutes by default). The function:

1. Connects to Gmail using OAuth credentials
2. Fetches recent emails (from a configurable time window)
3. Creates threads in a LangGraph server for each email
4. Submits the emails to the LangGraph server for processing

## Components

### EmailIngestTrigger

The main Azure Function that runs on a schedule defined in `function.json`. It:
- Initializes the LangGraph client
- Fetches emails from Gmail
- Processes each email and sends it to the LangGraph server

### EAIA Package

The function app includes a copy of the EAIA package, which provides:
- Gmail integration (`eaia/gmail.py`)
- Data schemas (`eaia/schemas.py`)
- Configuration utilities (`eaia/main/config.py`)
- Azure OpenAI integration (`eaia/main/azure_config.py`)

## Configuration

### Environment Variables

The function app requires the following environment variables:

| Variable | Description |
|----------|-------------|
| `LANGGRAPH_URL` | URL of the LangGraph server |
| `EMAIL_ADDRESS` | Gmail address to monitor |
| `GMAIL_TOKEN` | OAuth token for Gmail access |
| `GMAIL_SECRET` | OAuth client secret for Gmail |
| `MINUTES_SINCE` | Time window for email fetching (default: 60) |

### Timer Schedule

The function runs on a schedule defined in `function.json`. The default is every 5 minutes (`0 */5 * * * *`).

## Deployment

### Prerequisites

- Azure subscription
- Azure Container Registry
- Azure Function App (Premium or Dedicated plan for Docker support)
- Gmail account with OAuth credentials

### Deployment Steps

1. **Prepare the function app**:
   ```bash
   ./prepare.sh
   ```
   This copies the EAIA package and Poetry files into the function app directory.

2. **Build and push the Docker image**:
   ```bash
   cd function_app
   ./build_and_push.sh
   ```
   This builds a multi-architecture Docker image and pushes it to Azure Container Registry.

3. **Create an Azure Function App**:
   ```bash
   az functionapp create \
     --name your-function-app-name \
     --resource-group your-resource-group \
     --storage-account your-storage-account \
     --plan your-app-service-plan \
     --deployment-container-image-name acrstockanalysis.azurecr.io/email-ingest-function:v1.0.5 \
     --docker-registry-server-url https://acrstockanalysis.azurecr.io
   ```

4. **Configure Function App settings**:
   ```bash
   az functionapp config appsettings set \
     --name your-function-app-name \
     --resource-group your-resource-group \
     --settings \
       LANGGRAPH_URL="your-langgraph-url" \
       EMAIL_ADDRESS="your-email" \
       GMAIL_TOKEN="your-gmail-token" \
       GMAIL_SECRET="your-gmail-secret" \
       MINUTES_SINCE="60"
   ```

## Local Development

### Prerequisites

- Docker
- Azure Functions Core Tools
- Python 3.11

### Running Locally

1. **Prepare the function app**:
   ```bash
   ./prepare.sh
   ```

2. **Create a local settings file**:
   Create a `local.settings.json` file in the function_app directory:
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "LANGGRAPH_URL": "http://localhost:2024",
       "EMAIL_ADDRESS": "your-email@gmail.com",
       "GMAIL_TOKEN": "your-gmail-token",
       "GMAIL_SECRET": "your-gmail-secret",
       "MINUTES_SINCE": "60"
     }
   }
   ```

3. **Run the function locally**:
   ```bash
   cd function_app
   func start
   ```

4. **Test Gmail connection**:
   ```bash
   cd function_app
   python -m tests.test_gmail_connection
   ```

## Troubleshooting

### Common Issues

1. **Gmail Authentication Errors**:
   - Ensure the `GMAIL_TOKEN` and `GMAIL_SECRET` are correctly set
   - Check if the token has expired and needs to be refreshed

2. **LangGraph Connection Issues**:
   - Verify the `LANGGRAPH_URL` is correct and accessible
   - Check network connectivity between the function app and LangGraph server

3. **Function Not Triggering**:
   - Check the function app logs for any errors
   - Verify the timer schedule in `function.json`

### Logging

The function app uses the Azure Functions logging system. Logs can be viewed in:
- Azure Portal (Function App > Functions > EmailIngestTrigger > Monitor)
- Application Insights (if configured)
- Local console when running with `func start`

## Security Considerations

- OAuth tokens and secrets are stored as application settings in Azure
- The function app uses managed identity for Azure resources when possible
- All communication with external services uses HTTPS

## Future Improvements

- Add retry logic for transient errors
- Implement more robust error handling
- Add telemetry for monitoring email processing
- Support additional email providers beyond Gmail