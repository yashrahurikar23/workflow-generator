#!/bin/bash

# Workflow Generator Setup Script
echo "🚀 Setting up Workflow Generator..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key before running the application."
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if command -v uv &> /dev/null; then
    uv sync
else
    echo "⚠️  uv not found. Installing with pip..."
    pip install uv
    uv sync
fi
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "🎯 Quick Start Options:"
echo ""
echo "1. Start with Docker Compose (recommended):"
echo "   docker-compose up --build"
echo ""
echo "2. Start components separately:"
echo "   # Terminal 1: Start databases"
echo "   docker-compose up -d mongo redis"
echo ""
echo "   # Terminal 2: Start backend"
echo "   cd backend && uv run uvicorn main:app --reload"
echo ""
echo "   # Terminal 3: Start frontend"
echo "   cd frontend && npm start"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📖 For more information, see the README.md file."
