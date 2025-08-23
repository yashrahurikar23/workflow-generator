#!/bin/bash

# Frontend-Backend Integration Test Script
# Tests the connection between the React frontend and the deployed FastAPI backend

echo "🧪 Frontend-Backend Integration Test"
echo "===================================="

# Test 1: Check if backend is accessible
echo "1. Testing backend health endpoint..."
BACKEND_URL="https://workflow-backend.onrender.com"
curl -s "$BACKEND_URL/health" | jq '.' || echo "❌ Backend health check failed"

# Test 2: Test workflows endpoint
echo -e "\n2. Testing workflows endpoint..."
curl -s "$BACKEND_URL/api/v1/workflows/" | jq '.workflows[0:2]' || echo "❌ Workflows endpoint failed"

# Test 3: Check if frontend is running
echo -e "\n3. Testing frontend accessibility..."
FRONTEND_URL="http://localhost:3003"
curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200" && echo "✅ Frontend is accessible" || echo "❌ Frontend not accessible"

# Test 4: Test CORS headers
echo -e "\n4. Testing CORS headers..."
curl -s -I -H "Origin: http://localhost:3003" "$BACKEND_URL/health" | grep -i "access-control" && echo "✅ CORS headers present" || echo "❌ CORS headers missing"

# Test 5: Test chat threads endpoint
echo -e "\n5. Testing chat threads endpoint..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"title":"Test Thread","metadata":{"test":true}}' \
  "$BACKEND_URL/api/v1/chat/threads" | jq '.thread_id' || echo "❌ Chat threads failed"

echo -e "\n🎉 Integration test complete!"
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo -e "\nTo test the full workflow:"
echo "1. Open $FRONTEND_URL in your browser"
echo "2. Click 'Create New Workflow'"
echo "3. Test workflow creation and execution"
echo "4. Try the chat functionality"
