"""
Workflow Planner Agent - Plans the structure and steps for workflows
"""
import json
import logging
import uuid
from typing import Any, Dict

from app.agents.base_agent import BaseWorkflowAgent
from app.agents.workflow_tools import WorkflowTools
from app.schemas.workflow_agent_schemas import (AgentResponse, NodePosition,
                                                NodeType,
                                                WorkflowConnectionSchema,
                                                WorkflowNodeSchema,
                                                WorkflowPlan)
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.tools import FunctionTool

logger = logging.getLogger(__name__)

class WorkflowPlannerAgent(BaseWorkflowAgent):
    """Agent responsible for planning workflow structure"""
    
    def __init__(self):
        # Get workflow tools
        tools = WorkflowTools.get_all_tools()
        
        # Add planner-specific tools
        tools.extend([
            self._create_workflow_template_tool(),
            self._create_plan_generator_tool()
        ])
        
        super().__init__(
            name="workflow_planner",
            description="Plans workflow structure, nodes, and connections based on user requirements. I can analyze user requests and create detailed workflow plans with appropriate nodes and connections.",
            tools=tools
        )
        
        # Set up Pydantic output parser
        self.output_parser = PydanticOutputParser(WorkflowPlan)
    
    
    def _create_workflow_template_tool(self) -> FunctionTool:
        """Tool to get common workflow templates"""
        
        def get_workflow_template(workflow_type: str) -> Dict[str, Any]:
            """Get a template for common workflow patterns"""
            templates = {
                "web_scraping": {
                    "description": "Web scraping workflow that extracts content and processes it",
                    "nodes": [
                        {"type": "web_scraper", "name": "Web Scraper", "description": "Extracts content from target URL"},
                        {"type": "ai_processor", "name": "Content Processor", "description": "Processes and analyzes scraped content"},
                        {"type": "file_storage", "name": "Save Results", "description": "Stores processed results"},
                        {"type": "notification", "name": "Notify Complete", "description": "Sends completion notification"}
                    ],
                    "connections": [
                        {"from": "web_scraper", "from_output": "scraped_content", "to": "ai_processor", "to_input": "content"},
                        {"from": "ai_processor", "from_output": "processed_content", "to": "file_storage", "to_input": "content"},
                        {"from": "file_storage", "from_output": "file_path", "to": "notification", "to_input": "data"}
                    ]
                },
                "email_automation": {
                    "description": "Email automation workflow that monitors and responds to emails",
                    "nodes": [
                        {"type": "email_trigger", "name": "Email Monitor", "description": "Monitors incoming emails"},
                        {"type": "ai_processor", "name": "Email Classifier", "description": "Analyzes and classifies email content"},
                        {"type": "condition", "name": "Response Logic", "description": "Determines appropriate response"},
                        {"type": "notification", "name": "Send Response", "description": "Sends automated response"}
                    ],
                    "connections": [
                        {"from": "email_trigger", "from_output": "email_data", "to": "ai_processor", "to_input": "content"},
                        {"from": "ai_processor", "from_output": "analysis", "to": "condition", "to_input": "input_data"},
                        {"from": "condition", "from_output": "condition_result", "to": "notification", "to_input": "data"}
                    ]
                },
                "api_integration": {
                    "description": "API integration workflow for data synchronization",
                    "nodes": [
                        {"type": "http_request", "name": "Fetch Data", "description": "Retrieves data from external API"},
                        {"type": "data_transformer", "name": "Transform Data", "description": "Transforms data to required format"},
                        {"type": "database_operation", "name": "Store Data", "description": "Stores transformed data"},
                        {"type": "notification", "name": "Report Status", "description": "Reports operation status"}
                    ],
                    "connections": [
                        {"from": "http_request", "from_output": "response_data", "to": "data_transformer", "to_input": "input_data"},
                        {"from": "data_transformer", "from_output": "transformed_data", "to": "database_operation", "to_input": "data"},
                        {"from": "database_operation", "from_output": "result", "to": "notification", "to_input": "data"}
                    ]
                }
            }
            return templates.get(workflow_type, {"description": "Custom workflow", "nodes": [], "connections": []})
        
        return FunctionTool.from_defaults(
            fn=get_workflow_template,
            name="get_workflow_template",
            description="Get a template for common workflow patterns like web_scraping, email_automation, or api_integration"
        )
    
    def _create_plan_generator_tool(self) -> FunctionTool:
        """Tool to generate a complete workflow plan based on user requirements"""
        
        def generate_workflow_plan(
            workflow_name: str,
            workflow_description: str,
            requirements: str,
            workflow_type: str = "custom"
        ) -> Dict[str, Any]:
            """
            Generate a complete workflow plan based on requirements.
            
            Args:
                workflow_name: Name for the workflow
                workflow_description: Description of what the workflow should do
                requirements: Detailed requirements from the user
                workflow_type: Type of workflow (web_scraping, email_automation, api_integration, custom)
                
            Returns:
                Complete workflow plan with nodes, connections, and execution order
            """
            try:
                nodes = []
                connections = []
                
                # Start with template if available
                if workflow_type != "custom":
                    template_tool = WorkflowPlannerAgent._get_workflow_template_static(workflow_type)
                    base_nodes = template_tool.get("nodes", [])
                    base_connections = template_tool.get("connections", [])
                    
                    # Create nodes with proper IDs and positioning
                    node_id_map = {}
                    for i, node_template in enumerate(base_nodes):
                        node_id = str(uuid.uuid4())
                        node_id_map[node_template["type"]] = node_id
                        
                        # Position nodes in a flow layout
                        x_pos = 100 + (i * 300)
                        y_pos = 200
                        
                        node = {
                            "node_id": node_id,
                            "node_type": node_template["type"],
                            "name": node_template["name"],
                            "description": node_template["description"],
                            "position": {"x": x_pos, "y": y_pos},
                            "config": {},
                            "inputs": [],
                            "outputs": []
                        }
                        nodes.append(node)
                    
                    # Create connections using the mapped IDs
                    for conn_template in base_connections:
                        from_type = conn_template["from"]
                        to_type = conn_template["to"]
                        
                        if from_type in node_id_map and to_type in node_id_map:
                            connection = {
                                "connection_id": str(uuid.uuid4()),
                                "source_node_id": node_id_map[from_type],
                                "target_node_id": node_id_map[to_type],
                                "source_output": conn_template["from_output"],
                                "target_input": conn_template["to_input"]
                            }
                            connections.append(connection)
                
                # Generate execution order (simple topological sort)
                execution_order = [node["node_id"] for node in nodes]
                
                plan = {
                    "workflow_name": workflow_name,
                    "workflow_description": workflow_description,
                    "nodes": nodes,
                    "connections": connections,
                    "execution_order": execution_order,
                    "estimated_execution_time": len(nodes) * 30  # Rough estimate
                }
                
                logger.info(f"Generated workflow plan: {workflow_name} with {len(nodes)} nodes")
                return plan
                
            except Exception as e:
                logger.error(f"Failed to generate workflow plan: {str(e)}")
                return {
                    "error": f"Failed to generate plan: {str(e)}",
                    "workflow_name": workflow_name,
                    "workflow_description": workflow_description,
                    "nodes": [],
                    "connections": [],
                    "execution_order": []
                }
        
        return FunctionTool.from_defaults(
            fn=generate_workflow_plan,
            name="generate_workflow_plan",
            description="Generate a complete workflow plan with nodes, connections, and execution order based on user requirements"
        )
    
    @staticmethod
    def _get_workflow_template_static(workflow_type: str) -> Dict[str, Any]:
        """Static method to get workflow templates"""
        templates = {
            "web_scraping": {
                "description": "Web scraping workflow that extracts content and processes it",
                "nodes": [
                    {"type": "web_scraper", "name": "Web Scraper", "description": "Extracts content from target URL"},
                    {"type": "ai_processor", "name": "Content Processor", "description": "Processes and analyzes scraped content"},
                    {"type": "file_storage", "name": "Save Results", "description": "Stores processed results"},
                    {"type": "notification", "name": "Notify Complete", "description": "Sends completion notification"}
                ],
                "connections": [
                    {"from": "web_scraper", "from_output": "scraped_content", "to": "ai_processor", "to_input": "content"},
                    {"from": "ai_processor", "from_output": "processed_content", "to": "file_storage", "to_input": "content"},
                    {"from": "file_storage", "from_output": "file_path", "to": "notification", "to_input": "data"}
                ]
            },
            "email_automation": {
                "description": "Email automation workflow that monitors and responds to emails",
                "nodes": [
                    {"type": "email_trigger", "name": "Email Monitor", "description": "Monitors incoming emails"},
                    {"type": "ai_processor", "name": "Email Classifier", "description": "Analyzes and classifies email content"},
                    {"type": "condition", "name": "Response Logic", "description": "Determines appropriate response"},
                    {"type": "notification", "name": "Send Response", "description": "Sends automated response"}
                ],
                "connections": [
                    {"from": "email_trigger", "from_output": "email_data", "to": "ai_processor", "to_input": "content"},
                    {"from": "ai_processor", "from_output": "analysis", "to": "condition", "to_input": "input_data"},
                    {"from": "condition", "from_output": "condition_result", "to": "notification", "to_input": "data"}
                ]
            },
            "api_integration": {
                "description": "API integration workflow for data synchronization",
                "nodes": [
                    {"type": "http_request", "name": "Fetch Data", "description": "Retrieves data from external API"},
                    {"type": "data_transformer", "name": "Transform Data", "description": "Transforms data to required format"},
                    {"type": "database_operation", "name": "Store Data", "description": "Stores transformed data"},
                    {"type": "notification", "name": "Report Status", "description": "Reports operation status"}
                ],
                "connections": [
                    {"from": "http_request", "from_output": "response_data", "to": "data_transformer", "to_input": "input_data"},
                    {"from": "data_transformer", "from_output": "transformed_data", "to": "database_operation", "to_input": "data"},
                    {"from": "database_operation", "from_output": "result", "to": "notification", "to_input": "data"}
                ]
            }
        }
        return templates.get(workflow_type, {"description": "Custom workflow", "nodes": [], "connections": []})
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process user input and generate a workflow plan"""
        try:
            # Extract workflow context
            workflow_context = context or {}
            current_workflow = workflow_context.get('current_workflow', {})
            
            # Create a comprehensive prompt for planning
            planning_prompt = f"""
