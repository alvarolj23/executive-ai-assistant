"""Configuration for Azure OpenAI."""
from typing import Optional

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from eaia.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
)

def get_azure_llm(
    temperature: float = 0,
    model: Optional[str] = None,
    disable_streaming: Optional[bool] = None,
) -> AzureChatOpenAI:
    """Get configured Azure OpenAI LLM instance."""
    return AzureChatOpenAI(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        temperature=temperature,
        model=model,
        streaming=not disable_streaming if disable_streaming is not None else True,
    )


def get_azure_embeddings() -> AzureOpenAIEmbeddings:
    """Get configured Azure OpenAI embeddings instance."""
    return AzureOpenAIEmbeddings(
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        chunk_size=1,  # Process one text at a time
    ) 