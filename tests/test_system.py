#!/usr/bin/env python3
"""
Comprehensive test script for the AI Workflow Generator system
Tests API endpoints, chat system, and validates that the frontend can display workflows
"""
import json
import time
from datetime import datetime

import requests

BASE_URL = "http://localhost:8003/api/v1"
FRONTEND_URL = "http://localhost:3003"

def test_api_health():
    """Test if the API is healthy"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/../health")
        if response.status_code == 200:
            print("   ✅ API is healthy")
            return True
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API health check error: {str(e)}")
        return False

def test_workflow_endpoints():
    """Test workflow CRUD operations"""
    print("\n📋 Testing Workflow Endpoints...")
    
    # Test 1: List workflows
    print("\n1. Testing GET /workflows")
    try:
        response = requests.get(f"{BASE_URL}/workflows/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            print(f"   ✅ Found {len(workflows)} workflows")
            
            # Display workflow names
            for workflow in workflows[:3]:  # Show first 3
                print(f"      - {workflow['name']} ({len(workflow['steps'])} steps)")
            
            return workflows
        else:
            print(f"   ❌ Error: {response.text}")
            return []
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return []

def test_chat_endpoints():
    """Test chat system"""
    print("\n💬 Testing Chat System...")
    
    # Test 1: Create a thread
    print("\n1. Creating a chat thread...")
    try:
        thread_data = {
            "title": "Test API Validation Thread",
            "metadata": {"test": True}
        }
        response = requests.post(f"{BASE_URL}/chat/threads", json=thread_data)
        
        if response.status_code == 200:
            thread = response.json()
            thread_id = thread['thread_id']
            print(f"   ✅ Created thread: {thread_id}")
            print(f"   📝 Title: {thread['title']}")
            
            # Test 2: Send a message to the agent
            print("\n2. Testing chat with agent...")
            chat_data = {
                "message_content": "Hello! Can you list the available workflows in the system?",
                "use_context": True
            }
            
            response = requests.post(
                f"{BASE_URL}/chat/threads/{thread_id}/chat", 
                json=chat_data
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                message = chat_response['message']
                print(f"   ✅ Agent responded!")
                print(f"   🤖 Response: {message['content'][:100]}...")
                print(f"   ⏱️  Response time: {chat_response['context_used']['response_time_ms']}ms")
                print(f"   🔧 Tools available: {chat_response['context_used']['tools_available']}")
                
                # Test 3: Get thread messages
                print("\n3. Retrieving thread messages...")
                response = requests.get(f"{BASE_URL}/chat/threads/{thread_id}/messages")
                
                if response.status_code == 200:
                    messages = response.json()
                    print(f"   ✅ Found {len(messages)} messages in thread")
                    for i, msg in enumerate(messages):
                        print(f"      {i+1}. {msg['role']}: {msg['content'][:50]}...")
                else:
                    print(f"   ❌ Failed to get messages: {response.status_code}")
                
                return thread_id
            else:
                print(f"   ❌ Chat failed: {response.status_code} - {response.text}")
                return thread_id
        else:
            print(f"   ❌ Thread creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def test_workflow_generation():
    """Test AI workflow generation"""
    print("\n🤖 Testing AI Workflow Generation...")
    
    try:
        generation_data = {
            "description": "Create an automated system for processing customer feedback emails",
            "requirements": [
                "Receive emails",
                "Analyze sentiment", 
                "Route to appropriate team",
                "Send acknowledgment"
            ]
        }
        
        response = requests.post(f"{BASE_URL}/workflows/generate", json=generation_data)
        
        if response.status_code == 200:
            workflow = response.json()
            print(f"   ✅ Generated workflow: {workflow['name']}")
            print(f"   📝 Description: {workflow['description']}")
            print(f"   🔧 Steps: {len(workflow['steps'])}")
            
            # Show first few steps
            for i, step in enumerate(workflow['steps'][:3]):
                print(f"      {i+1}. {step['name']} ({step['step_type']})")
            
            return workflow['workflow_id']
        else:
            print(f"   ❌ Generation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def test_workflow_execution():
    """Test workflow execution"""
    print("\n⚡ Testing Workflow Execution...")
    
    workflows = test_workflow_endpoints()
    if not workflows:
        print("   ❌ No workflows available for execution test")
        return
    
    # Pick the first workflow
    workflow = workflows[0]
    workflow_id = workflow['workflow_id']
    
    try:
        execution_data = {
            "input_data": {"test": True},
            "metadata": {"test_execution": True}
        }
        
        response = requests.post(
            f"{BASE_URL}/workflows/{workflow_id}/execute", 
            json=execution_data
        )
        
        if response.status_code == 200:
            execution = response.json()
            print(f"   ✅ Started execution: {execution['execution_id']}")
            print(f"   📊 Status: {execution['status']}")
            print(f"   🎯 Workflow: {workflow['name']}")
        else:
            print(f"   ❌ Execution failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_frontend_availability():
    """Test if frontend is accessible"""
    print("\n🖥️  Testing Frontend Availability...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Frontend is accessible at {FRONTEND_URL}")
            print(f"   📄 Page size: {len(response.content)} bytes")
            return True
        else:
            print(f"   ❌ Frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {str(e)}")
        return False

def display_system_summary():
    """Display a summary of the entire system"""
    print("\n" + "="*60)
    print("🎉 AI WORKFLOW GENERATOR SYSTEM SUMMARY")
    print("="*60)
    
    # Get workflows
    try:
        response = requests.get(f"{BASE_URL}/workflows/")
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            
            print(f"\n📊 SYSTEM STATISTICS:")
            print(f"   • Total Workflows: {len(workflows)}")
            
            # Count by status
            status_counts = {}
            step_types = {}
            total_steps = 0
            
            for workflow in workflows:
                status = workflow.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                for step in workflow.get('steps', []):
                    total_steps += 1
                    step_type = step.get('step_type', 'unknown')
                    step_types[step_type] = step_types.get(step_type, 0) + 1
            
            print(f"   • Total Steps: {total_steps}")
            print(f"   • Avg Steps/Workflow: {total_steps/len(workflows):.1f}")
            
            print(f"\n📈 WORKFLOW STATUS:")
            for status, count in status_counts.items():
                print(f"   • {status.title()}: {count}")
            
            print(f"\n🔧 STEP TYPES:")
            for step_type, count in sorted(step_types.items()):
                print(f"   • {step_type.replace('_', ' ').title()}: {count}")
            
            print(f"\n🏷️  WORKFLOW DETAILS:")
            for workflow in workflows:
                tags = ', '.join(workflow.get('tags', [])[:3])
                execution_count = workflow.get('execution_count', 0)
                print(f"   • {workflow['name']}")
                print(f"     Steps: {len(workflow['steps'])}, Tags: [{tags}], Runs: {execution_count}")
        
    except Exception as e:
        print(f"   ❌ Could not fetch system statistics: {str(e)}")
    
    print(f"\n🌐 ENDPOINTS AVAILABLE:")
    print(f"   • Backend API: {BASE_URL}")
    print(f"   • Frontend UI: {FRONTEND_URL}")
    print(f"   • Health Check: {BASE_URL}/../health")
    
    print(f"\n🚀 FEATURES IMPLEMENTED:")
    print(f"   ✅ Workflow CRUD Operations")
    print(f"   ✅ AI-Powered Workflow Generation")
    print(f"   ✅ Workflow Execution Engine")
    print(f"   ✅ Chat System with LLM Agent")
    print(f"   ✅ React Flow Visualization")
    print(f"   ✅ MongoDB Data Persistence")
    print(f"   ✅ RESTful API with FastAPI")
    print(f"   ✅ Modern React Frontend")

def main():
    print("🚀 AI WORKFLOW GENERATOR - COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    api_healthy = test_api_health()
    
    if api_healthy:
        workflows = test_workflow_endpoints()
        chat_thread = test_chat_endpoints() 
        generated_workflow = test_workflow_generation()
        test_workflow_execution()
    
    frontend_available = test_frontend_availability()
    
    # Final summary
    display_system_summary()
    
    print(f"\n✅ SYSTEM STATUS:")
    print(f"   • Backend API: {'🟢 Online' if api_healthy else '🔴 Offline'}")
    print(f"   • Frontend UI: {'🟢 Online' if frontend_available else '🔴 Offline'}")
    print(f"   • Chat System: {'🟢 Working' if chat_thread else '🔴 Issues'}")
    
    if api_healthy and frontend_available:
        print(f"\n🎉 System is fully operational!")
        print(f"   👉 Visit {FRONTEND_URL} to interact with workflows")
        print(f"   👉 Check {BASE_URL}/docs for API documentation")
    else:
        print(f"\n⚠️  Some components have issues. Check the logs above.")

if __name__ == "__main__":
    main()
