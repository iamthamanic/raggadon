#!/bin/bash

# Sync requirements.txt from Poetry dependencies
# This keeps both systems in sync - Poetry for developers, requirements.txt for simple installs

set -e

echo "📦 Syncing requirements.txt from Poetry..."

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found. Run 'poetry init' first."
    exit 1
fi

# Generate requirements.txt from poetry.lock
echo "🔄 Generating requirements.txt from installed packages..."
poetry run pip freeze | grep -v -E "^-e git\+.*raggadon" > requirements.txt

# Filter out development dependencies for production requirements
echo "🔄 Filtering production dependencies..."
poetry run pip freeze | grep -v -E "(black|ruff|pre-commit|pytest|mypy|httpx)" | grep -v -E "^-e git\+.*raggadon" > requirements-prod.txt

echo "🔄 Creating development requirements..."
poetry run pip freeze | grep -E "(black|ruff|pre-commit|pytest|mypy|httpx)" > requirements-dev.txt

echo "✅ Requirements files updated!"
echo "   📄 requirements.txt - Production dependencies"
echo "   📄 requirements-dev.txt - Development dependencies"
echo ""
echo "💡 Tip: Run this script after updating pyproject.toml dependencies"