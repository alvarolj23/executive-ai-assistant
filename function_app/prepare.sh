#!/bin/bash

# Exit on error
set -e

# Create eaia directory if it doesn't exist
mkdir -p eaia

# Copy eaia package from parent directory
echo "Copying eaia package..."
cp -r ../eaia/* eaia/

# Copy poetry files
echo "Copying poetry files..."
cp ../pyproject.toml .
cp ../poetry.lock .

# Clean up any Python cache files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

echo "Function app directory prepared successfully!" 