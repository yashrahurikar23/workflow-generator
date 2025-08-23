import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.crud.chat import ChatCRUD
from app.crud.workflow import WorkflowCRUD
from app.models.chat import (AgentConfig, ChatResponse, Message,
                             MessageCreateRequest, MessageRole)
from app.services.workflow_generator import WorkflowGenerator
from llama_index.core import Settings as LlamaSettings
from llama_index.core.llms import ChatMessage
from llama_index.core.llms import MessageRole as LlamaMessageRole
from llama_index.core.tools import FunctionTool

# Import LLMs with try/except for optional dependencies
try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from llama_index.core.agent import ReActAgent
except ImportError:
    ReActAgent = None


class ChatAgent:
    """LlamaIndex-powered chat agent for workflow automation assistance"""
    
    def __init__(
        self, 
        chat_crud: ChatCRUD, 
        workflow_crud: WorkflowCRUD,
        config: Optional[AgentConfig] = None
    ):
        self.chat_crud = chat_crud
        self.workflow_crud = workflow_crud
        self.workflow_generator = WorkflowGenerator()
        self.config = config or AgentConfig()
        
        # Initialize LLM based on settings
        self.llm = self._setup_llm()
        
        # Setup tools if enabled
        self.tools = []
        if self.config.enable_workflow_tools:
            self.tools = self._setup_workflow_tools()
        
        # Initialize the agent
        self.agent = self._setup_agent()
    
    def _setup_llm(self):
        """Setup the LLM based on configuration"""
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY and OpenAI:
            return OpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        elif settings.LLM_PROVIDER == "aiml" and settings.AIML_API_KEY and OpenAI:
            return OpenAI(
                api_key=settings.AIML_API_KEY,
                api_base=settings.AIML_BASE_URL,
                model=settings.AIML_MODEL,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        else:
            # Fallback to a mock LLM for testing/development
            from llama_index.core.llms.mock import MockLLM
            return MockLLM(max_tokens=self.config.max_tokens)
    
    def _setup_workflow_tools(self) -> List[FunctionTool]:
        """Setup workflow-related tools for the agent"""
        tools = []
        
        # Tool to generate workflows
        def generate_workflow_tool(description: str) -> str:
            """Generate a workflow based on a natural language description"""
            try:
                # Note: This is a sync wrapper for the async function
                # In a real implementation, you'd want to handle this better
                return f"Workflow generation requested for: {description}"
            except Exception as e:
                return f"Error generating workflow: {str(e)}"
        
        tools.append(FunctionTool.from_defaults(
            fn=generate_workflow_tool,
            name="generate_workflow",
            description="Generate a workflow from a natural language description"
        ))
        
        # Tool to list workflows
        def list_workflows_tool(limit: int = 10) -> str:
            """List available workflows"""
            try:
                # Note: This is a sync wrapper for the async function
                return "Listing workflows functionality will be implemented"
            except Exception as e:
                return f"Error listing workflows: {str(e)}"
        
        tools.append(FunctionTool.from_defaults(
            fn=list_workflows_tool,
            name="list_workflows",
            description="List available workflows in the system"
        ))
        
        # Tool to get workflow details
        def get_workflow_details_tool(workflow_id: str) -> str:
            """Get detailed information about a specific workflow"""
            try:
                # Note: This is a sync wrapper for the async function
                return f"Workflow details for ID {workflow_id} will be implemented"
            except Exception as e:
                return f"Error getting workflow details: {str(e)}"
        
        tools.append(FunctionTool.from_defaults(
            fn=get_workflow_details_tool,
            name="get_workflow_details", 
            description="Get detailed information about a specific workflow by ID"
        ))
        
        return tools
    
    def _setup_agent(self):
        """Setup the agent with tools"""
        # Set global LlamaIndex settings
        LlamaSettings.llm = self.llm
        
        # For now, we'll use a simple LLM without the ReAct agent
        # In a full implementation, you'd want to use the proper agent setup
        return None
    
    async def process_message(
        self, 
        thread_id: str, 
        user_message: str,
        use_context: bool = True
    ) -> ChatResponse:
        """Process a user message and generate a response"""
        start_time = time.time()
        
        # Get conversation context if enabled
        context_messages = []
        if use_context and self.config.enable_memory:
            recent_messages = await self.chat_crud.get_recent_messages(thread_id, count=10)
            context_messages = self._convert_to_llama_messages(recent_messages)
        
        try:
            if self.agent:
                # Use the agent with tools
                response = await self._generate_agent_response(user_message, context_messages)
            else:
                # Use direct LLM chat
                response = await self._generate_llm_response(user_message, context_messages)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Create the response message
            response_message = await self.chat_crud.create_message(
                thread_id=thread_id,
                message_data=MessageCreateRequest(
                    content=response,
                    role=MessageRole.ASSISTANT
                ),
                response_time_ms=response_time_ms,
                model_used=self._get_model_name()
            )
            
            return ChatResponse(
                message=response_message,
                thread_updated=True,
                context_used={
                    "context_messages_count": len(context_messages),
                    "tools_available": len(self.tools),
                    "response_time_ms": response_time_ms
                }
            )
            
        except Exception as e:
            # Create error response
            error_message = await self.chat_crud.create_message(
                thread_id=thread_id,
                message_data=MessageCreateRequest(
                    content=f"I apologize, but I encountered an error: {str(e)}",
                    role=MessageRole.ASSISTANT
                ),
                response_time_ms=int((time.time() - start_time) * 1000),
                model_used=self._get_model_name()
            )
            
            return ChatResponse(
                message=error_message,
                thread_updated=True,
                context_used={"error": str(e)}
            )
    
    def _convert_to_llama_messages(self, messages: List[Message]) -> List[ChatMessage]:
        """Convert our message format to LlamaIndex ChatMessage format"""
        llama_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.USER:
                role = LlamaMessageRole.USER
            elif msg.role == MessageRole.ASSISTANT:
                role = LlamaMessageRole.ASSISTANT
            else:
                role = LlamaMessageRole.SYSTEM
            
            llama_messages.append(ChatMessage(role=role, content=msg.content))
        
        return llama_messages
    
    async def _generate_agent_response(self, user_message: str, context_messages: List[ChatMessage]) -> str:
        """Generate response using the ReAct agent"""
        # For now, we'll use the agent's chat method
        # In a full implementation, we'd pass context more carefully
        response = await self.agent.achat(user_message)
        return str(response)
    
    async def _generate_llm_response(self, user_message: str, context_messages: List[ChatMessage]) -> str:
        """Generate response using direct LLM chat"""
        # Build the full conversation
        messages = context_messages + [
            ChatMessage(role=LlamaMessageRole.SYSTEM, content=self.config.system_prompt),
            ChatMessage(role=LlamaMessageRole.USER, content=user_message)
        ]
        
        response = await self.llm.achat(messages)
        return str(response)
    
    def _get_model_name(self) -> str:
        """Get the name of the model being used"""
        if settings.LLM_PROVIDER == "openai":
            return settings.OPENAI_MODEL
        elif settings.LLM_PROVIDER == "aiml":
            return settings.AIML_MODEL
        elif settings.LLM_PROVIDER == "anthropic":
            return settings.ANTHROPIC_MODEL
        else:
            return "mock"
    
    async def generate_thread_title(self, thread_id: str) -> Optional[str]:
        """Generate a title for a thread based on its first few messages"""
        try:
            messages = await self.chat_crud.get_recent_messages(thread_id, count=3)
            if not messages:
                return None
            
            # Create a prompt to generate a title
            conversation_text = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
            prompt = f"Based on this conversation, generate a short, descriptive title (max 50 characters):\n\n{conversation_text}\n\nTitle:"
            
            title_message = ChatMessage(role=LlamaMessageRole.USER, content=prompt)
            response = await self.llm.achat([title_message])
            
            title = str(response).strip().strip('"').strip("'")
            return title[:50] if len(title) > 50 else title
            
        except Exception:
            return None
