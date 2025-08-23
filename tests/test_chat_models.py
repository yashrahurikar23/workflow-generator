#!/usr/bin/env python3
"""
Unit tests for Chat and Thread models
"""
from datetime import datetime

import pytest
from bson import ObjectId

from backend.app.models.chat import Message, MessageBase, Thread, ThreadBase


class TestThreadModel:
    """Unit tests for Thread model"""
    
    def test_thread_creation(self):
        """Test creating a Thread object"""
        thread_data = {
            "title": "Test Thread",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        thread = Thread(**thread_data)
        assert thread.title == "Test Thread"
        assert isinstance(thread.created_at, datetime)
        assert isinstance(thread.updated_at, datetime)
        assert thread.id is None  # Not set until saved to DB
    
    def test_thread_base_validation(self):
        """Test ThreadBase validation"""
        # Valid data
        valid_data = {"title": "Valid Thread"}
        thread_base = ThreadBase(**valid_data)
        assert thread_base.title == "Valid Thread"
        
        # Test title validation
        with pytest.raises(ValueError):
            ThreadBase(title="")  # Empty title should fail
        
        with pytest.raises(ValueError):
            ThreadBase(title="a" * 201)  # Too long title should fail
    
    def test_thread_with_id(self):
        """Test Thread with ObjectId"""
        thread_id = ObjectId()
        thread_data = {
            "id": thread_id,
            "title": "Test Thread with ID",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        thread = Thread(**thread_data)
        assert thread.id == thread_id
        assert thread.title == "Test Thread with ID"


class TestMessageModel:
    """Unit tests for Message model"""
    
    def test_message_creation(self):
        """Test creating a Message object"""
        thread_id = ObjectId()
        message_data = {
            "thread_id": thread_id,
            "content": "Hello, this is a test message",
            "is_user": True,
            "timestamp": datetime.utcnow()
        }
        
        message = Message(**message_data)
        assert message.thread_id == thread_id
        assert message.content == "Hello, this is a test message"
        assert message.is_user is True
        assert isinstance(message.timestamp, datetime)
        assert message.id is None  # Not set until saved to DB
    
    def test_message_base_validation(self):
        """Test MessageBase validation"""
        thread_id = ObjectId()
        
        # Valid data
        valid_data = {
            "thread_id": thread_id,
            "content": "Valid message content",
            "is_user": True
        }
        message_base = MessageBase(**valid_data)
        assert message_base.content == "Valid message content"
        assert message_base.is_user is True
        
        # Test content validation
        with pytest.raises(ValueError):
            MessageBase(thread_id=thread_id, content="", is_user=True)  # Empty content
        
        with pytest.raises(ValueError):
            MessageBase(thread_id=thread_id, content="a" * 5001, is_user=True)  # Too long content
    
    def test_user_vs_ai_message(self):
        """Test distinction between user and AI messages"""
        thread_id = ObjectId()
        
        # User message
        user_message = Message(
            thread_id=thread_id,
            content="User question",
            is_user=True,
            timestamp=datetime.utcnow()
        )
        assert user_message.is_user is True
        
        # AI message
        ai_message = Message(
            thread_id=thread_id,
            content="AI response",
            is_user=False,
            timestamp=datetime.utcnow()
        )
        assert ai_message.is_user is False
    
    def test_message_with_metadata(self):
        """Test Message with optional metadata"""
        thread_id = ObjectId()
        metadata = {
            "model": "gpt-4",
            "tokens_used": 150,
            "processing_time": 2.5
        }
        
        message = Message(
            thread_id=thread_id,
            content="Message with metadata",
            is_user=False,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        
        assert message.metadata == metadata
        assert message.metadata["model"] == "gpt-4"
        assert message.metadata["tokens_used"] == 150


class TestModelRelationships:
    """Test relationships between Thread and Message models"""
    
    def test_thread_message_relationship(self):
        """Test that messages can reference threads correctly"""
        # Create a thread
        thread = Thread(
            title="Parent Thread",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Simulate thread ID (normally assigned by MongoDB)
        thread_id = ObjectId()
        
        # Create messages for this thread
        message1 = Message(
            thread_id=thread_id,
            content="First message",
            is_user=True,
            timestamp=datetime.utcnow()
        )
        
        message2 = Message(
            thread_id=thread_id,
            content="Second message",
            is_user=False,
            timestamp=datetime.utcnow()
        )
        
        # Both messages should reference the same thread
        assert message1.thread_id == message2.thread_id == thread_id
    
    def test_message_ordering(self):
        """Test that messages can be ordered by timestamp"""
        thread_id = ObjectId()
        now = datetime.utcnow()
        
        # Create messages with different timestamps
        from datetime import timedelta
        
        message1 = Message(
            thread_id=thread_id,
            content="First message",
            is_user=True,
            timestamp=now
        )
        
        message2 = Message(
            thread_id=thread_id,
            content="Second message",
            is_user=False,
            timestamp=now + timedelta(seconds=30)
        )
        
        message3 = Message(
            thread_id=thread_id,
            content="Third message",
            is_user=True,
            timestamp=now + timedelta(minutes=1)
        )
        
        messages = [message3, message1, message2]  # Out of order
        sorted_messages = sorted(messages, key=lambda m: m.timestamp)
        
        assert sorted_messages[0] == message1
        assert sorted_messages[1] == message2
        assert sorted_messages[2] == message3


if __name__ == "__main__":
    pytest.main([__file__])
