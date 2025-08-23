#!/usr/bin/env python3
"""
Simple status check script for the chat and workflow APIs
"""
import json
from datetime import datetime

import requests

BASE_URL = "http://localhost:8004"
API_BASE = f"{BASE_URL}/api/v1"

def check_backend_status():
    """Check if backend is running"""
    print("🔍 Checking backend status...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"⚠️ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def check_workflows():
    """Check workflow endpoints"""
    print("\n📊 Checking workflow endpoints...")
    try:
        response = requests.get(f"{API_BASE}/workflows", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Workflows endpoint working - Found {len(data)} workflows")
            return True
        else:
            print(f"❌ Workflows endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workflows check failed: {e}")
        return False

def check_chat_threads():
    """Check chat thread endpoints"""
    print("\n💬 Checking chat thread endpoints...")
    try:
        response = requests.get(f"{API_BASE}/chat/threads", timeout=5)
        if response.status_code == 200:
            data = response.json()
            threads = data.get("threads", [])
            print(f"✅ Chat threads endpoint working - Found {len(threads)} threads")
            return True
        else:
            print(f"❌ Chat threads endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat threads check failed: {e}")
        return False

def test_create_thread():
    """Test creating a new thread"""
    print("\n📝 Testing thread creation...")
    try:
        thread_data = {
            "title": "Test Thread for Status Check",
            "initial_message": "This is a test message to verify the API is working"
        }
        
        response = requests.post(
            f"{API_BASE}/chat/threads",
            json=thread_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            thread_id = data.get("id")
            print(f"✅ Thread creation successful - ID: {thread_id}")
            return thread_id
        else:
            print(f"❌ Thread creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Thread creation error: {e}")
        return None

def test_send_message(thread_id):
    """Test sending a message to the agent"""
    if not thread_id:
        print("⏭️ Skipping message test - no thread ID")
        return False
        
    print("\n🤖 Testing agent message...")
    try:
        message_data = {
            "thread_id": thread_id,
            "message": "Can you help me create a simple workflow for email automation?"
        }
        
        response = requests.post(
            f"{API_BASE}/chat/send",
            json=message_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            user_msg = data.get("user_message", {})
            agent_msg = data.get("agent_response", {})
            
            print(f"✅ Agent interaction successful")
            print(f"   User message recorded: {len(user_msg.get('content', ''))} chars")
            print(f"   Agent response: {len(agent_msg.get('content', ''))} chars")
            return True
        else:
            print(f"❌ Agent interaction failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Agent interaction error: {e}")
        return False

def main():
    print("🧪 API STATUS CHECK")
    print("=" * 40)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track test results
    results = {}
    
    # 1. Check backend
    results["backend"] = check_backend_status()
    
    if not results["backend"]:
        print("\n❌ Backend not running. Cannot proceed with API tests.")
        print("\n💡 To start the backend:")
        print("cd backend && uvicorn main:app --host 0.0.0.0 --port 8004")
        return
    
    # 2. Check workflows
    results["workflows"] = check_workflows()
    
    # 3. Check chat threads
    results["chat_threads"] = check_chat_threads()
    
    # 4. Test thread creation
    thread_id = test_create_thread()
    results["thread_creation"] = thread_id is not None
    
    # 5. Test agent interaction
    results["agent_interaction"] = test_send_message(thread_id)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 20)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ The chat and workflow APIs are working correctly")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("Some API endpoints may need attention")

if __name__ == "__main__":
    main()
