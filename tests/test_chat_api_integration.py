#!/usr/bin/env python3
"""
Integration tests for Chat API endpoints
"""
import asyncio
from datetime import datetime
from typing import Any, Dict

import httpx
import pytest

# Test configuration
BASE_URL = "http://localhost:8004"
API_BASE = f"{BASE_URL}/api/v1"
CHAT_BASE = f"{API_BASE}/chat"


class TestChatAPIIntegration:
    """Integration tests for Chat API endpoints"""
    
    @pytest.fixture
    def client(self):
        """HTTP client for API testing"""
        return httpx.AsyncClient(timeout=10.0)
    
    @pytest.fixture
    def test_thread_data(self):
        """Sample thread data for testing"""
        return {
            "title": "Integration Test Thread",
            "initial_message": "Hello, I need help with workflow automation."
        }
    
    @pytest.fixture
    def test_message_data(self):
        """Sample message data for testing"""
        return {
            "content": "This is a test message from the integration tests.",
            "is_user": True
        }
    
    @pytest.mark.asyncio
    async def test_backend_health(self, client):
        """Test if backend is accessible"""
        try:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
        except httpx.ConnectError:
            pytest.skip("Backend not accessible. Skipping integration tests.")
    
    @pytest.mark.asyncio
    async def test_create_thread_endpoint(self, client, test_thread_data):
        """Test POST /chat/threads endpoint"""
        response = await client.post(
            f"{CHAT_BASE}/threads",
            json=test_thread_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["title"] == test_thread_data["title"]
        assert "created_at" in data
        assert "updated_at" in data
        
        return data["id"]  # Return for use in other tests
    
    @pytest.mark.asyncio
    async def test_get_thread_endpoint(self, client, test_thread_data):
        """Test GET /chat/threads/{thread_id} endpoint"""
        # First create a thread
        create_response = await client.post(
            f"{CHAT_BASE}/threads",
            json=test_thread_data
        )
        assert create_response.status_code == 200
        thread_id = create_response.json()["id"]
        
        # Then get it
        response = await client.get(f"{CHAT_BASE}/threads/{thread_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == thread_id
        assert data["title"] == test_thread_data["title"]
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_thread(self, client):
        """Test GET /chat/threads/{thread_id} with invalid ID"""
        from bson import ObjectId
        fake_id = str(ObjectId())
        
        response = await client.get(f"{CHAT_BASE}/threads/{fake_id}")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_threads_endpoint(self, client, test_thread_data):
        """Test GET /chat/threads endpoint"""
        # Create a few threads first
        for i in range(3):
            thread_data = {
                "title": f"Test Thread {i+1}",
                "initial_message": f"Initial message {i+1}"
            }
            await client.post(f"{CHAT_BASE}/threads", json=thread_data)
        
        # List threads
        response = await client.get(f"{CHAT_BASE}/threads")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "threads" in data
        assert "total" in data
        assert isinstance(data["threads"], list)
        assert data["total"] >= 3  # At least the ones we created
    
    @pytest.mark.asyncio
    async def test_list_threads_pagination(self, client):
        """Test pagination in list threads endpoint"""
        response = await client.get(f"{CHAT_BASE}/threads?skip=0&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["threads"]) <= 2
        assert "total" in data
    
    @pytest.mark.asyncio
    async def test_add_message_endpoint(self, client, test_thread_data, test_message_data):
        """Test POST /chat/threads/{thread_id}/messages endpoint"""
        # Create a thread first
        create_response = await client.post(
            f"{CHAT_BASE}/threads",
            json=test_thread_data
        )
        thread_id = create_response.json()["id"]
        
        # Add a message
        response = await client.post(
            f"{CHAT_BASE}/threads/{thread_id}/messages",
            json=test_message_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["content"] == test_message_data["content"]
        assert data["is_user"] == test_message_data["is_user"]
        assert data["thread_id"] == thread_id
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_get_messages_endpoint(self, client, test_thread_data):
        """Test GET /chat/threads/{thread_id}/messages endpoint"""
        # Create a thread
        create_response = await client.post(
            f"{CHAT_BASE}/threads",
            json=test_thread_data
        )
        thread_id = create_response.json()["id"]
        
        # Add some messages
        messages = [
            {"content": "First message", "is_user": True},
            {"content": "Second message", "is_user": False},
            {"content": "Third message", "is_user": True}
        ]
        
        for msg in messages:
            await client.post(
                f"{CHAT_BASE}/threads/{thread_id}/messages",
                json=msg
            )
        
        # Get messages
        response = await client.get(f"{CHAT_BASE}/threads/{thread_id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "messages" in data
        assert "total" in data
        assert len(data["messages"]) >= 3  # At least the ones we added
    
    @pytest.mark.asyncio
    async def test_delete_thread_endpoint(self, client, test_thread_data):
        """Test DELETE /chat/threads/{thread_id} endpoint"""
        # Create a thread
        create_response = await client.post(
            f"{CHAT_BASE}/threads",
            json=test_thread_data
        )
        thread_id = create_response.json()["id"]
        
        # Add a message to it
        await client.post(
            f"{CHAT_BASE}/threads/{thread_id}/messages",
            json={"content": "Test message", "is_user": True}
        )
        
        # Delete the thread
        response = await client.delete(f"{CHAT_BASE}/threads/{thread_id}")
        
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = await client.get(f"{CHAT_BASE}/threads/{thread_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_chat_agent_endpoint(self, client, test_thread_data):
        """Test POST /chat/send endpoint (agent interaction)"""
        # Create a thread
        create_response = await client.post(
            f"{CHAT_BASE}/threads",
            json=test_thread_data
        )
        thread_id = create_response.json()["id"]
        
        # Send a message to the agent
        agent_request = {
            "thread_id": thread_id,
            "message": "Can you help me create a simple workflow?"
        }
        
        response = await client.post(
            f"{CHAT_BASE}/send",
            json=agent_request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_message" in data
        assert "agent_response" in data
        assert data["user_message"]["content"] == agent_request["message"]
        assert data["user_message"]["is_user"] is True
        assert data["agent_response"]["is_user"] is False
        assert len(data["agent_response"]["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, client):
        """Test a complete conversation flow"""
        # 1. Create a thread
        thread_data = {
            "title": "Full Conversation Test",
            "initial_message": "I want to automate my email marketing"
        }
        
        create_response = await client.post(f"{CHAT_BASE}/threads", json=thread_data)
        thread_id = create_response.json()["id"]
        
        # 2. Have a conversation
        conversation = [
            "Can you help me create an email marketing workflow?",
            "What are the key steps I should include?",
            "How can I personalize the emails?"
        ]
        
        for message in conversation:
            # Send message to agent
            agent_request = {"thread_id": thread_id, "message": message}
            response = await client.post(f"{CHAT_BASE}/send", json=agent_request)
            assert response.status_code == 200
            
            # Verify response
            data = response.json()
            assert data["user_message"]["content"] == message
            assert len(data["agent_response"]["content"]) > 0
        
        # 3. Get all messages
        messages_response = await client.get(f"{CHAT_BASE}/threads/{thread_id}/messages")
        messages_data = messages_response.json()
        
        # Should have initial message + 3 user messages + 3 agent responses = 7 total
        assert len(messages_data["messages"]) >= 7
        
        # 4. List threads (should include our test thread)
        threads_response = await client.get(f"{CHAT_BASE}/threads")
        threads_data = threads_response.json()
        
        thread_ids = [t["id"] for t in threads_data["threads"]]
        assert thread_id in thread_ids


class TestChatAPIErrorHandling:
    """Test error handling in Chat API"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(timeout=10.0)
    
    @pytest.mark.asyncio
    async def test_invalid_thread_id_format(self, client):
        """Test with malformed thread ID"""
        response = await client.get(f"{CHAT_BASE}/threads/invalid-id")
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_empty_thread_title(self, client):
        """Test creating thread with empty title"""
        thread_data = {"title": "", "initial_message": "Test"}
        
        response = await client.post(f"{CHAT_BASE}/threads", json=thread_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_empty_message_content(self, client):
        """Test adding empty message"""
        # First create a valid thread
        thread_data = {"title": "Test Thread", "initial_message": "Test"}
        create_response = await client.post(f"{CHAT_BASE}/threads", json=thread_data)
        thread_id = create_response.json()["id"]
        
        # Try to add empty message
        message_data = {"content": "", "is_user": True}
        response = await client.post(
            f"{CHAT_BASE}/threads/{thread_id}/messages",
            json=message_data
        )
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """Test requests with missing required fields"""
        # Missing title in thread creation
        response = await client.post(f"{CHAT_BASE}/threads", json={})
        assert response.status_code == 422
        
        # Missing content in message
        thread_data = {"title": "Test Thread", "initial_message": "Test"}
        create_response = await client.post(f"{CHAT_BASE}/threads", json=thread_data)
        thread_id = create_response.json()["id"]
        
        response = await client.post(
            f"{CHAT_BASE}/threads/{thread_id}/messages",
            json={"is_user": True}  # Missing content
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent API operations"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Create multiple threads concurrently
        tasks = []
        for i in range(5):
            thread_data = {
                "title": f"Concurrent Thread {i}",
                "initial_message": f"Message {i}"
            }
            task = client.post(f"{CHAT_BASE}/threads", json=thread_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) == 5
        
        for response in successful_responses:
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
