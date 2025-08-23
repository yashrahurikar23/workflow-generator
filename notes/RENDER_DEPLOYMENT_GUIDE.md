# Render Deployment Guide - FastAPI Backend

## Overview

This guide will walk you through deploying your FastAPI workflow generator backend on Render's free tier. Render is an excellent choice for Python applications and offers a straightforward deployment process with automatic HTTPS, custom domains, and zero-downtime deploys.

## Why Render?

- **Free Tier**: Generous free tier perfect for development and small projects
- **Zero Configuration**: Automatic builds and deployments from Git
- **Python Optimized**: Native Python runtime support
- **Database Support**: Easy integration with PostgreSQL and Redis
- **No Infrastructure Management**: Fully managed platform

## Prerequisites

1. **Git Repository**: Your code should be in a GitHub, GitLab, or Bitbucket repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **MongoDB Database**: You'll need a MongoDB connection string (Atlas recommended)
4. **OpenAI API Key**: For AI functionality

## Step 1: Prepare Your Application

### 1.1 Verify Your Files

Ensure your backend directory has these essential files:

```text
backend/
├── app/
│   ├── main.py                 # Your FastAPI app
│   ├── core/
│   │   ├── config.py          # Settings
│   │   └── database.py        # MongoDB connection
│   └── api/
├── requirements.txt           # Dependencies
└── render.yaml               # Optional: Render configuration
```

### 1.2 Update requirements.txt

Your `requirements.txt` should include all necessary dependencies:

```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
motor>=3.3.0
pydantic>=2.5.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
openai>=1.6.0
requests>=2.31.0
beautifulsoup4>=4.12.2
pydantic-settings>=2.1.0
httpx>=0.26.0
```

### 1.3 Update Your FastAPI App

Ensure your `main.py` is configured for production:

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Workflow Generator API",
    version="1.0.0",
    description="A simple, extensible workflow generation system"
)

# CORS Configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Local development
        "https://*.vercel.app",           # Vercel deployments
        "https://*.netlify.app",          # Netlify deployments
        "https://your-domain.com",        # Your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Workflow Generator API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "workflow-generator-api"}

# Your routes here...

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

## Step 2: Deploy to Render

### 2.1 Create a New Web Service

