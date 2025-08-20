#!/bin/bash

# Test runner script for the workflow generator backend

set -e

echo "🧪 Running Backend Tests for Workflow Generator"
echo "=============================================="

# Change to backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📁 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install test dependencies if not already installed
echo "📦 Ensuring test dependencies are installed..."
uv sync --group test

# Run linting with ruff
echo "🔍 Running code linting..."
uv run ruff check app/ tests/ --fix || true

# Run type checking with mypy
echo "🔧 Running type checking..."
uv run mypy app/ || true

# Run unit tests
echo "🧪 Running unit tests..."
uv run pytest tests/unit/ -v --tb=short

# Run integration tests
echo "🔗 Running integration tests..."
uv run pytest tests/integration/ -v --tb=short

# Run all tests with coverage
echo "📊 Running all tests with coverage..."
uv run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

echo "✅ All tests completed!"
echo "📊 Coverage report generated in htmlcov/"
