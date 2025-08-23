# FastAPI Backend Deployment Guide

## Overview

This document provides step-by-step instructions for deploying the FastAPI backend without managing VMs, Docker containers, or Nginx configurations. The frontend can be easily deployed to Vercel/Netlify, but the backend requires a platform that supports Python applications.

## 🎯 Problem Statement

- **Frontend deployment**: Easy with Vercel/Netlify
- **Backend deployment**: Challenging without managed services
- **Traditional approach**: Requires VM + Docker + Nginx + Domain setup
- **Solution**: Use managed backend platforms

## 🚀 Recommended Deployment Platforms

### 1. Railway (Recommended)
- **Cost**: $5/month after free credits
- **Setup time**: 5 minutes
- **Maintenance**: Zero
- **Features**: Auto-deploy, HTTPS, environment variables, database add-ons

### 2. Render
- **Cost**: Free tier available
- **Setup time**: 5 minutes  
- **Maintenance**: Zero
- **Features**: Auto-deploy, HTTPS, environment variables

### 3. Fly.io
- **Cost**: $5/month
- **Setup time**: 10 minutes
- **Maintenance**: Minimal
- **Features**: Global edge deployment, auto-scaling

## 📁 Project Structure

```
workflow-generator/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── api/             # API routes
│   │   └── ...
│   ├── requirements.txt     # Python dependencies
│   ├── Procfile            # Process configuration
│   ├── railway.toml        # Railway configuration
│   └── render.yaml         # Render configuration
├── frontend/               # React application
└── README.md
```

## 🔧 Backend Configuration Files

### requirements.txt
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
motor>=3.3.0
pydantic>=2.5.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
llama-index>=0.10.0
llama-index-core>=0.10.0
llama-index-llms-openai>=0.1.0
llama-index-embeddings-openai>=0.1.0
llama-index-agent-openai>=0.1.0
openai>=1.6.0
pydantic-settings>=2.1.0
httpx>=0.26.0
jinja2>=3.1.0
```

### Procfile
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### railway.toml
```toml
# Railway configuration
[build]
  builder = "NIXPACKS"

[deploy]
  restartPolicyType = "ON_FAILURE"
  restartPolicyMaxRetries = 10

[env]
  PORT = "8000"
  PYTHONPATH = "/app"
```

### render.yaml
```yaml
# Render configuration
services:
  - type: web
    name: workflow-backend
    runtime: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: PORT
        value: "8000"
```

## 🔐 CORS Configuration

Update `backend/app/main.py` to allow frontend domains:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "https://*.vercel.app",       # Vercel deployments
        "https://*.netlify.app",      # Netlify deployments
        "https://your-domain.com"     # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Deployment Instructions

### Option A: Railway Deployment

#### Prerequisites
- GitHub repository with your code
- Railway account (free signup)

#### Steps
1. **Prepare repository**
   ```bash
   git add .
   git commit -m "Add deployment configurations"
   git push origin main
   ```

2. **Deploy to Railway**
   - Visit [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Set root directory to `backend`
   - Railway auto-detects and deploys

3. **Configure environment variables**
   - Go to your project dashboard
   - Click "Variables" tab
   - Add required variables:
     ```
     MONGODB_URI=mongodb+srv://your-cluster.mongodb.net/workflow_generator
     OPENAI_API_KEY=your-openai-key
     ENVIRONMENT=production
     ```

4. **Get your backend URL**
   - Your API will be available at: `https://your-app-name.railway.app`

#### CLI Method (Alternative)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
cd backend
railway init

# Deploy
railway up
```

### Option B: Render Deployment

#### Prerequisites
- GitHub repository with your code
- Render account (free signup)

#### Steps
1. **Prepare repository**
   ```bash
   git add .
   git commit -m "Add render configuration"
   git push origin main
   ```

2. **Deploy to Render**
   - Visit [render.com](https://render.com)
   - Click "New Web Service"
   - Connect your GitHub repository
   - Configure service:
     - **Name**: workflow-backend
     - **Root Directory**: backend
     - **Build Command**: pip install -r requirements.txt
     - **Start Command**: uvicorn app.main:app --host 0.0.0.0 --port $PORT

3. **Configure environment variables**
   - In service settings, add:
     ```
     MONGODB_URI=mongodb+srv://your-cluster.mongodb.net/workflow_generator
     OPENAI_API_KEY=your-openai-key
     ENVIRONMENT=production
     ```

4. **Get your backend URL**
   - Your API will be available at: `https://your-app-name.onrender.com`

