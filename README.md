# Workflow Generator

A robust, AI-powered workflow generation application with a FastAPI/MongoDB backend and React frontend. This project provides a solid foundation for building workflow automation tools with modern web technologies and AI integration.

## 🚀 Current Status

### ✅ **COMPLETED** 
- **Backend Infrastructure**: FastAPI app with comprehensive CRUD operations, MongoDB integration, and LlamaIndex support
- **Database Models**: Workflow model with metadata, steps, and AI-generated content support
- **API Endpoints**: Full REST API with OpenAPI documentation for workflow management  
- **Testing Suite**: 100% passing unit and integration tests (44/44) with 73% code coverage
- **Frontend Foundation**: React 19 + TypeScript app with Tailwind CSS, shadcn/ui components, and theming
- **State Management**: Zustand store with workflow state management and error handling
- **Development Environment**: Docker setup, Python virtual environment, and build configurations

### � **IN PROGRESS**
- **API Integration**: Frontend currently uses mock data - needs real API integration
- **UI Polish**: Basic workflow interface exists but needs workflow designer implementation

### 📋 **TODO**
- **Visual Workflow Designer**: React Flow integration for drag-and-drop workflow creation
- **AI-Powered Generation**: Natural language workflow creation using LlamaIndex
- **Real-time Execution**: Execute workflows with live monitoring
- **Authentication**: User management and secure access

## 📋 Documentation

- [**Product Requirements**](./notes/PRODUCT_REQUIREMENTS.md) - Detailed product specifications and user stories
- [**Engineering Architecture**](./notes/ENGINEERING_ARCHITECTURE.md) - Complete technical architecture and implementation details
- [**Quick Start Guide**](./notes/QUICK_START.md) - Step-by-step setup instructions

## 🛠 Technology Stack

### Frontend (✅ Implemented)

- React 19 + TypeScript
- Tailwind CSS for styling  
- shadcn/ui component library
- Zustand for state management
- Axios for API communication (configured, using mock data)

### Backend (✅ Implemented)

- FastAPI (Python 3.11+) with async support
- uv for Python package management
- LlamaIndex for AI workflow capabilities (integrated, not yet used)
- Pydantic for data validation
- MongoDB for data storage (configured, using in-memory for development)
- Comprehensive testing with pytest (44 tests, 73% coverage)

### Development Tools (✅ Configured)

- Docker & Docker Compose for containerization
- Ruff for Python linting and formatting
- MyPy for static type checking
- Pytest with coverage reporting
- ESLint and Prettier for JavaScript/TypeScript

## 📦 Quick Setup

1. **Clone and setup environment**:

   ```bash
   git clone <repository-url>
   cd workflow-generator
   cp .env.example .env
   # Edit .env with your API keys (OpenAI, etc.)
   ```

2. **Start development environment**:

   ```bash
   # Backend setup (Python 3.11+)
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install uv
   uv sync  # Install dependencies
   
   # Run backend tests
   ./run_tests.sh
   
   # Start backend server
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Frontend setup (in new terminal)
   cd frontend
   npm install
   npm start
   ```

3. **Access the application**:

   - Frontend: <http://localhost:3001>
   - Backend API: <http://localhost:8000>
   - API Documentation: <http://localhost:8000/docs>

## 🧪 Testing

The backend includes comprehensive testing:

```bash
cd backend
./run_tests.sh  # Runs all tests with coverage
```

- **Unit Tests**: 44/44 passing
- **Coverage**: 73% overall
- **Integration Tests**: Full API endpoint testing with mock database

## 🎯 Development Roadmap

### Phase 1 (MVP Foundation) ✅ **COMPLETED**

- [x] Project setup and architecture
- [x] FastAPI backend with CRUD operations
- [x] MongoDB integration and data models
- [x] Comprehensive testing suite (44 tests, 73% coverage)
- [x] React frontend with TypeScript
- [x] Tailwind CSS and shadcn/ui components
- [x] Zustand state management
- [x] Docker containerization setup

