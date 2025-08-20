# Workflow Generator - Quick Start Guide

## Overview

This guide will help you set up the basic project structure and start development for your AI-powered workflow generation app similar to n8n.

## Project Structure

```
workflow-generator/
├── frontend/                 # React + Vite frontend
├── backend/                  # FastAPI backend
├── docker-compose.yml        # Development environment
├── README.md
├── PRODUCT_REQUIREMENTS.md   # Product specifications
└── ENGINEERING_ARCHITECTURE.md  # Technical architecture
```

## Technology Stack Summary

### Frontend Stack
- **React 18** with TypeScript
- **Vite** for fast development
- **React Flow** (@xyflow/react) for visual workflow editor
- **shadcn/ui** + Tailwind CSS for beautiful UI
- **Zustand** for state management

### Backend Stack  
- **FastAPI** for REST API
- **LlamaIndex** for AI workflow generation
- **MongoDB** for data storage
- **Redis** for caching and background jobs

## Quick Setup Commands

### 1. Initialize Frontend

```bash
# Create React + Vite + TypeScript project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install core dependencies
npm install @xyflow/react zustand axios react-hook-form @hookform/resolvers zod

# Install UI dependencies
npm install -D tailwindcss postcss autoprefixer @types/node
npx tailwindcss init -p

# Install shadcn/ui
npx shadcn-ui@latest init
```

### 2. Initialize Backend

```bash
# Create backend directory and virtual environment
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn motor pymongo llama-index python-jose bcrypt python-multipart

# Create requirements.txt
pip freeze > requirements.txt
```

### 3. Setup Development Environment

```bash
# Create docker-compose.yml for local development
touch docker-compose.yml

# Start MongoDB and Redis
docker-compose up -d mongo redis
```

## Next Steps

1. **Frontend Development**:
   - Set up React Flow workflow editor
   - Create node palette component
   - Implement basic drag-and-drop functionality

2. **Backend Development**:
   - Create FastAPI application structure
   - Set up MongoDB connections
   - Implement basic workflow CRUD operations
   - Integrate LlamaIndex for AI generation

3. **Integration**:
   - Connect frontend to backend APIs
   - Implement real-time execution monitoring
   - Add authentication and user management

## Development Workflow

1. **Start Services**:
   ```bash
   # Terminal 1: Start database services
   docker-compose up -d
   
   # Terminal 2: Start backend
   cd backend
   uvicorn app.main:app --reload --port 8000
   
   # Terminal 3: Start frontend  
   cd frontend
   npm run dev
   ```

2. **Access Applications**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Key Features to Implement First

### Phase 1 (MVP - 4-6 weeks)
1. **Visual Workflow Editor**:
   - Basic React Flow setup
   - Node palette with 5 essential node types
   - Drag and drop functionality
   - Node configuration panels

2. **AI Workflow Generation**:
   - LlamaIndex integration
   - Natural language to workflow conversion
   - Basic workflow templates

3. **Execution Engine**:
   - Simple workflow execution
   - Step-by-step monitoring
   - Basic error handling

4. **Data Storage**:
   - MongoDB workflow storage
   - Basic user management
   - Execution history

### Phase 2 (Enhanced - 6-8 weeks)
1. **Advanced Features**:
   - User authentication
   - Workflow sharing
   - Advanced node types
   - Real-time collaboration

2. **Integrations**:
   - Webhook triggers
   - External API connectors
   - Email notifications

## Architecture Decisions Made

### Why React Flow?
- **Mature**: Well-established library with excellent documentation
- **Performant**: Handles complex workflows efficiently
- **Customizable**: Easy to create custom node types
- **TypeScript**: Full TypeScript support

### Why FastAPI?
- **Performance**: One of the fastest Python frameworks
- **Modern**: Built-in async support, automatic API documentation
- **Type Safety**: Excellent Pydantic integration
- **Ecosystem**: Great compatibility with AI/ML libraries

### Why LlamaIndex?
- **AI-First**: Purpose-built for LLM applications
- **Flexible**: Supports various LLM providers
- **Workflow Support**: Built-in workflow orchestration
- **Production Ready**: Used in many production applications

### Why MongoDB?
- **Schema Flexibility**: Perfect for varying workflow structures
- **JSON-Native**: Natural fit for React Flow data structures
- **Scalability**: Horizontal scaling support
- **Rich Queries**: Advanced querying capabilities

## Development Tips

1. **Start Simple**: Begin with a minimal working version
2. **Test Early**: Set up testing from the beginning
3. **Document Everything**: Keep architecture decisions documented
4. **Performance First**: Profile and optimize as you build
5. **User Feedback**: Get user feedback early and often

## Resources

- [React Flow Documentation](https://reactflow.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [MongoDB Documentation](https://docs.mongodb.com/)

## Getting Help

1. **Product Questions**: Review PRODUCT_REQUIREMENTS.md
2. **Technical Questions**: Review ENGINEERING_ARCHITECTURE.md
3. **Setup Issues**: Check this guide first
4. **Architecture Decisions**: Refer to architecture document

---

**Happy Coding!** 🚀

Start with the MVP features and iterate based on user feedback. The architecture is designed to scale as your application grows.