You are a workflow planning expert. Your task is to analyze the user's request and create a detailed workflow plan.

USER REQUEST: {user_input}

CURRENT WORKFLOW CONTEXT:
- Workflow Name: {current_workflow.get('name', 'New Workflow')}
- Existing Nodes: {len(current_workflow.get('visual_data', {}).get('nodes', []))}
- Existing Connections: {len(current_workflow.get('visual_data', {}).get('connections', []))}

INSTRUCTIONS:
1. Analyze the user's request to understand what they want to achieve
2. Determine if this is a request to:
   - Create a new workflow from scratch
   - Modify an existing workflow
   - Add specific functionality
3. Use the generate_workflow_plan tool to create a complete plan
4. If modifying existing workflow, consider current structure
5. Choose appropriate node types and connections

AVAILABLE NODE TYPES:
- web_scraper: Extract content from websites
- ai_processor: Process content with AI/LLM
- email_trigger: Monitor incoming emails
- notification: Send notifications (email, slack, etc.)
- file_storage: Store data to files or cloud
- http_request: Make API calls
- data_transformer: Transform and process data
- condition: Conditional logic and branching
- database_operation: Database read/write operations

Please analyze the request and generate an appropriate workflow plan.
"""
            
            # Execute the agent with the planning prompt
            response = await self._execute_with_context(planning_prompt, workflow_context)
            
            # Parse the response to extract workflow plan
            # The agent should have used tools to generate the plan
            plan_data = self._extract_plan_from_response(response, user_input, current_workflow)
            
            return AgentResponse(
                success=True,
                message=f"Generated workflow plan for: {user_input}",
                data=plan_data,
                confidence=0.9,
                reasoning=f"Analyzed user request '{user_input}' and generated appropriate workflow structure with {len(plan_data.get('nodes', []))} nodes and {len(plan_data.get('connections', []))} connections."
            )
            
        except Exception as e:
            logger.error(f"Workflow planning failed: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to generate workflow plan: {str(e)}",
                data={},
                confidence=0.0,
                reasoning=f"Error occurred during planning: {str(e)}"
            )
    
    def _extract_plan_from_response(self, response: str, user_input: str, current_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workflow plan from agent response"""
        try:
            # Try to extract JSON from the response if it contains structured data
            import re

            # Look for JSON-like structures in the response
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if 'nodes' in data and 'connections' in data:
                        return data
                except json.JSONDecodeError:
                    continue
            
            # If no structured plan found, create a default plan
            return self._create_default_plan(user_input, current_workflow)
            
        except Exception as e:
            logger.warning(f"Failed to extract plan from response: {str(e)}")
            return self._create_default_plan(user_input, current_workflow)
    
    def _create_default_plan(self, user_input: str, current_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create a default workflow plan based on keywords in user input"""
        user_lower = user_input.lower()
        
        # Determine workflow type based on keywords
        if any(keyword in user_lower for keyword in ['scrape', 'website', 'url', 'web']):
            workflow_type = "web_scraping"
        elif any(keyword in user_lower for keyword in ['email', 'gmail', 'mail']):
            workflow_type = "email_automation"
        elif any(keyword in user_lower for keyword in ['api', 'http', 'request']):
            workflow_type = "api_integration"
        else:
            workflow_type = "custom"
        
        # Generate using the tool
        plan_tool = self._create_plan_generator_tool()
        
        plan = plan_tool.fn(
            workflow_name=current_workflow.get('name', 'Generated Workflow'),
            workflow_description=f"Workflow generated from: {user_input}",
            requirements=user_input,
            workflow_type=workflow_type
        )
        
        return plan
