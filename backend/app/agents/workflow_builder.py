"""
Workflow Builder Agent - Converts workflow plans into actual workflow structures
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from app.agents.base_agent import BaseWorkflowAgent
from app.agents.workflow_tools import WorkflowTools
from app.schemas.workflow_agent_schemas import AgentResponse
from llama_index.core.tools import FunctionTool

logger = logging.getLogger(__name__)

class WorkflowBuilderAgent(BaseWorkflowAgent):
    """Agent responsible for building actual workflows from plans"""
    
    def __init__(self):
        # Get workflow tools
        tools = WorkflowTools.get_all_tools()
        
        # Add builder-specific tools
        tools.extend([
            self._create_visual_layout_tool(),
            self._create_workflow_converter_tool()
        ])
        
        super().__init__(
            name="workflow_builder",
            description="Builds actual workflow structures from workflow plans. I convert abstract plans into concrete visual workflows with proper node positioning and configurations.",
            tools=tools
        )
    
    
    def _create_visual_layout_tool(self) -> FunctionTool:
        """Tool to create optimal visual layout for workflow nodes"""
        
        def create_visual_layout(nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> Dict[str, Any]:
            """
            Create an optimal visual layout for workflow nodes.
            
            Args:
                nodes: List of workflow nodes
                connections: List of connections between nodes
                
            Returns:
                Layout information with optimized node positions
            """
            try:
                # Simple horizontal flow layout
                layout_info = {
                    "layout_type": "horizontal_flow",
                    "node_spacing": {"x": 300, "y": 150},
                    "start_position": {"x": 100, "y": 200}
                }
                
                # Position nodes in a flow pattern
                positioned_nodes = []
                for i, node in enumerate(nodes):
                    x_pos = layout_info["start_position"]["x"] + (i * layout_info["node_spacing"]["x"])
                    y_pos = layout_info["start_position"]["y"]
                    
                    # Add some vertical variation for better visual appeal
                    if i % 2 == 1:
                        y_pos += 50
                    
                    positioned_node = {
                        **node,
                        "position": {"x": x_pos, "y": y_pos}
                    }
                    positioned_nodes.append(positioned_node)
                
                return {
                    "nodes": positioned_nodes,
                    "layout_info": layout_info,
                    "canvas_size": {
                        "width": max(1200, len(nodes) * 300 + 200),
                        "height": 600
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to create visual layout: {str(e)}")
                return {"nodes": nodes, "layout_info": {}, "canvas_size": {"width": 1200, "height": 600}}
        
        return FunctionTool.from_defaults(
            fn=create_visual_layout,
            name="create_visual_layout",
            description="Create optimal visual layout for workflow nodes with proper positioning"
        )
    
    def _create_workflow_converter_tool(self) -> FunctionTool:
        """Tool to convert workflow plan to visual workflow format"""
        
        def convert_plan_to_visual_workflow(
            workflow_plan: Dict[str, Any],
            current_workflow: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """
            Convert a workflow plan into the visual workflow format used by the frontend.
            
            Args:
                workflow_plan: The workflow plan from the planner agent
                current_workflow: Current workflow data (for updates)
                
            Returns:
                Complete visual workflow structure
            """
            try:
                plan_nodes = workflow_plan.get("nodes", [])
                plan_connections = workflow_plan.get("connections", [])
                
                # Convert nodes to visual format
                visual_nodes = []
                for node in plan_nodes:
                    visual_node = {
                        "node_id": node.get("node_id", str(uuid.uuid4())),
                        "node_type_id": node.get("node_type", "unknown"),
                        "name": node.get("name", "Unnamed Node"),
                        "position": node.get("position", {"x": 100, "y": 100}),
                        "config": node.get("config", {}),
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    visual_nodes.append(visual_node)
                
                # Convert connections to visual format
                visual_connections = []
                for conn in plan_connections:
                    visual_connection = {
                        "connection_id": conn.get("connection_id", str(uuid.uuid4())),
                        "source_node_id": conn.get("source_node_id"),
                        "target_node_id": conn.get("target_node_id"),
                        "source_output": conn.get("source_output", "output"),
                        "target_input": conn.get("target_input", "input"),
                        "created_at": datetime.utcnow().isoformat()
                    }
                    visual_connections.append(visual_connection)
                
                # Create optimal layout
                layout_result = create_visual_layout(visual_nodes, visual_connections)
                positioned_nodes = layout_result["nodes"]
                
                # Create the complete visual workflow
                visual_workflow = {
                    "visual_data": {
                        "nodes": positioned_nodes,
                        "connections": visual_connections
                    },
                    "metadata": {
                        "layout_info": layout_result.get("layout_info", {}),
                        "canvas_size": layout_result.get("canvas_size", {"width": 1200, "height": 600}),
                        "generated_at": datetime.utcnow().isoformat(),
                        "node_count": len(positioned_nodes),
                        "connection_count": len(visual_connections)
                    }
                }
                
                # If updating existing workflow, merge with current data
                if current_workflow:
                    visual_workflow = {
                        **current_workflow,
                        **visual_workflow,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                
                logger.info(f"Converted workflow plan to visual format: {len(positioned_nodes)} nodes, {len(visual_connections)} connections")
                return visual_workflow
                
            except Exception as e:
                logger.error(f"Failed to convert plan to visual workflow: {str(e)}")
                return current_workflow or {"visual_data": {"nodes": [], "connections": []}}
        
        return FunctionTool.from_defaults(
            fn=convert_plan_to_visual_workflow,
            name="convert_plan_to_visual_workflow",
            description="Convert a workflow plan into the visual workflow format used by the frontend"
        )
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process workflow plan and build the actual workflow structure"""
        try:
            # Extract context
            workflow_context = context or {}
            workflow_plan = workflow_context.get('workflow_plan', {})
            current_workflow = workflow_context.get('original_context', {})
            
            if not workflow_plan:
                raise ValueError("No workflow plan provided for building")
            
            # Create a comprehensive prompt for building
            building_prompt = f"""
You are a workflow building expert. Your task is to convert the workflow plan into a concrete visual workflow structure.

WORKFLOW PLAN TO BUILD:
{json.dumps(workflow_plan, indent=2)}

CURRENT WORKFLOW CONTEXT:
{json.dumps(current_workflow, indent=2) if current_workflow else "No existing workflow"}

USER REQUEST: {user_input}

INSTRUCTIONS:
1. Use the convert_plan_to_visual_workflow tool to convert the plan
2. Ensure all nodes have proper positioning and configuration
3. Validate all connections are correct
4. Create a layout that flows logically from left to right
5. If updating existing workflow, preserve user customizations where possible

Please convert the workflow plan into a complete visual workflow structure.
"""
            
            # Execute the agent with the building prompt
            response = await self._execute_with_context(building_prompt, workflow_context)
            
            # Extract the built workflow from the response
            built_workflow = self._extract_workflow_from_response(response, workflow_plan, current_workflow)
            
            return AgentResponse(
                success=True,
                message=f"Built workflow structure from plan",
                data=built_workflow,
                confidence=0.95,
                reasoning=f"Successfully converted workflow plan with {len(workflow_plan.get('nodes', []))} nodes into visual workflow structure with proper positioning and connections."
            )
            
        except Exception as e:
            logger.error(f"Workflow building failed: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to build workflow: {str(e)}",
                data={},
                confidence=0.0,
                reasoning=f"Error occurred during building: {str(e)}"
            )
    
    def _extract_workflow_from_response(
        self, 
        response: str, 
        workflow_plan: Dict[str, Any], 
        current_workflow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract built workflow from agent response"""
        try:
            # Try to extract JSON from response if available
            import re
            
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if 'visual_data' in data:
                        return data
                except json.JSONDecodeError:
                    continue
            
            # If no structured workflow found, use the converter tool directly
            converter_tool = self._create_workflow_converter_tool()
            return converter_tool.fn(workflow_plan, current_workflow)
            
        except Exception as e:
            logger.warning(f"Failed to extract workflow from response: {str(e)}")
            # Fallback to direct conversion
            converter_tool = self._create_workflow_converter_tool()
            return converter_tool.fn(workflow_plan, current_workflow)
