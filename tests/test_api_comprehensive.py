#!/usr/bin/env python3
"""
Comprehensive unit and integration tests for Chat and Thread APIs
"""
import json
import time

import requests

# Test configuration
BASE_URL = "http://localhost:8004"
API_BASE = f"{BASE_URL}/api/v1"
CHAT_BASE = f"{API_BASE}/chat"

class TestChatAPI:
    """Integration tests for Chat API endpoints"""
    
    def __init__(self):
        self.test_thread_id = None
        self.test_message_ids = []
    
    def test_backend_connectivity(self):
        """Test if backend is accessible"""
        print("\n🔍 Testing Backend Connectivity")
        print("=" * 50)
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            print(f"Health endpoint status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Backend connectivity failed: {e}")
            return False
    
    def test_create_thread(self):
        """Test thread creation endpoint"""
        print("\n📝 Testing Thread Creation")
        print("-" * 30)
        
        thread_data = {
            "title": "Test Chat Thread",
            "initial_message": "Hello, I need help with workflow automation."
        }
        
        try:
            response = requests.post(
                f"{CHAT_BASE}/threads",
                json=thread_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 201:
                thread = response.json()
                self.test_thread_id = thread["thread_id"]
                
                print(f"✅ Thread created: {self.test_thread_id}")
                print(f"   Title: {thread.get('title', 'N/A')}")
                return thread
            else:
                print(f"❌ Thread creation failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Thread creation error: {e}")
            return None
    
    def test_send_message(self):
        """Test sending a message to a thread"""
        if not self.test_thread_id:
            print("❌ No thread ID available for testing")
            return None
            
        print(f"\n💬 Testing Send Message")
        print("-" * 25)
        
        message_data = {
            "content": "Can you help me create a workflow for email marketing?",
            "role": "user"
        }
        
        try:
            response = requests.post(
                f"{CHAT_BASE}/threads/{self.test_thread_id}/chat",
                json=message_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                chat_response = response.json()
                print(f"✅ Message sent successfully")
                return chat_response
            else:
                print(f"❌ Send message failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return None
    
    def test_get_messages(self):
        """Test retrieving messages from a thread"""
        if not self.test_thread_id:
            print("❌ No thread ID available for testing")
            return None
            
        print(f"\n📋 Testing Get Messages")
        print("-" * 25)
        
        try:
            response = requests.get(
                f"{CHAT_BASE}/threads/{self.test_thread_id}/messages",
                timeout=5
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                messages_response = response.json()
                messages = messages_response.get("messages", [])
                print(f"✅ Retrieved {len(messages)} messages")
                return messages_response
            else:
                print(f"❌ Get messages failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Get messages error: {e}")
            return None
    
    def test_list_threads(self):
        """Test listing all threads"""
        print(f"\n📑 Testing List Threads")
        print("-" * 25)
        
        try:
            response = requests.get(f"{CHAT_BASE}/threads", timeout=5)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                threads_response = response.json()
                threads = threads_response.get("threads", [])
                print(f"✅ Found {len(threads)} threads")
                return threads_response
            else:
                print(f"❌ List threads failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ List threads error: {e}")
            return None
    
    def run_all_tests(self):
        """Run all chat API tests"""
        print("🧪 CHAT API INTEGRATION TESTS")
        print("=" * 50)
        
        # Check backend connectivity first
        if not self.test_backend_connectivity():
            print("❌ Backend not accessible. Tests cannot continue.")
            return False
        
        # Run tests in sequence
        results = {}
        results["connectivity"] = True
        results["create_thread"] = self.test_create_thread() is not None
        results["send_message"] = self.test_send_message() is not None
        results["get_messages"] = self.test_get_messages() is not None
        results["list_threads"] = self.test_list_threads() is not None
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 30)
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        return passed == total


def run_workflow_test():
    """Test workflow endpoints"""
    print("\n🔄 Testing Workflow Endpoints")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE}/workflows/", timeout=5)
        print(f"Workflows endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total', 0)} workflows")
            return True
        else:
            print(f"❌ Workflows endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Workflows test error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 STARTING API TESTS")
    print("=" * 50)
    
    # Test workflows first
    workflow_test = run_workflow_test()
    
    # Test chat API
    chat_tester = TestChatAPI()
    chat_test = chat_tester.run_all_tests()
    
    # Final summary
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 20)
    print(f"Workflow Tests: {'✅ PASS' if workflow_test else '❌ FAIL'}")
    print(f"Chat Tests: {'✅ PASS' if chat_test else '❌ FAIL'}")
    
    if workflow_test and chat_test:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("\nNote: Backend connectivity issues may cause test failures.")
        print("Make sure the backend server is running on port 8004.")
