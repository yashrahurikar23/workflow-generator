#!/bin/bash
# Test deployment status script
echo "Testing Render deployment status..."

for i in {1..10}; do
    echo "Attempt $i:"
    
    # Test status endpoint
    echo "Testing /status endpoint:"
    status_response=$(curl -s https://workflow-backend.onrender.com/status)
    echo "Status: $status_response"
    
    # Test health endpoint  
    echo "Testing /health endpoint:"
    health_response=$(curl -s https://workflow-backend.onrender.com/health)
    echo "Health: $health_response"
    
    # Check if we got valid JSON responses
    if [[ "$status_response" == *"Hello World"* ]] && [[ "$health_response" == *"healthy"* ]]; then
        echo "✅ Deployment successful! Both endpoints are working."
        exit 0
    fi
    
    echo "⏳ Deployment still in progress, waiting 30 seconds..."
    sleep 30
done

echo "❌ Deployment may have failed or is taking longer than expected."
echo "Check Render logs for more details."
