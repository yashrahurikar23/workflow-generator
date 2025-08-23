"""
Test script for the enhanced visual workflow system
"""
import asyncio
import json
from datetime import datetime

import requests

# Test configuration
BACKEND_URL = "http://localhost:8000"
VISUAL_WORKFLOW_API = f"{BACKEND_URL}/api/v1/visual-workflows"

async def test_node_types_api():
    """Test node types and categories API"""
    print("🧪 Testing Node Types API...")
    
    try:
        # Test get all node types
        response = requests.get(f"{VISUAL_WORKFLOW_API}/node-types")
        if response.status_code == 200:
            node_types = response.json()
            print(f"✅ Found {len(node_types)} node types")
            
            # Show sample node types
            for node_type in node_types[:3]:
                print(f"   - {node_type['name']} ({node_type['category']})")
        else:
            print(f"❌ Failed to get node types: {response.status_code}")
        
        # Test get categories
        response = requests.get(f"{VISUAL_WORKFLOW_API}/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories")
            
            for category in categories:
                print(f"   - {category['name']}: {category['description']}")
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing node types API: {str(e)}")

async def test_create_visual_workflow():
    """Test creating a visual workflow"""
    print("\n🧪 Testing Visual Workflow Creation...")
    
    # Sample visual workflow
    workflow_data = {
        "name": "AI Content Analysis Pipeline",
        "description": "Analyze content using AI and data transformation",
        "workflow_type": "visual",
        "visual_data": {
            "nodes": [
                {
                    "node_id": "trigger-1",
                    "node_type_id": "manual_trigger",
                    "name": "Content Input",
                    "position": {"x": 100, "y": 100},
                    "config": {
                        "name": "Start Analysis"
                    }
                },
                {
                    "node_id": "ai-1",
                    "node_type_id": "ai_model",
                    "name": "AI Content Analyzer",
                    "position": {"x": 400, "y": 100},
                    "config": {
                        "provider": "OpenAI",
                        "model": "gpt-4",
                        "prompt": "Analyze the following content for sentiment and key topics:",
                        "temperature": 0.5
                    }
                },
                {
                    "node_id": "transform-1",
                    "node_type_id": "data_transformer",
                    "name": "Format Results",
                    "position": {"x": 700, "y": 100},
                    "config": {
                        "operation": "map",
                        "expression": "result => ({ analysis: result, timestamp: new Date().toISOString() })"
                    }
                }
            ],
            "connections": [
                {
                    "connection_id": "conn-1",
                    "source_node_id": "trigger-1",
                    "target_node_id": "ai-1",
                    "source_output": "triggered",
                    "target_input": "text"
                },
                {
                    "connection_id": "conn-2",
                    "source_node_id": "ai-1",
                    "target_node_id": "transform-1",
                    "source_output": "response",
                    "target_input": "data"
                }
            ]
        },
        "tags": ["ai", "analysis", "test"],
        "status": "active"
    }
    
    try:
        response = requests.post(
            f"{VISUAL_WORKFLOW_API}/visual-workflows",
            json=workflow_data
        )
        
        if response.status_code == 201:
            workflow = response.json()
            workflow_id = workflow["workflow_id"]
            print(f"✅ Created visual workflow: {workflow_id}")
            print(f"   Name: {workflow['name']}")
            print(f"   Nodes: {len(workflow['visual_data']['nodes'])}")
            print(f"   Connections: {len(workflow['visual_data']['connections'])}")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating visual workflow: {str(e)}")
        return None