### Option C: Fly.io Deployment

#### Prerequisites
- Fly.io account
- Flyctl CLI installed

#### Steps
1. **Install Flyctl**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Initialize and deploy**
   ```bash
   cd backend
   fly launch --no-deploy
   
   # Configure fly.toml as needed
   fly deploy
   ```

3. **Set environment variables**
   ```bash
   fly secrets set MONGODB_URI="mongodb+srv://your-cluster.mongodb.net/workflow_generator"
   fly secrets set OPENAI_API_KEY="your-openai-key"
   fly secrets set ENVIRONMENT="production"
   ```

## 🌐 Frontend Configuration

Update your React app's API configuration:

### Environment Variables (.env.production)
```env
REACT_APP_API_URL=https://your-backend-url.railway.app
```

### API Client Configuration
```javascript
// src/config/api.js
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? process.env.REACT_APP_API_URL
  : 'http://localhost:8000';

export const apiClient = {
  baseURL: API_BASE_URL,
  
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
  }
};

// Usage example
// const workflows = await apiClient.request('/api/v1/workflows');
```

## 🗄️ Database Configuration

### MongoDB Atlas (Recommended)
1. Create MongoDB Atlas account
2. Create cluster
3. Get connection string
4. Add to environment variables as `MONGODB_URI`

### Alternative: Railway PostgreSQL
```bash
# In Railway dashboard
# Add PostgreSQL plugin
# Use the provided DATABASE_URL
```

## 📊 Environment Variables Reference

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/db` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ENVIRONMENT` | Application environment | `production` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `info` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## 🚀 Complete Deployment Checklist

### Backend Deployment
- [ ] Push code to GitHub
- [ ] Create deployment configuration files
- [ ] Deploy to chosen platform (Railway/Render/Fly.io)
- [ ] Configure environment variables
- [ ] Test API endpoints
- [ ] Verify database connectivity

### Frontend Deployment
- [ ] Update API base URL
- [ ] Deploy to Vercel/Netlify
- [ ] Test frontend-backend connectivity
- [ ] Configure custom domain (optional)

### Post-Deployment
- [ ] Test complete workflow functionality
- [ ] Monitor application logs
- [ ] Set up error tracking (optional)
- [ ] Configure monitoring/alerts (optional)

## 🔍 Troubleshooting

### Common Issues

#### 1. CORS Errors
**Problem**: Frontend can't connect to backend
**Solution**: Update CORS origins in `main.py`

#### 2. Environment Variables Not Loading
**Problem**: App can't connect to database/APIs
**Solution**: Verify environment variables are set correctly

#### 3. Build Failures
**Problem**: Deployment fails during build
**Solution**: Check requirements.txt and build logs

#### 4. Port Binding Issues
**Problem**: App doesn't start
**Solution**: Ensure app binds to `0.0.0.0:$PORT`

### Debugging Commands

```bash
# Check Railway logs
railway logs

# Check Render logs
# Available in Render dashboard

# Check Fly.io logs
fly logs

# Test API locally
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans | Features |
|----------|-----------|------------|----------|
| **Railway** | $5 credit | $5+/month | Auto-scaling, databases |
| **Render** | 750 hours/month | $7+/month | Auto-deploy, SSL |
| **Fly.io** | Limited | $5+/month | Edge deployment |
| **Traditional VM** | None | $20+/month | Full control, more setup |

## 📈 Scaling Considerations

### Performance Optimization
- Use connection pooling for database
- Implement caching for frequently accessed data
- Add rate limiting for API endpoints

### Monitoring
- Set up application monitoring (e.g., Sentry)
- Monitor database performance
- Track API response times

### Security
- Use environment variables for secrets
- Implement proper authentication
- Regular security updates

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [Fly.io Documentation](https://fly.io/docs/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review platform-specific documentation
3. Check application logs
4. Verify environment variables
5. Test locally first

---

**Last Updated**: August 23, 2025
**Version**: 1.0
