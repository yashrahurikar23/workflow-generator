#!/usr/bin/env python3
"""
Quick test script to verify backend connectivity and create sample workflows
"""
import json

import requests


# Test API connectivity
def test_backend():
    base_url = "http://localhost:8004"
    
    print("🔍 Testing Backend Connectivity")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test workflows endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/workflows/", timeout=5)
        print(f"✅ Workflows endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Found {data.get('total', 0)} workflows")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Workflows endpoint failed: {e}")
    
    # Test docs endpoint
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Docs endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Docs endpoint failed: {e}")

# Create a simple test workflow
def create_test_workflow():
    base_url = "http://localhost:8004"
    
    workflow_data = {
        "name": "Simple Test Workflow",
        "description": "A basic workflow for testing the API",
        "steps": [
            {
                "step_id": "step1",
                "name": "Start Process",
                "step_type": "manual",
                "description": "Initial step to start the workflow",
                "depends_on": [],
                "config": {"action": "start"}
            },
            {
                "step_id": "step2", 
                "name": "Process Data",
                "step_type": "data_transform",
                "description": "Transform the input data",
                "depends_on": ["step1"],
                "config": {"operation": "transform"}
            }
        ],
        "tags": ["test", "simple"],
        "parallel_execution": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/workflows/",
            json=workflow_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"\n🚀 Creating test workflow...")
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created workflow: {result.get('workflow_id')}")
            return result
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 Backend Test Suite")
    print("=" * 50)
    
    # Test backend connectivity
    test_backend()
    
    # Create a test workflow
    create_test_workflow()
    
    print("\n🎯 Test complete!")
