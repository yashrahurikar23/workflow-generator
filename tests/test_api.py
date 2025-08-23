#!/usr/bin/env python3
import json

import requests

BASE_URL = "http://localhost:8003/api/v1"

def test_api():
    print("🧪 Testing Workflow Generator API...")
    
    # Test 1: List workflows (should return empty list initially)
    print("\n1. Testing GET /workflows")
    try:
        response = requests.get(f"{BASE_URL}/workflows")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Create a new workflow
    print("\n2. Testing POST /workflows")
    workflow_data = {
        "name": "Test Workflow",
        "description": "A simple test workflow",
        "steps": [
            {
                "step_id": "step1",
                "name": "API Call",
                "step_type": "api_call",
                "config": {
                    "url": "https://api.example.com/data",
                    "method": "GET"
                }
            }
        ],
        "tags": ["test", "api"],
        "timeout_minutes": 30
    }
    
    try:
        response = requests.post(f"{BASE_URL}/workflows", json=workflow_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            workflow = response.json()
            print(f"   Created workflow: {workflow['workflow_id']}")
            workflow_id = workflow['workflow_id']
            
            # Test 3: Get the specific workflow
            print(f"\n3. Testing GET /workflows/{workflow_id}")
            response = requests.get(f"{BASE_URL}/workflows/{workflow_id}")
            print(f"   Status: {response.status_code}")
            print(f"   Workflow name: {response.json()['name']}")
            
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API test completed!")

if __name__ == "__main__":
    test_api()
