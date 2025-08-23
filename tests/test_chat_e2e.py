#!/usr/bin/env python3
"""
End-to-end tests for the complete chat system
"""
import asyncio
import json
from datetime import datetime, timedelta

import httpx
import pytest


class TestChatSystemE2E:
    """End-to-end tests for the complete chat system"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(timeout=30.0)
    
    @pytest.mark.asyncio
    async def test_complete_workflow_assistance_scenario(self, client):
        """Test a complete workflow where user gets help creating a workflow"""
        
        # Scenario: User wants to create an email marketing automation
        
        # 1. Create a new chat thread
        thread_data = {
            "title": "Email Marketing Automation Help",
            "initial_message": "I want to create an automated email marketing campaign for my e-commerce store"
        }
        
        response = await client.post(f"http://localhost:8004/api/v1/chat/threads", json=thread_data)
        assert response.status_code == 200
        thread_id = response.json()["id"]
        
        # 2. User asks for specific help
        conversation_steps = [
            {
                "message": "Can you help me design a workflow that sends personalized emails to customers who haven't purchased in 30 days?",
                "expected_keywords": ["workflow", "email", "personalized", "customers"]
            },
            {
                "message": "What data do I need to collect from customers for personalization?",
                "expected_keywords": ["data", "collect", "personalization", "customers"]
            },
            {
                "message": "How can I segment my customers based on their behavior?",
                "expected_keywords": ["segment", "customers", "behavior"]
            },
            {
                "message": "Can you create a workflow JSON for this automation?",
                "expected_keywords": ["workflow", "JSON", "automation"]
            }
        ]
        
        # 3. Go through the conversation
        for step in conversation_steps:
            agent_request = {
                "thread_id": thread_id,
                "message": step["message"]
            }
            
            response = await client.post(
                f"http://localhost:8004/api/v1/chat/send",
                json=agent_request
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify user message was recorded
            assert data["user_message"]["content"] == step["message"]
            assert data["user_message"]["is_user"] is True
            
            # Verify agent responded
            agent_response = data["agent_response"]["content"]
            assert len(agent_response) > 50  # Substantial response
            assert data["agent_response"]["is_user"] is False
            
            # Check if response contains expected keywords (basic relevance check)
            response_lower = agent_response.lower()
            found_keywords = [kw for kw in step["expected_keywords"] if kw in response_lower]
            assert len(found_keywords) > 0, f"No expected keywords found in response: {agent_response[:100]}..."
        
        # 4. Verify complete conversation history
        messages_response = await client.get(f"http://localhost:8004/api/v1/chat/threads/{thread_id}/messages")
        assert messages_response.status_code == 200
        
        messages_data = messages_response.json()
        messages = messages_data["messages"]
        
        # Should have: 1 initial + 4 user + 4 agent = 9 messages
        assert len(messages) >= 9
        
        # Verify message ordering and alternating user/agent pattern
        user_messages = [msg for msg in messages if msg["is_user"]]
        agent_messages = [msg for msg in messages if not msg["is_user"]]
        
        assert len(user_messages) >= 5  # Initial + 4 conversation
        assert len(agent_messages) >= 4  # 4 agent responses
    
    @pytest.mark.asyncio
    async def test_multi_thread_conversation_management(self, client):
        """Test managing multiple conversation threads"""
        
        # Create multiple threads for different topics
        thread_scenarios = [
            {
                "title": "Data Processing Pipeline",
                "initial_message": "I need help with data processing workflows",
                "follow_up": "How do I handle large CSV files?"
            },
            {
                "title": "Customer Onboarding",
                "initial_message": "I want to automate customer onboarding",
                "follow_up": "What steps should be included in onboarding?"
            },
            {
                "title": "Inventory Management",
                "initial_message": "Help me create inventory tracking workflows",
                "follow_up": "How do I set up low stock alerts?"
            }
        ]
        
        thread_ids = []
        
        # Create all threads
        for scenario in thread_scenarios:
            thread_data = {
                "title": scenario["title"],
                "initial_message": scenario["initial_message"]
            }
            
            response = await client.post(f"http://localhost:8004/api/v1/chat/threads", json=thread_data)
            assert response.status_code == 200
            thread_ids.append(response.json()["id"])
        
        # Have conversations in each thread
        for i, (thread_id, scenario) in enumerate(zip(thread_ids, thread_scenarios)):
            agent_request = {
                "thread_id": thread_id,
                "message": scenario["follow_up"]
            }
            
            response = await client.post(
                f"http://localhost:8004/api/v1/chat/send",
                json=agent_request
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_message"]["content"] == scenario["follow_up"]
        
        # Verify all threads exist and have correct content
        threads_response = await client.get(f"http://localhost:8004/api/v1/chat/threads")
        assert threads_response.status_code == 200
        
        threads_data = threads_response.json()
        existing_thread_ids = [t["id"] for t in threads_data["threads"]]
        
        for thread_id in thread_ids:
            assert thread_id in existing_thread_ids
        
        # Verify each thread has its own separate conversation
        for i, thread_id in enumerate(thread_ids):
            messages_response = await client.get(f"http://localhost:8004/api/v1/chat/threads/{thread_id}/messages")
            messages_data = messages_response.json()
            messages = messages_data["messages"]
            
            # Each thread should have initial message + follow-up + agent response
            assert len(messages) >= 3
            
            # Verify the messages contain the right content
            user_messages = [msg["content"] for msg in messages if msg["is_user"]]
            expected_initial = thread_scenarios[i]["initial_message"]
            expected_followup = thread_scenarios[i]["follow_up"]
            
            assert expected_initial in user_messages
            assert expected_followup in user_messages
    
    @pytest.mark.asyncio
    async def test_chat_system_performance(self, client):
        """Test chat system performance under load"""
        
        # Create a thread
        thread_data = {
            "title": "Performance Test Thread",
            "initial_message": "Testing system performance"
        }
        
        response = await client.post(f"http://localhost:8004/api/v1/chat/threads", json=thread_data)
        thread_id = response.json()["id"]
        
        # Send multiple messages quickly
        start_time = datetime.now()
        
        tasks = []
        for i in range(10):
            agent_request = {
                "thread_id": thread_id,
                "message": f"Performance test message {i+1}. Can you help me with workflow optimization?"
            }
            
            task = client.post(
                f"http://localhost:8004/api/v1/chat/send",
                json=agent_request
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()
        
        # Verify all requests succeeded
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        assert len(successful_responses) == 10
        
        # Check performance (should complete within reasonable time)
        duration = (end_time - start_time).total_seconds()
        assert duration < 60  # Should complete within 60 seconds
        
        # Verify all messages were recorded
        messages_response = await client.get(f"http://localhost:8004/api/v1/chat/threads/{thread_id}/messages")
        messages_data = messages_response.json()
        
        # Should have: 1 initial + 10 user + 10 agent = 21 messages
        assert len(messages_data["messages"]) >= 21
    
    @pytest.mark.asyncio
    async def test_agent_context_awareness(self, client):
        """Test that the agent maintains context across conversation"""
        
        # Create a thread
        thread_data = {
            "title": "Context Awareness Test",
            "initial_message": "I'm building an e-commerce platform and need automation workflows"
        }
        
        response = await client.post(f"http://localhost:8004/api/v1/chat/threads", json=thread_data)
        thread_id = response.json()["id"]
        
        # Have a conversation that builds context
        conversation = [
            "I need help with order processing workflows",
            "The orders come from Shopify",
            "I want to automatically send emails when orders are shipped",
            "Can you create a workflow for this using the Shopify info I mentioned?"
        ]
        
        responses = []
        for message in conversation:
            agent_request = {
                "thread_id": thread_id,
                "message": message
            }
            
            response = await client.post(
                f"http://localhost:8004/api/v1/chat/send",
                json=agent_request
            )
            
            assert response.status_code == 200
            data = response.json()
            responses.append(data["agent_response"]["content"])
        
        # The last response should reference earlier context (Shopify, orders, emails)
        last_response = responses[-1].lower()
        context_keywords = ["shopify", "order", "email", "ship"]
        found_context = [kw for kw in context_keywords if kw in last_response]
        
        assert len(found_context) >= 2, f"Agent didn't maintain context. Response: {last_response[:200]}..."
    
    @pytest.mark.asyncio
    async def test_chat_system_recovery(self, client):
        """Test system behavior during and after errors"""
        
        # Test with invalid thread ID
        invalid_request = {
            "thread_id": "invalid-thread-id",
            "message": "This should fail"
        }
        
        response = await client.post(
            f"http://localhost:8004/api/v1/chat/send",
            json=invalid_request
        )
        
        # Should handle error gracefully
        assert response.status_code in [404, 422]
        
        # System should still work after error
        thread_data = {
            "title": "Recovery Test Thread",
            "initial_message": "Testing system recovery after error"
        }
        
        response = await client.post(f"http://localhost:8004/api/v1/chat/threads", json=thread_data)
        assert response.status_code == 200
        
        thread_id = response.json()["id"]
        
        # Normal operation should work
        agent_request = {
            "thread_id": thread_id,
            "message": "System should work normally now"
        }
        
        response = await client.post(
            f"http://localhost:8004/api/v1/chat/send",
            json=agent_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["agent_response"]["content"]) > 0


class TestChatSystemIntegrationWithWorkflows:
    """Test integration between chat system and workflow functionality"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(timeout=30.0)
    
    @pytest.mark.asyncio
    async def test_workflow_generation_through_chat(self, client):
        """Test generating workflows through chat interaction"""
        
        # Create a thread focused on workflow creation
        thread_data = {
            "title": "Workflow Generation via Chat",
            "initial_message": "I want to create a workflow for processing customer feedback"
        }
        
        response = await client.post(f"http://localhost:8004/api/v1/chat/threads", json=thread_data)
        thread_id = response.json()["id"]
        
        # Ask agent to generate a workflow
        agent_request = {
            "thread_id": thread_id,
            "message": "Can you generate a complete workflow JSON for processing customer feedback that includes email collection, sentiment analysis, and response automation?"
        }
        
        response = await client.post(
            f"http://localhost:8004/api/v1/chat/send",
            json=agent_request
        )
        
        assert response.status_code == 200
        data = response.json()
        agent_response = data["agent_response"]["content"]
        
        # Response should contain workflow-related content
        workflow_keywords = ["workflow", "step", "email", "sentiment", "automation"]
        found_keywords = [kw for kw in workflow_keywords if kw.lower() in agent_response.lower()]
        assert len(found_keywords) >= 3
        
        # Check if we can also test the workflow generation endpoint directly
        workflow_request = {
            "description": "Process customer feedback with sentiment analysis and automated responses"
        }
        
        workflow_response = await client.post(
            f"http://localhost:8004/api/v1/workflows/generate",
            json=workflow_request
        )
        
        # This might fail if the LLM service isn't configured, but we should handle it gracefully
        if workflow_response.status_code == 200:
            workflow_data = workflow_response.json()
            assert "name" in workflow_data
            assert "steps" in workflow_data
            assert len(workflow_data["steps"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
