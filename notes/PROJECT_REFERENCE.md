# Workflow Generator - Project Reference

## Overview

This document serves as a comprehensive reference for the Workflow Generator project, capturing its evolution from a complex multi-workflow system to a focused, production-grade workflow automation platform with web scraping capabilities.

## Project Evolution

### Initial Vision

- Multi-workflow automation platform supporting various automation types
- Complex node-based workflow system with visual interface
- Customer Support Email Automation as primary use case

### Current Focus

- **Simple Web Scraping Workflow**: URL input → Scrape → Summarize → Output
- **Production-Ready Deployment**: Focus on backend deployment without infrastructure overhead
- **Streamlined Architecture**: Simplified for rapid deployment and iteration

## Current Architecture

### Backend (FastAPI)

- **Framework**: FastAPI with Python 3.9+
- **Database**: MongoDB for workflow storage
- **AI Integration**: OpenAI API for content summarization
- **Web Scraping**: BeautifulSoup4 + Requests for content extraction

### Frontend (React)

- **Framework**: React with modern component architecture
- **Deployment**: Vercel/Netlify compatible
- **API Integration**: Connects to deployed FastAPI backend

## Key Features

### Web Scraping Workflow

1. **URL Input Node**: Accepts website URLs for scraping
2. **Web Scraping Node**: Extracts content using BeautifulSoup4
3. **Summarization Node**: AI-powered content summarization via OpenAI
4. **Output Node**: Formatted results delivery

### Deployment Solutions

- **Render**: **RECOMMENDED** - Free tier, Python-optimized, zero configuration
- **Railway**: Excellent developer experience, automatic Nixpacks builds
- **Fly.io**: Advanced option with global deployment and Docker support

## File Structure

```text
workflow-generator/
├── backend/
│   ├── app/
│   │   ├── main.py                           # FastAPI application
│   │   ├── services/
│   │   │   ├── node_registry.py              # Node type definitions
│   │   │   └── enhanced_workflow_executor.py # Execution engine
│   │   └── models/                           # Data models
│   ├── requirements.txt                      # Python dependencies
│   ├── Procfile                             # Process configuration
│   ├── railway.toml                         # Railway deployment config
│   ├── render.yaml                          # Render deployment config
│   └── test_web_scraping.py                 # Testing script
├── frontend/                                # React application
├── setup_web_scraping.py                   # Workflow seeding script
├── BACKEND_DEPLOYMENT_GUIDE.md             # Deployment instructions
├── RENDER_DEPLOYMENT_GUIDE.md              # Render-specific deployment guide
└── PROJECT_REFERENCE.md                    # This document
```

## Deployment Configuration

### Environment Variables

```bash
# Required for all deployments
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname
OPENAI_API_KEY=sk-...
PORT=8000

# Optional
PYTHONPATH=/app
```

### Platform-Specific Configs

#### Railway (railway.toml)

```toml
[build]
  builder = "NIXPACKS"

[deploy]
  restartPolicyType = "ON_FAILURE"
  restartPolicyMaxRetries = 10

[env]
  PORT = "8000"
  PYTHONPATH = "/app"
```

#### Render (render.yaml)

```yaml
services:
  - type: web
    name: workflow-generator-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHONPATH
        value: /opt/render/project/src
```

#### Procfile (Railway/Heroku-style)

```text
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Dependencies

### Backend (requirements.txt)

```text
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
motor==3.3.2
python-dotenv==1.0.0
openai==1.3.6
requests==2.31.0
beautifulsoup4==4.12.2
python-multipart==0.0.6
```

### Key Node Types

#### Web Scraping Nodes

1. **URLInputNode**: Accepts and validates URLs
2. **WebScrapingNode**: Extracts content from web pages
3. **SummarizationNode**: AI-powered content summarization
4. **OutputNode**: Formats and delivers results

## Quick Start Commands

### Setup Web Scraping Workflow

```bash
python setup_web_scraping.py
```

### Test Web Scraping

```bash
cd backend && python test_web_scraping.py
```

### Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

## API Endpoints

### Core Endpoints

- `GET /`: Health check
- `POST /workflows`: Create workflow
- `GET /workflows/{workflow_id}`: Get workflow
- `POST /workflows/{workflow_id}/execute`: Execute workflow
- `GET /workflows/{workflow_id}/status`: Check execution status

### Web Scraping API

- URL: Submit via workflow execution with URL input node
- Output: Receive scraped and summarized content

## Security Considerations

### CORS Configuration

```python
# Configured for production deployment
origins = [
    "http://localhost:3000",  # Local development
    "https://*.vercel.app",   # Vercel deployments
    "https://*.netlify.app",  # Netlify deployments
    # Add your custom domains here
]
```

### Environment Security

- Store sensitive keys in platform environment variables
- Use HTTPS for all production communications
- Implement rate limiting for public APIs

## Monitoring & Maintenance

### Health Checks

- Root endpoint (`/`) provides basic health status
- Database connectivity validation
- API key validation

### Logging

- FastAPI automatic request logging
- Custom logging for workflow execution
- Error tracking and debugging

## Future Enhancements

### Immediate Opportunities

1. **Enhanced Error Handling**: Robust error recovery in workflows
2. **Rate Limiting**: Prevent API abuse
3. **Caching**: Improve performance for repeated requests
4. **Monitoring**: Add application performance monitoring

### Long-term Vision

1. **Multi-Node Workflows**: Expand beyond simple linear workflows
2. **Visual Workflow Builder**: Drag-and-drop interface
3. **Webhook Integration**: Real-time workflow triggers
4. **Marketplace**: Community-contributed workflow templates

## Troubleshooting

### Common Issues

#### Deployment Failures

- Verify all environment variables are set
- Check requirements.txt includes all dependencies
- Ensure Python version compatibility (3.9+)

#### CORS Errors

- Update CORS origins in `main.py`
- Verify frontend URL matches allowed origins

#### Database Connection

- Validate MongoDB URI format
- Check network connectivity to MongoDB cluster
- Verify database user permissions

### Debug Commands

```bash
# Check environment variables
railway variables

# View deployment logs
railway logs

# Test local connection
python -c "import motor.motor_asyncio; print('MongoDB driver installed')"
```

## Contact & Support

### Development Team

- Primary Developer: Yash Rahurikar
- Repository: `/Users/yashrahurikar/yash/projects/personal/active/workflow-generator`

### Resources

- [Backend Deployment Guide](./BACKEND_DEPLOYMENT_GUIDE.md)
- [Render Deployment Guide](./RENDER_DEPLOYMENT_GUIDE.md)
- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

*Last Updated: August 23, 2025*
*Version: 2.0 (Web Scraping Focus)*
