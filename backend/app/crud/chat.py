import uuid
from datetime import datetime
from typing import List, Optional

from app.models.chat import (Message, MessageCreateRequest, MessageRole,
                             Thread, ThreadCreateRequest, ThreadStatus)
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING


class ChatCRUD:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.threads_collection = database.threads
        self.messages_collection = database.messages

    # Thread operations
    async def create_thread(self, thread_data: ThreadCreateRequest) -> Thread:
        """Create a new chat thread"""
        thread_id = str(uuid.uuid4())
        
        thread = Thread(
            thread_id=thread_id,
            title=thread_data.title,
            metadata=thread_data.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Convert to dict and insert
        thread_dict = thread.model_dump()
        await self.threads_collection.insert_one(thread_dict)
        
        return thread

    async def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Get a thread by ID"""
        thread_doc = await self.threads_collection.find_one({"thread_id": thread_id})
        if thread_doc:
            # Remove MongoDB's _id field
            thread_doc.pop("_id", None)
            return Thread(**thread_doc)
        return None

    async def update_thread_activity(self, thread_id: str) -> bool:
        """Update the last activity timestamp for a thread"""
        result = await self.threads_collection.update_one(
            {"thread_id": thread_id},
            {
                "$set": {
                    "last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"message_count": 1}
            }
        )
        return result.modified_count > 0

    async def update_thread_title(self, thread_id: str, title: str) -> bool:
        """Update the title of a thread"""
        result = await self.threads_collection.update_one(
            {"thread_id": thread_id},
            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def archive_thread(self, thread_id: str) -> bool:
        """Archive a thread"""
        result = await self.threads_collection.update_one(
            {"thread_id": thread_id},
            {
                "$set": {
                    "status": ThreadStatus.ARCHIVED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def list_threads(
        self, 
        status: Optional[ThreadStatus] = None, 
        limit: int = 50, 
        skip: int = 0
    ) -> List[Thread]:
        """List threads with optional filtering"""
        query = {}
        if status:
            query["status"] = status

        cursor = self.threads_collection.find(query).sort("last_activity", DESCENDING).skip(skip).limit(limit)
        threads = []
        
        async for thread_doc in cursor:
            thread_doc.pop("_id", None)
            threads.append(Thread(**thread_doc))
        
        return threads

    # Message operations
    async def create_message(
        self, 
        thread_id: str, 
        message_data: MessageCreateRequest,
        tokens_used: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        model_used: Optional[str] = None
    ) -> Message:
        """Create a new message in a thread"""
        message_id = str(uuid.uuid4())
        
        message = Message(
            message_id=message_id,
            thread_id=thread_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            model_used=model_used,
            created_at=datetime.utcnow()
        )
        
        # Convert to dict and insert
        message_dict = message.model_dump()
        await self.messages_collection.insert_one(message_dict)
        
        # Update thread activity
        await self.update_thread_activity(thread_id)
        
        return message

    async def get_message(self, message_id: str) -> Optional[Message]:
        """Get a message by ID"""
        message_doc = await self.messages_collection.find_one({"message_id": message_id})
        if message_doc:
            # Remove MongoDB's _id field
            message_doc.pop("_id", None)
            return Message(**message_doc)
        return None

    async def get_thread_messages(
        self, 
        thread_id: str, 
        limit: int = 100, 
        skip: int = 0
    ) -> List[Message]:
        """Get messages for a specific thread"""
        cursor = self.messages_collection.find(
            {"thread_id": thread_id}
        ).sort("created_at", 1).skip(skip).limit(limit)  # Sort by creation time ascending
        
        messages = []
        async for message_doc in cursor:
            message_doc.pop("_id", None)
            messages.append(Message(**message_doc))
        
        return messages

    async def get_recent_messages(
        self, 
        thread_id: str, 
        count: int = 10
    ) -> List[Message]:
        """Get the most recent messages from a thread (for context)"""
        cursor = self.messages_collection.find(
            {"thread_id": thread_id}
        ).sort("created_at", DESCENDING).limit(count)
        
        messages = []
        async for message_doc in cursor:
            message_doc.pop("_id", None)
            messages.append(Message(**message_doc))
        
        # Reverse to get chronological order
        return list(reversed(messages))

    async def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        result = await self.messages_collection.delete_one({"message_id": message_id})
        return result.deleted_count > 0

    async def get_thread_stats(self, thread_id: str) -> dict:
        """Get statistics for a thread"""
        message_count = await self.messages_collection.count_documents({"thread_id": thread_id})
        
        # Get role distribution
        pipeline = [
            {"$match": {"thread_id": thread_id}},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        
        role_stats = {}
        async for doc in self.messages_collection.aggregate(pipeline):
            role_stats[doc["_id"]] = doc["count"]
        
        # Get total tokens used (for LLM responses)
        pipeline = [
            {"$match": {"thread_id": thread_id, "tokens_used": {"$exists": True}}},
            {"$group": {"_id": None, "total_tokens": {"$sum": "$tokens_used"}}}
        ]
        
        total_tokens = 0
        async for doc in self.messages_collection.aggregate(pipeline):
            total_tokens = doc["total_tokens"]
        
        return {
            "message_count": message_count,
            "role_distribution": role_stats,
            "total_tokens_used": total_tokens
        }
