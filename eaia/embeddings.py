"""Embeddings configuration for LangGraph."""
from langchain_openai import AzureOpenAIEmbeddings
from eaia.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
)

def init_embeddings(config: dict) -> AzureOpenAIEmbeddings:
    """Initialize Azure OpenAI embeddings for LangGraph."""
    return AzureOpenAIEmbeddings(
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        chunk_size=1,
    ) 