"""
Base agent framework for workflow generation using LlamaIndex
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.llm_config import get_llm_instance
from app.schemas.workflow_agent_schemas import AgentResponse
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import LLM
from llama_index.core.tools import FunctionTool

logger = logging.getLogger(__name__)

class BaseWorkflowAgent(ABC):
    """Base class for all workflow agents"""
    
    def __init__(
        self, 
        name: str,
        description: str,
        llm: Optional[LLM] = None,
        tools: Optional[List[FunctionTool]] = None
    ):
        self.name = name
        self.description = description
        self.llm = llm or get_llm_instance()
        self.tools = tools or []
        self.agent = self._create_agent()
    
    def _create_agent(self) -> ReActAgent:
        """Create the LlamaIndex ReAct agent"""
        return ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            max_iterations=10
        )
    
    @abstractmethod
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process user input and return agent response"""
        pass
    
    def add_tool(self, tool: FunctionTool):
        """Add a tool to the agent"""
        self.tools.append(tool)
        self.agent = self._create_agent()  # Recreate agent with new tools
    
    async def _execute_with_context(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Execute agent with context"""
        try:
            if context:
                enriched_prompt = f"""
Context: {context}

User Request: {prompt}

Please analyze the request and provide a detailed response based on your role as {self.name}.
"""
            else:
                enriched_prompt = prompt
            
            response = await self.agent.achat(enriched_prompt)
            return str(response)
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {str(e)}")
            raise

class WorkflowAgentOrchestrator:
    """Main orchestrator that coordinates all workflow agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseWorkflowAgent] = {}
        self.conversation_history: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: BaseWorkflowAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    async def process_workflow_request(
        self, 
        user_message: str, 
        workflow_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a workflow request by coordinating multiple agents
        """
        try:
            # Step 1: Use WorkflowPlannerAgent to create a plan
            if "workflow_planner" not in self.agents:
                raise ValueError("WorkflowPlannerAgent not registered")
            
            planner_response = await self.agents["workflow_planner"].process(
                user_message, 
                workflow_context
            )
            
            # Step 2: Use WorkflowBuilderAgent to build the actual workflow
            if "workflow_builder" not in self.agents:
                raise ValueError("WorkflowBuilderAgent not registered")
            
            builder_response = await self.agents["workflow_builder"].process(
                user_message,
                {
                    "workflow_plan": planner_response.data,
                    "original_context": workflow_context
                }
            )
            
            # Step 3: Validate the workflow
            if "workflow_validator" in self.agents:
                validator_response = await self.agents["workflow_validator"].process(
                    user_message,
                    {
                        "workflow": builder_response.data,
                        "original_plan": planner_response.data
                    }
                )
                
                if not validator_response.success:
                    # If validation fails, try to fix the workflow
                    logger.warning(f"Workflow validation failed: {validator_response.message}")
            
            # Store conversation history
            self.conversation_history.append({
                "user_message": user_message,
                "planner_response": planner_response.dict(),
                "builder_response": builder_response.dict(),
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "workflow_plan": planner_response.data,
                "generated_workflow": builder_response.data,
                "ai_message": {
                    "id": f"msg_{int(__import__('time').time() * 1000)}",
                    "role": "assistant",
                    "content": self._generate_user_friendly_response(
                        user_message, 
                        planner_response, 
                        builder_response
                    ),
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Workflow request processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ai_message": {
                    "id": f"msg_{int(__import__('time').time() * 1000)}",
                    "role": "assistant",
                    "content": f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your request or contact support.",
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                }
            }
    
    def _generate_user_friendly_response(
        self, 
        user_message: str, 
        planner_response: AgentResponse, 
        builder_response: AgentResponse
    ) -> str:
        """Generate a user-friendly response explaining what was created"""
        
        workflow_plan = planner_response.data
        workflow = builder_response.data
        
        response = f"""🚀 **Workflow Created Successfully!**

**Your Request**: {user_message}

**What I Built**:
• **Workflow Name**: {workflow_plan.get('workflow_name', 'New Workflow')}
• **Description**: {workflow_plan.get('workflow_description', 'Custom workflow')}
• **Nodes Created**: {len(workflow.get('visual_data', {}).get('nodes', []))} workflow steps
• **Connections**: {len(workflow.get('visual_data', {}).get('connections', []))} data flows

**Workflow Steps**:
"""
        
        # Add details about each node
        nodes = workflow.get('visual_data', {}).get('nodes', [])
        for i, node in enumerate(nodes, 1):
            response += f"{i}. **{node.get('name', 'Unknown')}** ({node.get('node_type_id', 'unknown')})\n"
        
        response += f"""
**Next Steps**:
✅ Your workflow is now visible in the diagram
✅ You can click on any node to configure its settings
✅ You can ask me to modify or add more steps
✅ When ready, you can execute the workflow

**Try saying**: "Add error handling" or "Modify the scraper settings" to continue building!
"""
        
        return response
