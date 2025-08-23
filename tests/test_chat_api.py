#!/usr/bin/env python3
"""
Comprehensive unit and integration tests for Chat and Thread APIs
"""
import json
import requests
from datetime import datetime
import uuid
import time

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


def run_simple_workflow_test():
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
    workflow_test = run_simple_workflow_test()
    
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
            
            # Test 2: Get the thread
            print(f"\n2. Testing GET /chat/threads/{thread_id}")
            response = requests.get(f"{CHAT_URL}/threads/{thread_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Thread title: {response.json()['title']}")
            
            # Test 3: Create a user message
            print(f"\n3. Testing POST /chat/threads/{thread_id}/messages")
            message_data = {
                "content": "Hello, I need help creating a workflow",
                "role": "user"
            }
            
            response = requests.post(f"{CHAT_URL}/threads/{thread_id}/messages", json=message_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                message = response.json()
                print(f"   Created message: {message['message_id']}")
                print(f"   Message content: {message['content']}")
            
            # Test 4: Chat with the agent
            print(f"\n4. Testing POST /chat/threads/{thread_id}/chat")
            chat_request = {
                "message_content": "Can you help me create a workflow for sending daily email reports?",
                "use_context": True
            }
            
            # Convert to query params since it's not expecting JSON body
            response = requests.post(
                f"{CHAT_URL}/threads/{thread_id}/chat",
                params={
                    "message_content": chat_request["message_content"],
                    "use_context": chat_request["use_context"]
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                chat_response = response.json()
                print(f"   Agent response: {chat_response['message']['content'][:100]}...")
                print(f"   Response time: {chat_response.get('context_used', {}).get('response_time_ms', 'N/A')}ms")
            else:
                print(f"   Error: {response.text}")
            
            # Test 5: Get thread messages
            print(f"\n5. Testing GET /chat/threads/{thread_id}/messages")
            response = requests.get(f"{CHAT_URL}/threads/{thread_id}/messages")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                print(f"   Total messages: {len(messages)}")
                for i, msg in enumerate(messages):
                    print(f"   {i+1}. {msg['role']}: {msg['content'][:50]}...")
            
            # Test 6: Generate thread title
            print(f"\n6. Testing POST /chat/threads/{thread_id}/generate-title")
            response = requests.post(f"{CHAT_URL}/threads/{thread_id}/generate-title")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                title_response = response.json()
                print(f"   Generated title: {title_response.get('title', 'N/A')}")
            
            # Test 7: Get thread stats
            print(f"\n7. Testing GET /chat/threads/{thread_id}/stats")
            response = requests.get(f"{CHAT_URL}/threads/{thread_id}/stats")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"   Message count: {stats['message_count']}")
                print(f"   Role distribution: {stats['role_distribution']}")
                print(f"   Total tokens used: {stats['total_tokens_used']}")
            
        else:
            print(f"   Error creating thread: {response.json()}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: List all threads
    print("\n8. Testing GET /chat/threads")
    try:
        response = requests.get(f"{CHAT_URL}/threads")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            threads = response.json()
            print(f"   Total threads: {len(threads)}")
            for thread in threads[:3]:  # Show first 3
                print(f"   - {thread['thread_id']}: {thread.get('title', 'No title')}")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 9: Get agent config
    print("\n9. Testing GET /chat/agent/config")
    try:
        response = requests.get(f"{CHAT_URL}/agent/config")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"   System prompt length: {len(config['system_prompt'])}")
            print(f"   Max tokens: {config['max_tokens']}")
            print(f"   Temperature: {config['temperature']}")
            print(f"   Workflow tools enabled: {config['enable_workflow_tools']}")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Chat API test completed!")

def test_chat_conversation():
    """Test a longer conversation flow"""
    print("\n🗣️  Testing Chat Conversation Flow...")
    
    # Create a new thread for this test
    thread_data = {"title": "Conversation Test"}
    response = requests.post(f"{CHAT_URL}/threads", json=thread_data)
    
    if response.status_code != 200:
        print("Failed to create thread for conversation test")
        return
    
    thread_id = response.json()['thread_id']
    print(f"Created conversation thread: {thread_id}")
    
    # Series of messages to test conversation flow
    messages = [
        "Hi there! I'm new to workflow automation.",
        "Can you explain what workflows are?", 
        "How would I create a workflow to backup files daily?",
        "What about sending email notifications?",
        "Thanks for the help!"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n   Message {i}: {message}")
        
        try:
            response = requests.post(
                f"{CHAT_URL}/threads/{thread_id}/chat",
                params={"message_content": message, "use_context": True}
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                agent_message = chat_response['message']['content']
                print(f"   Agent: {agent_message[:100]}...")
                
                # Small delay to make it feel more natural
                time.sleep(0.5)
            else:
                print(f"   Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"\n✅ Conversation test completed for thread {thread_id}")

if __name__ == "__main__":
    test_chat_api()
    test_chat_conversation()
