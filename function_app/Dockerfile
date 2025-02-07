FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Create necessary directories
RUN mkdir -p /home/site/wwwroot

# Copy the function app files
COPY EmailIngestTrigger /home/site/wwwroot/EmailIngestTrigger/
COPY host.json /home/site/wwwroot/
COPY requirements.txt /home/site/wwwroot/

# Copy eaia package and its installation files
COPY eaia /home/site/wwwroot/eaia/
COPY pyproject.toml /home/site/wwwroot/
COPY poetry.lock /home/site/wwwroot/

# Set working directory
WORKDIR /home/site/wwwroot

# Install dependencies and eaia package
RUN pip install -r requirements.txt && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root 