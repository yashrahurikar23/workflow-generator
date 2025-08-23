from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of the message sender"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ThreadStatus(str, Enum):
    """Status of a chat thread"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


class Message(BaseModel):
    """A single message in a chat thread"""
    message_id: str = Field(..., description="Unique identifier for the message")
    thread_id: str = Field(..., description="ID of the thread this message belongs to")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the message")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the message was created")
    
    # Optional fields for agent responses
    tokens_used: Optional[int] = Field(None, description="Number of tokens used for this message (LLM responses)")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds (LLM responses)")
    model_used: Optional[str] = Field(None, description="Model used to generate this message (LLM responses)")


class Thread(BaseModel):
    """A chat thread/conversation"""
    thread_id: str = Field(..., description="Unique identifier for the thread")
    title: Optional[str] = Field(None, description="Optional title for the thread")
    status: ThreadStatus = Field(default=ThreadStatus.ACTIVE, description="Status of the thread")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the thread")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the thread was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the thread was last updated")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="When the last message was sent")
    
    # Summary fields
    message_count: int = Field(default=0, description="Total number of messages in this thread")
    

class ThreadCreateRequest(BaseModel):
    """Request to create a new thread"""
    title: Optional[str] = Field(None, description="Optional title for the thread")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the thread")


class MessageCreateRequest(BaseModel):
    """Request to create a new message"""
    content: str = Field(..., description="Content of the message")
    role: MessageRole = Field(default=MessageRole.USER, description="Role of the message sender")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the message")


class ChatResponse(BaseModel):
    """Response from the chat agent"""
    message: Message = Field(..., description="The agent's response message")
    thread_updated: bool = Field(default=False, description="Whether the thread was updated")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Context or tools used by the agent")


class AgentConfig(BaseModel):
    """Configuration for the chat agent"""
    system_prompt: str = Field(
        default="You are a helpful AI assistant specialized in workflow automation. "
        "You can help users create, understand, and manage automated workflows. "
        "You have access to workflow generation tools and can provide guidance on automation best practices.",
        description="System prompt for the agent"
    )
    max_tokens: int = Field(default=1000, description="Maximum tokens for agent responses")
    temperature: float = Field(default=0.7, description="Temperature for response generation")
    enable_workflow_tools: bool = Field(default=True, description="Whether to enable workflow-related tools")
    enable_memory: bool = Field(default=True, description="Whether to use conversation memory")