1. **Login to Render**: Go to [render.com](https://render.com) and sign in
2. **Click "New +"**: In the dashboard, click the "New +" button
3. **Select "Web Service"**: Choose "Web Service" from the options
4. **Connect Repository**: Grant Render access to your GitHub/GitLab/Bitbucket repository

### 2.2 Configure Your Service

Fill out the configuration form:

| Field | Value | Description |
|-------|-------|-------------|
| **Name** | `workflow-generator-api` | Choose a unique name for your service |
| **Region** | `US East (N. Virginia)` | Choose the region closest to your users |
| **Branch** | `main` | The Git branch to deploy from |
| **Root Directory** | `backend` | Since your FastAPI app is in the backend folder |
| **Language** | `Python 3` | Render will auto-detect, or select manually |
| **Build Command** | `pip install -r requirements.txt` | Command to install dependencies |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Command to start your app |
| **Instance Type** | `Free` | Choose Free for development |

### 2.3 Advanced Options

Click "Advanced" to configure additional settings:

#### Environment Variables

Add these required environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `MONGODB_URI` | `mongodb+srv://username:password@cluster.mongodb.net/dbname` | Your MongoDB connection string |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |
| `PORT` | `8000` | Port for the application (auto-set by Render) |
| `PYTHONPATH` | `/opt/render/project/src/backend` | Python path for imports |

#### Health Check Path (Optional)

- **Health Check Path**: `/health`

This tells Render to monitor your `/health` endpoint to ensure your service is running properly.

### 2.4 Deploy

1. **Click "Create Web Service"**: This will start the deployment process
2. **Watch the Build**: You can monitor the build logs in real-time
3. **Wait for Completion**: First deployments usually take 2-5 minutes

## Step 3: Set Up MongoDB (if needed)

If you don't have a MongoDB database yet:

### Option 1: MongoDB Atlas (Recommended)

1. **Create Account**: Sign up at [mongodb.com/atlas](https://mongodb.com/atlas)
2. **Create Cluster**: Choose the free M0 cluster
3. **Configure Access**: 
   - Add your IP address (or 0.0.0.0/0 for Render)
   - Create a database user
4. **Get Connection String**: Copy the connection string
5. **Add to Render**: Update the `MONGODB_URI` environment variable

### Option 2: Render Postgres (Alternative)

If you prefer PostgreSQL, you can use Render's managed Postgres:

1. **Create Database**: In Render dashboard, click "New +" → "PostgreSQL"
2. **Configure**: Choose free tier and configure
3. **Update Code**: Modify your app to use PostgreSQL instead of MongoDB

## Step 4: Verify Deployment

### 4.1 Check Service Status

1. **Dashboard**: Your service should show "Live" status
2. **URL**: Render provides a URL like `https://workflow-generator-api.onrender.com`
3. **Test Endpoints**:
   - `GET /` - Should return basic info
   - `GET /health` - Should return health status

### 4.2 Test Your API

Use curl or your browser to test:

```bash
# Test health endpoint
curl https://your-service-name.onrender.com/health

# Expected response:
# {"status": "healthy", "service": "workflow-generator-api"}
```

### 4.3 Check Logs

If something isn't working:

1. **Go to Service**: Click on your service in the Render dashboard
2. **View Logs**: Click "Logs" to see real-time application logs
3. **Debug Issues**: Look for error messages or startup problems

## Step 5: Connect Frontend

Update your React frontend to use the deployed API:

```javascript
// In your React app, update the API base URL
const API_BASE_URL = 'https://your-service-name.onrender.com';

// Example API call
const response = await fetch(`${API_BASE_URL}/health`);
const data = await response.json();
```

## Step 6: Custom Domain (Optional)

To use your own domain:

1. **Add Domain**: In your service settings, go to "Custom Domains"
2. **Add Domain**: Click "Add" and enter your domain
3. **Configure DNS**: Add the CNAME record provided by Render to your DNS
4. **Update CORS**: Add your custom domain to the CORS origins list

## Troubleshooting

### Common Issues

#### Build Failures

**Problem**: `pip install` fails or missing dependencies
**Solution**: 
- Check your `requirements.txt` is in the root directory (`backend/`)
- Ensure all dependencies are listed with compatible versions
- Check build logs for specific error messages

#### Environment Variable Issues

**Problem**: `KeyError` or configuration errors
**Solution**:
- Verify all required environment variables are set
- Check for typos in variable names
- Ensure MongoDB URI format is correct

#### Import Errors

**Problem**: `ModuleNotFoundError` or import issues
**Solution**:
- Set `PYTHONPATH` environment variable to `/opt/render/project/src/backend`
- Check your import statements are relative to the backend directory
- Verify your app structure matches the expected layout

#### Health Check Failures

**Problem**: Service shows as unhealthy
**Solution**:
- Ensure your app listens on `0.0.0.0:$PORT`
- Check that the `/health` endpoint is responding
- Review startup logs for errors

### Debug Commands

Check your service status:

```bash
# View service details via Render API (optional)
curl -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services/$SERVICE_ID
```

## Render Service Limits (Free Tier)

- **Sleep**: Services sleep after 15 minutes of inactivity
- **Build Time**: 15 minutes maximum build time
- **Bandwidth**: 100GB/month outbound bandwidth
- **Memory**: 512MB RAM
- **Storage**: Ephemeral (no persistent storage)

## Scaling & Upgrading

When you're ready to scale:

1. **Upgrade Plan**: Switch from Free to Starter ($7/month) for always-on service
2. **Auto Scaling**: Configure auto-scaling based on CPU/memory
3. **Multiple Instances**: Run multiple instances for high availability
4. **Add Monitoring**: Set up log streaming and monitoring

## Next Steps

1. **Monitor Performance**: Use Render's built-in monitoring
2. **Set Up CI/CD**: Configure automatic deploys on push
3. **Add Database Backups**: Set up regular MongoDB backups
4. **Implement Caching**: Add Redis for improved performance
5. **Add Error Tracking**: Integrate with services like Sentry

## Additional Resources

- [Render FastAPI Documentation](https://render.com/docs/deploy-fastapi)
- [Render Environment Variables](https://render.com/docs/configure-environment-variables)
- [Render Troubleshooting](https://render.com/docs/troubleshooting-deploys)
- [Render API Documentation](https://render.com/docs/api)

---

**Need Help?** Check the Render community forums or their detailed documentation for specific issues. The Render team is also responsive on their Discord community.
