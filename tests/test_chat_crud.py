#!/usr/bin/env python3
"""
Unit tests for Chat CRUD operations
"""
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId

from backend.app.crud.chat import ChatCRUD
from backend.app.models.chat import Message, MessageBase, Thread, ThreadBase


class TestChatCRUD:
    """Unit tests for ChatCRUD operations"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database for testing"""
        return AsyncMock()
    
    @pytest.fixture
    def chat_crud(self, mock_db):
        """ChatCRUD instance with mocked database"""
        return ChatCRUD(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_thread(self, chat_crud, mock_db):
        """Test creating a new thread"""
        # Mock database response
        thread_id = ObjectId()
        mock_db.threads.insert_one.return_value.inserted_id = thread_id
        
        # Test data
        thread_data = ThreadBase(title="Test Thread")
        
        # Execute
        result = await chat_crud.create_thread(thread_data)
        
        # Assertions
        assert result["id"] == str(thread_id)
        assert result["title"] == "Test Thread"
        assert "created_at" in result
        assert "updated_at" in result
        
        # Verify database call
        mock_db.threads.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_thread_exists(self, chat_crud, mock_db):
        """Test getting an existing thread"""
        thread_id = ObjectId()
        mock_thread_data = {
            "_id": thread_id,
            "title": "Existing Thread",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_db.threads.find_one.return_value = mock_thread_data
        
        result = await chat_crud.get_thread(str(thread_id))
        
        assert result["id"] == str(thread_id)
        assert result["title"] == "Existing Thread"
        mock_db.threads.find_one.assert_called_once_with({"_id": thread_id})
    
    @pytest.mark.asyncio
    async def test_get_thread_not_found(self, chat_crud, mock_db):
        """Test getting a non-existent thread"""
        thread_id = ObjectId()
        mock_db.threads.find_one.return_value = None
        
        result = await chat_crud.get_thread(str(thread_id))
        
        assert result is None
        mock_db.threads.find_one.assert_called_once_with({"_id": thread_id})
    
    @pytest.mark.asyncio
    async def test_list_threads(self, chat_crud, mock_db):
        """Test listing threads with pagination"""
        # Mock threads data
        mock_threads = [
            {
                "_id": ObjectId(),
                "title": "Thread 1",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "title": "Thread 2", 
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Mock database responses
        mock_db.threads.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list.return_value = mock_threads
        mock_db.threads.count_documents.return_value = 2
        
        result = await chat_crud.list_threads(skip=0, limit=10)
        
        assert len(result["threads"]) == 2
        assert result["total"] == 2
        assert result["threads"][0]["title"] == "Thread 1"
        assert result["threads"][1]["title"] == "Thread 2"
    
    @pytest.mark.asyncio
    async def test_add_message(self, chat_crud, mock_db):
        """Test adding a message to a thread"""
        thread_id = ObjectId()
        message_id = ObjectId()
        
        # Mock database responses
        mock_db.messages.insert_one.return_value.inserted_id = message_id
        mock_db.threads.update_one.return_value = AsyncMock()
        
        message_data = MessageBase(
            thread_id=thread_id,
            content="Test message",
            is_user=True
        )
        
        result = await chat_crud.add_message(message_data)
        
        assert result["id"] == str(message_id)
        assert result["content"] == "Test message"
        assert result["is_user"] is True
        assert result["thread_id"] == str(thread_id)
        
        # Verify both database calls
        mock_db.messages.insert_one.assert_called_once()
        mock_db.threads.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_messages(self, chat_crud, mock_db):
        """Test getting messages for a thread"""
        thread_id = ObjectId()
        mock_messages = [
            {
                "_id": ObjectId(),
                "thread_id": thread_id,
                "content": "First message",
                "is_user": True,
                "timestamp": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "thread_id": thread_id,
                "content": "Second message",
                "is_user": False,
                "timestamp": datetime.utcnow()
            }
        ]
        
        mock_db.messages.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list.return_value = mock_messages
        mock_db.messages.count_documents.return_value = 2
        
        result = await chat_crud.get_messages(str(thread_id), skip=0, limit=50)
        
        assert len(result["messages"]) == 2
        assert result["total"] == 2
        assert result["messages"][0]["content"] == "First message"
        assert result["messages"][1]["content"] == "Second message"
    
    @pytest.mark.asyncio
    async def test_delete_thread(self, chat_crud, mock_db):
        """Test deleting a thread and its messages"""
        thread_id = ObjectId()
        
        # Mock database responses
        mock_db.threads.delete_one.return_value.deleted_count = 1
        mock_db.messages.delete_many.return_value.deleted_count = 3
        
        result = await chat_crud.delete_thread(str(thread_id))
        
        assert result is True
        mock_db.threads.delete_one.assert_called_once_with({"_id": thread_id})
        mock_db.messages.delete_many.assert_called_once_with({"thread_id": thread_id})
    
    @pytest.mark.asyncio
    async def test_delete_thread_not_found(self, chat_crud, mock_db):
        """Test deleting a non-existent thread"""
        thread_id = ObjectId()
        
        # Mock database responses
        mock_db.threads.delete_one.return_value.deleted_count = 0
        
        result = await chat_crud.delete_thread(str(thread_id))
        
        assert result is False
        mock_db.threads.delete_one.assert_called_once_with({"_id": thread_id})
    
    @pytest.mark.asyncio
    async def test_update_thread(self, chat_crud, mock_db):
        """Test updating a thread"""
        thread_id = ObjectId()
        updated_thread_data = {
            "_id": thread_id,
            "title": "Updated Thread",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Mock database responses
        mock_db.threads.update_one.return_value.modified_count = 1
        mock_db.threads.find_one.return_value = updated_thread_data
        
        result = await chat_crud.update_thread(str(thread_id), {"title": "Updated Thread"})
        
        assert result["title"] == "Updated Thread"
        mock_db.threads.update_one.assert_called_once()
        mock_db.threads.find_one.assert_called_once()


class TestChatCRUDEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def chat_crud(self, mock_db):
        return ChatCRUD(mock_db)
    
    @pytest.mark.asyncio
    async def test_invalid_object_id(self, chat_crud, mock_db):
        """Test handling of invalid ObjectId strings"""
        with pytest.raises(Exception):  # Should raise InvalidId or similar
            await chat_crud.get_thread("invalid_id")
    
    @pytest.mark.asyncio
    async def test_empty_thread_list(self, chat_crud, mock_db):
        """Test listing threads when none exist"""
        mock_db.threads.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list.return_value = []
        mock_db.threads.count_documents.return_value = 0
        
        result = await chat_crud.list_threads()
        
        assert result["threads"] == []
        assert result["total"] == 0
    
    @pytest.mark.asyncio
    async def test_large_message_content(self, chat_crud, mock_db):
        """Test handling of large message content"""
        thread_id = ObjectId()
        large_content = "x" * 10000  # Very large message
        
        message_data = MessageBase(
            thread_id=thread_id,
            content=large_content,
            is_user=True
        )
        
        # This should work as long as it's under the limit
        message_id = ObjectId()
        mock_db.messages.insert_one.return_value.inserted_id = message_id
        mock_db.threads.update_one.return_value = AsyncMock()
        
        result = await chat_crud.add_message(message_data)
        assert result["content"] == large_content
    
    @pytest.mark.asyncio
    async def test_concurrent_message_addition(self, chat_crud, mock_db):
        """Test adding multiple messages concurrently"""
        thread_id = ObjectId()
        
        # Mock database responses
        mock_db.messages.insert_one.side_effect = [
            AsyncMock(inserted_id=ObjectId()),
            AsyncMock(inserted_id=ObjectId()),
            AsyncMock(inserted_id=ObjectId())
        ]
        mock_db.threads.update_one.return_value = AsyncMock()
        
        # Create multiple messages
        messages = [
            MessageBase(thread_id=thread_id, content=f"Message {i}", is_user=True)
            for i in range(3)
        ]
        
        # Add them concurrently
        tasks = [chat_crud.add_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["content"] == f"Message {i}"


if __name__ == "__main__":
    pytest.main([__file__])