async def test_workflow_execution(workflow_id: str):
    """Test workflow execution"""
    print(f"\n🧪 Testing Workflow Execution for {workflow_id}...")
    
    try:
        # Test single node execution first
        print("   Testing single node execution...")
        
        response = requests.post(
            f"{VISUAL_WORKFLOW_API}/visual-workflows/{workflow_id}/nodes/ai-1/execute",
            json={"text": "This is a test content for AI analysis."}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Node execution successful")
            print(f"   Node: {result['node_id']}")
            print(f"   Status: {result['status']}")
            if 'result' in result:
                print(f"   Result type: {type(result['result'])}")
        else:
            print(f"❌ Node execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test full workflow execution
        print("   Testing full workflow execution...")
        
        response = requests.post(
            f"{VISUAL_WORKFLOW_API}/visual-workflows/{workflow_id}/execute",
            json={"input_text": "Sample content to analyze with the AI pipeline."}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow execution successful")
            print(f"   Execution ID: {result['execution_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Duration: {result['duration']} seconds")
            print(f"   Nodes executed: {len(result['node_results'])}")
            return result['execution_id']
        else:
            print(f"❌ Workflow execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing workflow execution: {str(e)}")
        return None

async def test_workflow_conversion(workflow_id: str):
    """Test workflow conversion to LlamaIndex format"""
    print(f"\n🧪 Testing Workflow Conversion for {workflow_id}...")
    
    try:
        response = requests.post(
            f"{VISUAL_WORKFLOW_API}/visual-workflows/{workflow_id}/convert-to-llamaindex"
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow conversion successful")
            
            llamaindex_workflow = result["llamaindex_workflow"]
            print(f"   Workflow name: {llamaindex_workflow['workflow_name']}")
            print(f"   Steps: {len(llamaindex_workflow['steps'])}")
            print(f"   Connections: {len(llamaindex_workflow['connections'])}")
            
            # Show step details
            for step in llamaindex_workflow['steps']:
                print(f"   - Step: {step['name']} ({step['step_type']})")
                print(f"     Dependencies: {step['depends_on']}")
            
            return result
        else:
            print(f"❌ Workflow conversion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing workflow conversion: {str(e)}")
        return None

async def test_execution_status(execution_id: str):
    """Test execution status retrieval"""
    print(f"\n🧪 Testing Execution Status for {execution_id}...")
    
    try:
        response = requests.get(f"{VISUAL_WORKFLOW_API}/executions/{execution_id}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Retrieved execution status")
            print(f"   Status: {status['status']}")
            print(f"   Duration: {status['duration']} seconds")
            print(f"   Execution log entries: {len(status['execution_log'])}")
            
            # Show execution log
            for log_entry in status['execution_log'][-3:]:  # Show last 3 entries
                print(f"   - {log_entry['timestamp']}: {log_entry['node_id']} -> {log_entry['status']}")
            
            return status
        else:
            print(f"❌ Failed to get execution status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting execution status: {str(e)}")
        return None

async def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Visual Workflow Test Suite")
    print("=" * 60)
    
    # Test 1: Node Types API
    await test_node_types_api()
    
    # Test 2: Create Visual Workflow
    workflow_id = await test_create_visual_workflow()
    
    if workflow_id:
        # Test 3: Execute Workflow
        execution_id = await test_workflow_execution(workflow_id)
        
        # Test 4: Convert to LlamaIndex
        await test_workflow_conversion(workflow_id)
        
        # Test 5: Check Execution Status
        if execution_id:
            await test_execution_status(execution_id)
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Complete!")

def test_frontend_components():
    """Test frontend component structure"""
    print("\n🧪 Testing Frontend Component Structure...")
    
    import os
    
    frontend_dir = "frontend/src"
    required_components = [
        "components/NodePalette.tsx",
        "components/NodeConfigPanel.tsx", 
        "components/CustomNodes.tsx",
        "components/WorkflowVisualization.tsx",
        "App.tsx"
    ]
    
    for component in required_components:
        component_path = os.path.join(frontend_dir, component)
        if os.path.exists(component_path):
            print(f"✅ {component} exists")
            
            # Check file size to ensure it's not empty
            size = os.path.getsize(component_path)
            if size > 1000:  # At least 1KB
                print(f"   Size: {size} bytes (Good)")
            else:
                print(f"   Size: {size} bytes (Small - check content)")
        else:
            print(f"❌ {component} missing")

if __name__ == "__main__":
    print("🧪 Visual Workflow System Test Suite")
    print("Testing frontend components first...")
    
    # Test frontend components
    test_frontend_components()
    
    print("\nTo test the backend APIs, start the backend server first:")
    print("cd backend && uvicorn app.main:app --reload")
    print("\nThen run the API tests:")
    print("python test_visual_workflows.py --api-tests")
    
    import sys
    if "--api-tests" in sys.argv:
        print("\n🚀 Running API Tests...")
        asyncio.run(run_comprehensive_test())
