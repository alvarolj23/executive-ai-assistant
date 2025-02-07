# Build stage
FROM python:3.11-slim AS builder

# Install poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy project files needed for installation
COPY pyproject.toml poetry.lock README.md langgraph.json ./
COPY eaia ./eaia/
COPY scripts ./scripts/

# Configure poetry to create the virtualenv in the project directory
RUN poetry config virtualenvs.in-project true

# Install dependencies (using --only main instead of --no-dev)
RUN poetry install --only main --no-interaction --no-ansi

# Install langgraph-cli with inmem extra
RUN pip install "langgraph-cli[inmem]" langgraph-api

# Runtime stage
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=2024

# Create non-root user
RUN useradd -m -s /bin/bash app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv ./.venv

# Install langgraph-cli with inmem extra in runtime
RUN pip install "langgraph-cli[inmem]" langgraph-api

# Copy application code and necessary files
COPY eaia ./eaia
COPY scripts ./scripts
COPY pyproject.toml poetry.lock README.md langgraph.json ./

# Set ownership to non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose the correct port (2024 as specified in run_langgraph.py)
EXPOSE 2024

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-2024}/health || exit 1

# Command to run the application
CMD ["python", "scripts/run_langgraph.py"] 