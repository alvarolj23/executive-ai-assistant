"""Configuration for Azure OpenAI."""
import os
from typing import Optional

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from dotenv import load_dotenv
import os

load_dotenv() 

def get_azure_llm(
    temperature: float = 0,
    model: Optional[str] = None,
    disable_streaming: Optional[bool] = None,
) -> AzureChatOpenAI:
    """Get configured Azure OpenAI LLM instance."""
    return AzureChatOpenAI(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        temperature=temperature,
        model=model,
        streaming=not disable_streaming if disable_streaming is not None else True,
    )


def get_azure_embeddings() -> AzureOpenAIEmbeddings:
    """Get configured Azure OpenAI embeddings instance."""
    # Try to get API key from either environment variable
    api_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("AZURE_OPENAI_KEY")
    if not api_key:
        raise ValueError("No Azure OpenAI API key found in environment variables")

    return AzureOpenAIEmbeddings(
        azure_deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=api_key,
        chunk_size=1,  # Process one text at a time
    ) 