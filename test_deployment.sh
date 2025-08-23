#!/bin/bash

echo "🔍 WORKFLOW GENERATOR - DEPLOYMENT TEST"
echo "======================================"

echo ""
echo "🚀 Testing Render Deployment Status..."
echo "Time: $(date)"
echo "--------------------------------------------------"

# Common Render URL patterns - replace with your actual URL
RENDER_URLS=(
    "https://workflow-backend.onrender.com"
    "https://workflow-backend-abc123.onrender.com"  # Replace with actual if different
)

echo ""
for url in "${RENDER_URLS[@]}"; do
    echo "📡 Testing: $url"
    
    # Test health endpoint with timeout
    if curl -s --max-time 10 "$url/health" > /dev/null 2>&1; then
        echo "✅ Health check: SUCCESS"
        echo "   Response: $(curl -s --max-time 5 "$url/health")"
        
        # Test workflows API
        if curl -s --max-time 10 "$url/api/v1/workflows/" > /dev/null 2>&1; then
            echo "✅ Workflows API: SUCCESS"
        else
            echo "⚠️  Workflows API: Not accessible"
        fi
        
        echo ""
        echo "🎉 DEPLOYMENT IS LIVE!"
        echo "🔗 Your API URL: $url"
        echo "📖 API Docs: $url/docs"
        echo "🔧 Update your frontend to use this URL"
        exit 0
    else
        echo "❌ Health check failed: Connection timeout or error"
    fi
    echo ""
done

echo "🏠 Testing Local Backend..."
LOCAL_URLS=("http://localhost:8004" "http://localhost:8003" "http://localhost:8000")

for url in "${LOCAL_URLS[@]}"; do
    if curl -s --max-time 3 "$url/health" > /dev/null 2>&1; then
        echo "✅ Local backend running at: $url"
        LOCAL_FOUND=true
        break
    fi
done

if [ -z "$LOCAL_FOUND" ]; then
    echo "❌ No local backend found"
fi

echo ""
echo "📝 SUMMARY"
echo "----------"
echo "❌ Render: Not accessible yet"
if [ -n "$LOCAL_FOUND" ]; then
    echo "✅ Local: Running"
else
    echo "❌ Local: Not running"
fi

echo ""
echo "🔧 NEXT STEPS:"
echo "1. 📋 Check your Render dashboard for deployment status"
echo "2. 🔍 Look for build logs and any error messages"
echo "3. ⏳ Wait for deployment to complete (can take 5-10 minutes)"
echo "4. 🔄 Retry this test once deployment is ready"
echo "5. 📝 Get the actual Render URL from your dashboard"
echo ""
echo "💡 TIP: If using free tier, first request may take 30-60s to wake up"