### Phase 2 (UI & Integration) 🔄 **IN PROGRESS**

- [ ] Real API integration (replace mock data)
- [ ] React Flow workflow designer
- [ ] Workflow creation and editing UI
- [ ] AI workflow generation with LlamaIndex
- [ ] Basic execution engine

### Phase 3 (Enhanced Features) 📋 **PLANNED**

- [ ] User authentication and authorization  
- [ ] Advanced node types and configurations
- [ ] Real-time execution monitoring
- [ ] Webhook triggers and scheduling
- [ ] External API integrations

### Phase 4 (Production Ready) 📋 **PLANNED**

- [ ] Performance optimization
- [ ] Advanced error handling and retry logic
- [ ] Workflow templates marketplace
- [ ] Team collaboration features
- [ ] Enterprise deployment options

## 🏗 Project Structure

```text
workflow-generator/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/       # UI components (theme-provider, mode-toggle)
│   │   ├── store/           # Zustand state stores (workflow-store)
│   │   ├── services/        # API services (configured for backend)
│   │   ├── lib/             # Utilities (shadcn/ui utils)
│   │   └── App.tsx          # Main app component
│   ├── package.json         # Node.js dependencies
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── Dockerfile           # Frontend container
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/endpoints/ # API route handlers (workflows)
│   │   ├── core/            # Core functionality (config, database)
│   │   ├── models/          # Pydantic models (workflow)
│   │   └── crud/            # CRUD operations (workflow)
│   ├── tests/               # Comprehensive test suite
│   │   ├── unit/            # Unit tests (models, crud)
│   │   └── integration/     # Integration tests (API)
│   ├── main.py              # FastAPI app entry point
│   ├── pyproject.toml       # Python dependencies and config
│   ├── run_tests.sh         # Test runner script
│   └── Dockerfile           # Backend container
├── notes/                    # Documentation
│   ├── PRODUCT_REQUIREMENTS.md
│   ├── ENGINEERING_ARCHITECTURE.md
│   └── QUICK_START.md
├── docker-compose.yml        # Development environment
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🚀 Next Steps

### For Developers

1. **Connect Frontend to Backend**: Replace mock data in `frontend/src/store/workflow-store.ts` with real API calls
2. **Add React Flow**: Integrate visual workflow designer for drag-and-drop functionality  
3. **AI Integration**: Implement LlamaIndex workflow generation in the backend
4. **Authentication**: Add user management and secure API endpoints

### For Contributors

1. Review the [Engineering Architecture](./notes/ENGINEERING_ARCHITECTURE.md) for technical details
2. Check [Product Requirements](./notes/PRODUCT_REQUIREMENTS.md) for feature specifications
3. Follow the [Quick Start Guide](./notes/QUICK_START.md) for development setup
4. All backend functionality is tested - extend tests when adding new features

## 🔧 Key Technical Decisions

- **FastAPI**: Chosen for performance, async support, and automatic API documentation
- **React 19**: Latest version with TypeScript for type safety and modern development
- **Zustand**: Lightweight state management without Redux complexity
- **shadcn/ui**: High-quality, customizable components with Tailwind CSS
- **uv**: Fast Python package management and virtual environment handling
- **pytest**: Comprehensive testing with mocking for reliable CI/CD

## 🤝 Contributing

1. Read the documentation in the `/notes` folder
2. Set up the development environment following the Quick Setup guide
3. Run tests to ensure everything works: `cd backend && ./run_tests.sh`
4. Create a feature branch and submit a pull request
5. Ensure new features include tests and documentation

## 📝 License

[Add your license here]

## 🆘 Support

- Check the documentation in the `/notes` folder  
- Review the Quick Start guide for setup issues
- Backend API documentation: <http://localhost:8000/docs> when running
- Submit issues for bugs or feature requests

---

Built with ❤️ for workflow automation enthusiasts
