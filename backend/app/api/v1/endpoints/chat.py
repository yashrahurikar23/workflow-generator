from typing import List, Optional

from app.core.database import get_database
from app.crud.chat import ChatCRUD
from app.crud.workflow import WorkflowCRUD
from app.models.chat import (AgentConfig, ChatResponse, Message,
                             MessageCreateRequest, Thread, ThreadCreateRequest,
                             ThreadStatus)
from app.services.chat_agent import ChatAgent
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


async def get_chat_crud(db: AsyncIOMotorDatabase = Depends(get_database)) -> ChatCRUD:
    """Dependency to get chat CRUD instance"""
    return ChatCRUD(db)


async def get_workflow_crud(db: AsyncIOMotorDatabase = Depends(get_database)) -> WorkflowCRUD:
    """Dependency to get workflow CRUD instance"""
    return WorkflowCRUD(db)


async def get_chat_agent(
    chat_crud: ChatCRUD = Depends(get_chat_crud),
    workflow_crud: WorkflowCRUD = Depends(get_workflow_crud)
) -> ChatAgent:
    """Dependency to get chat agent instance"""
    return ChatAgent(chat_crud, workflow_crud)


# Thread endpoints
@router.post("/threads", response_model=Thread)
async def create_thread(
    thread_data: ThreadCreateRequest,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Create a new chat thread"""
    try:
        thread = await chat_crud.create_thread(thread_data)
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")


@router.get("/threads/{thread_id}", response_model=Thread)
async def get_thread(
    thread_id: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Get a specific thread by ID"""
    thread = await chat_crud.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.get("/threads", response_model=List[Thread])
async def list_threads(
    status: Optional[ThreadStatus] = None,
    limit: int = 50,
    skip: int = 0,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """List threads with optional filtering"""
    try:
        threads = await chat_crud.list_threads(status=status, limit=limit, skip=skip)
        return threads
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list threads: {str(e)}")


@router.patch("/threads/{thread_id}/title")
async def update_thread_title(
    thread_id: str,
    title: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Update the title of a thread"""
    success = await chat_crud.update_thread_title(thread_id, title)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found or update failed")
    return {"message": "Thread title updated successfully"}


@router.patch("/threads/{thread_id}/archive")
async def archive_thread(
    thread_id: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Archive a thread"""
    success = await chat_crud.archive_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found or archive failed")
    return {"message": "Thread archived successfully"}


@router.get("/threads/{thread_id}/stats")
async def get_thread_stats(
    thread_id: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Get statistics for a thread"""
    # Check if thread exists
    thread = await chat_crud.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    try:
        stats = await chat_crud.get_thread_stats(thread_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thread stats: {str(e)}")


# Message endpoints
@router.post("/threads/{thread_id}/messages", response_model=Message)
async def create_message(
    thread_id: str,
    message_data: MessageCreateRequest,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Create a new message in a thread"""
    # Check if thread exists
    thread = await chat_crud.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    try:
        message = await chat_crud.create_message(thread_id, message_data)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")


@router.get("/threads/{thread_id}/messages", response_model=List[Message])
async def get_thread_messages(
    thread_id: str,
    limit: int = 100,
    skip: int = 0,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Get messages for a specific thread"""
    # Check if thread exists
    thread = await chat_crud.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    try:
        messages = await chat_crud.get_thread_messages(thread_id, limit=limit, skip=skip)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.get("/messages/{message_id}", response_model=Message)
async def get_message(
    message_id: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Get a specific message by ID"""
    message = await chat_crud.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud)
):
    """Delete a message"""
    success = await chat_crud.delete_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or delete failed")
    return {"message": "Message deleted successfully"}


# Chat agent endpoints
@router.post("/threads/{thread_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    thread_id: str,
    request: dict,  # Expecting {"message_content": str, "use_context": bool}
    chat_crud: ChatCRUD = Depends(get_chat_crud),
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Send a message to the chat agent and get a response"""
    # Check if thread exists
    thread = await chat_crud.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Extract parameters from request
    message_content = request.get("message_content")
    use_context = request.get("use_context", True)
    
    if not message_content:
        raise HTTPException(status_code=400, detail="message_content is required")
    
    try:
        # First, save the user's message
        user_message = await chat_crud.create_message(
            thread_id,
            MessageCreateRequest(content=message_content, role="user")
        )
        
        # Then get the agent's response
        response = await agent.process_message(thread_id, message_content, use_context)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")


@router.post("/threads/{thread_id}/generate-title")
async def generate_thread_title(
    thread_id: str,
    chat_crud: ChatCRUD = Depends(get_chat_crud),
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Generate a title for a thread based on its content"""
    # Check if thread exists
    thread = await chat_crud.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    try:
        title = await agent.generate_thread_title(thread_id)
        if title:
            await chat_crud.update_thread_title(thread_id, title)
            return {"title": title, "message": "Thread title generated and updated"}
        else:
            return {"message": "Could not generate title for thread"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate title: {str(e)}")


# Agent configuration endpoints
@router.get("/agent/config", response_model=AgentConfig)
async def get_agent_config(agent: ChatAgent = Depends(get_chat_agent)):
    """Get the current agent configuration"""
    return agent.config


@router.post("/agent/config", response_model=AgentConfig)
async def update_agent_config(
    config: AgentConfig,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Update the agent configuration"""
    agent.config = config
    # Note: In a production system, you might want to save this to a database
    # and recreate the agent with the new config
    return config
