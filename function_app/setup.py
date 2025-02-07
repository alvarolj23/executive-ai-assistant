from setuptools import setup, find_packages

setup(
    name="eaia",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "azure-functions",
        "httpx",
        "python-dotenv",
        "langgraph-sdk",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "azure-identity",
    ],
) 