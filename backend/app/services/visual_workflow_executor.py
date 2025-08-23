"""
Visual Workflow Execution Engine - Converts and executes visual workflows using LlamaIndex
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from llama_index.core.workflow import (Context, Event, StartEvent, StopEvent,
                                       Workflow, step)

from backend.app.models.workflow_visual import (NodeConnection, VisualNode,
                                                VisualWorkflow)
from backend.app.services.node_registry import NodeTypeRegistry

logger = logging.getLogger(__name__)


class NodeExecutionEvent(Event):
    """Event for node execution results"""
    node_id: str
    result: Any
    metadata: Dict[str, Any] = {}


class WorkflowExecutionContext:
    """Context for workflow execution"""
    def __init__(self, workflow_id: str, execution_id: str):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.node_results: Dict[str, Any] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()
        self.status = "running"
    
    def log_node_execution(self, node_id: str, status: str, result: Any = None, error: str = None):
        """Log node execution details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node_id,
            "status": status,
            "result": result,
            "error": error
        }
        self.execution_log.append(log_entry)
        
        if result is not None:
            self.node_results[node_id] = result
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "duration": (datetime.utcnow() - self.start_time).total_seconds(),
            "node_results": self.node_results,
            "execution_log": self.execution_log
        }


class DynamicWorkflow(Workflow):
    """Dynamic workflow that can be configured with visual nodes"""
    
    def __init__(self, visual_workflow: VisualWorkflow, node_registry: NodeTypeRegistry):
        super().__init__()
        self.visual_workflow = visual_workflow
        self.node_registry = node_registry
        self.execution_context = WorkflowExecutionContext(
            workflow_id=visual_workflow.workflow_id,
            execution_id=str(uuid.uuid4())
        )
        
        # Build execution graph
        self.execution_graph = self._build_execution_graph()
        self.trigger_nodes = self._find_trigger_nodes()
    
    def _build_execution_graph(self) -> Dict[str, List[str]]:
        """Build execution graph from node connections"""
        graph = {}
        
        # Initialize all nodes
        for node in self.visual_workflow.visual_data.nodes:
            graph[node.node_id] = []
        
        # Add connections
        for connection in self.visual_workflow.visual_data.connections:
            source_id = connection.source_node_id
            target_id = connection.target_node_id
            
            if source_id not in graph:
                graph[source_id] = []
            graph[source_id].append(target_id)
        
        return graph
    
    def _find_trigger_nodes(self) -> List[VisualNode]:
        """Find trigger nodes (nodes with no incoming connections)"""
        incoming_connections = set()
        for connection in self.visual_workflow.visual_data.connections:
            incoming_connections.add(connection.target_node_id)
        
        trigger_nodes = []
        for node in self.visual_workflow.visual_data.nodes:
            if node.node_id not in incoming_connections:
                node_type = self.node_registry.get_node_type(node.node_type_id)
                if node_type and node_type.category == "triggers":
                    trigger_nodes.append(node)
        
        return trigger_nodes
    
    @step
    async def process_start(self, ctx: Context, ev: StartEvent) -> NodeExecutionEvent:
        """Process workflow start event"""
        logger.info(f"Starting workflow execution: {self.execution_context.execution_id}")
        
        # Find and execute first trigger node
        if self.trigger_nodes:
            first_trigger = self.trigger_nodes[0]
            result = await self._execute_node(first_trigger, {})            
            return NodeExecutionEvent(
                node_id=first_trigger.node_id,
                result=result,
                metadata={"is_trigger": True}
            )
        else:
            # No trigger nodes found, start with first node
            if self.visual_workflow.visual_data.nodes:
                first_node = self.visual_workflow.visual_data.nodes[0]
                result = await self._execute_node(first_node, {})
                
                return NodeExecutionEvent(
                    node_id=first_node.node_id,
                    result=result
                )
            else:
                self.execution_context.status = "completed"
                return StopEvent(result={"message": "No nodes to execute"})
    
    @step
    async def process_node_execution(self, ctx: Context, ev: NodeExecutionEvent) -> List[NodeExecutionEvent]:
        """Process node execution results and trigger dependent nodes"""
        node_id = ev.node_id
        result = ev.result
        
        # Log execution
        self.execution_context.log_node_execution(node_id, "completed", result)
        
        # Get dependent nodes
        dependent_node_ids = self.execution_graph.get(node_id, [])
        
        if not dependent_node_ids:
            # No dependent nodes, workflow complete
            self.execution_context.status = "completed"
            return [StopEvent(result=self.execution_context.get_execution_summary())]
        
        # Execute dependent nodes
        dependent_events = []
        for dependent_id in dependent_node_ids:
            dependent_node = self._find_node_by_id(dependent_id)
            if dependent_node:
                # Check if all dependencies are satisfied
                if await self._are_dependencies_satisfied(dependent_node):
                    try:
                        # Get input data from previous nodes
                        input_data = self._gather_input_data(dependent_node)
                        
                        # Execute dependent node
                        dependent_result = await self._execute_node(dependent_node, input_data)
                        
                        dependent_events.append(NodeExecutionEvent(
                            node_id=dependent_id,
                            result=dependent_result
                        ))
                    except Exception as e:
                        logger.error(f"Error executing node {dependent_id}: {str(e)}")
                        self.execution_context.log_node_execution(
                            dependent_id, "error", error=str(e)
                        )
        
        return dependent_events
    
    async def _execute_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Any:
        """Execute a single node based on its type"""
        node_type = self.node_registry.get_node_type(node.node_type_id)
        if not node_type:
            raise ValueError(f"Unknown node type: {node.node_type_id}")
        
        logger.info(f"Executing node: {node.node_id} (type: {node.node_type_id})")
        
        try:
            # Execute based on node type
            if node_type.id == "ai_model":
                return await self._execute_ai_model_node(node, input_data)
            elif node_type.id == "data_transformer":
                return await self._execute_data_transformer_node(node, input_data)
            elif node_type.id == "http_request":
                return await self._execute_http_request_node(node, input_data)
            elif node_type.id == "condition":
                return await self._execute_condition_node(node, input_data)
            elif node_type.id.endswith("_trigger"):
                return await self._execute_trigger_node(node, input_data)
            else:
                # Generic node execution
                return await self._execute_generic_node(node, input_data)
                
        except Exception as e:
            logger.error(f"Node execution failed: {node.node_id} - {str(e)}")
            raise
    
    async def _execute_ai_model_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI model node"""
        config = node.config
        
        # Extract configuration
        provider = config.get("provider", "OpenAI")
        model = config.get("model", "gpt-3.5-turbo")
        prompt = config.get("prompt", "")
        temperature = config.get("temperature", 0.7)
        
        # Get input text
        input_text = input_data.get("text", input_data.get("input", ""))
        
        # Build full prompt
        full_prompt = f"{prompt}\n\nInput: {input_text}" if input_text else prompt
        
        # TODO: Implement actual AI model execution
        # For now, return mock response
        result = {
            "provider": provider,
            "model": model,
            "prompt": full_prompt,
            "response": f"AI response for: {full_prompt[:100]}...",
            "temperature": temperature,
            "usage": {
                "prompt_tokens": len(full_prompt.split()),
                "completion_tokens": 50,
                "total_tokens": len(full_prompt.split()) + 50
            }
        }
        
        return result
    
    async def _execute_data_transformer_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Any:
        """Execute data transformer node"""
        config = node.config
        operation = config.get("operation", "filter")
        expression = config.get("expression", "")
        
        # Get input data
        data = input_data.get("data", input_data)
        
        # TODO: Implement actual data transformation
        # For now, return mock transformation
        result = {
            "operation": operation,
            "expression": expression,
            "input_data": data,
            "transformed_data": f"Transformed: {data}",
            "transformation_applied": True
        }
        
        return result
    
    async def _execute_http_request_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request node"""
        config = node.config
        
        url = config.get("url", "")
        method = config.get("method", "GET")
        headers = config.get("headers", {})
        body = config.get("body", "")
        
        # TODO: Implement actual HTTP request
        # For now, return mock response
        result = {
            "url": url,
            "method": method,
            "headers": headers,
            "body": body,
            "status_code": 200,
            "response": {"message": "Mock HTTP response"},
            "request_time": datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _execute_condition_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute condition node"""
        config = node.config
        
        condition_type = config.get("condition_type", "equals")
        value1 = config.get("value1", "")
        value2 = config.get("value2", "")
        
        # TODO: Implement actual condition evaluation
        result = {
            "condition_type": condition_type,
            "value1": value1,
            "value2": value2,
            "result": True,  # Mock result
            "evaluation_time": datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _execute_trigger_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trigger node"""
        config = node.config
        
        result = {
            "trigger_type": node.node_type_id,
            "trigger_name": config.get("name", node.name),
            "triggered": True,
            "trigger_time": datetime.utcnow().isoformat(),
            "trigger_data": input_data
        }
        
        return result
    
    async def _execute_generic_node(self, node: VisualNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic node"""
        return {
            "node_id": node.node_id,
            "node_type": node.node_type_id,
            "input_data": input_data,
            "config": node.config,
            "execution_time": datetime.utcnow().isoformat(),
            "status": "completed"
        }
    
    def _find_node_by_id(self, node_id: str) -> Optional[VisualNode]:
        """Find node by ID"""
        for node in self.visual_workflow.visual_data.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    async def _are_dependencies_satisfied(self, node: VisualNode) -> bool:
        """Check if all dependencies for a node are satisfied"""
        # Find all incoming connections for this node
        incoming_connections = [
            conn for conn in self.visual_workflow.visual_data.connections
            if conn.target_node_id == node.node_id
        ]
        
        # Check if all source nodes have been executed
        for connection in incoming_connections:
            if connection.source_node_id not in self.execution_context.node_results:
                return False
        
        return True
    
    def _gather_input_data(self, node: VisualNode) -> Dict[str, Any]:
        """Gather input data from previous nodes"""
        input_data = {}
        
        # Find all incoming connections
        incoming_connections = [
            conn for conn in self.visual_workflow.visual_data.connections
            if conn.target_node_id == node.node_id
        ]
        
        # Gather data from source nodes
        for connection in incoming_connections:
            source_result = self.execution_context.node_results.get(connection.source_node_id)
            if source_result:
                # Map source output to target input
                source_output = connection.source_output or "result"
                target_input = connection.target_input or "input"
                
                if isinstance(source_result, dict) and source_output in source_result:
                    input_data[target_input] = source_result[source_output]
                else:
                    input_data[target_input] = source_result
        
        return input_data


class VisualWorkflowExecutor:
    """Service for executing visual workflows"""
    
    def __init__(self, node_registry: NodeTypeRegistry):
        self.node_registry = node_registry
        self.active_executions: Dict[str, WorkflowExecutionContext] = {}
    
    async def execute_workflow(self, visual_workflow: VisualWorkflow, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a visual workflow"""
        try:
            # Create dynamic workflow
            workflow = DynamicWorkflow(visual_workflow, self.node_registry)
            
            # Store execution context
            self.active_executions[workflow.execution_context.execution_id] = workflow.execution_context
            
            # Execute workflow
            result = await workflow.run(input_data or {})
            
            # Update execution status
            workflow.execution_context.status = "completed"
            
            return workflow.execution_context.get_execution_summary()
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            if hasattr(workflow, 'execution_context'):
                workflow.execution_context.status = "failed"
                workflow.execution_context.log_node_execution(
                    "workflow", "error", error=str(e)
                )
                return workflow.execution_context.get_execution_summary()
            else:
                return {
                    "workflow_id": visual_workflow.workflow_id,
                    "status": "failed",
                    "error": str(e),
                    "execution_time": datetime.utcnow().isoformat()
                }
    
    async def execute_node_preview(self, node: VisualNode, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a single node for preview/testing"""
        try:
            # Create a minimal workflow with just this node
            visual_data = type('VisualData', (), {
                'nodes': [node],
                'connections': []
            })()
            
            mock_workflow = type('MockWorkflow', (), {
                'workflow_id': f"preview-{node.node_id}",
                'visual_data': visual_data
            })()
            
            # Create workflow and execute node
            workflow = DynamicWorkflow(mock_workflow, self.node_registry)
            result = await workflow._execute_node(node, input_data or {})
            
            return {
                "node_id": node.node_id,
                "node_type": node.node_type_id,
                "status": "completed",
                "result": result,
                "execution_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Node preview execution failed: {str(e)}")
            return {
                "node_id": node.node_id,
                "node_type": node.node_type_id,
                "status": "failed",
                "error": str(e),
                "execution_time": datetime.utcnow().isoformat()
            }
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        context = self.active_executions.get(execution_id)
        if context:
            return context.get_execution_summary()
        return None
    
    def list_active_executions(self) -> List[Dict[str, Any]]:
        """List all active executions"""
        return [
            context.get_execution_summary()
            for context in self.active_executions.values()
            if context.status == "running"
        ]
