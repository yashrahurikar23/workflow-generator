"""
Workflow-specific tools for LlamaIndex agents
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.schemas.workflow_agent_schemas import (NodePosition, NodeType,
                                                WorkflowConnectionSchema,
                                                WorkflowNodeSchema)
from llama_index.core.tools import FunctionTool

logger = logging.getLogger(__name__)

class WorkflowTools:
    """Collection of tools for workflow generation and manipulation"""
    
    @staticmethod
    def create_workflow_node_tool() -> FunctionTool:
        """Tool to create a new workflow node"""
        
        def create_workflow_node(
            node_type: str,
            name: str,
            description: str,
            x_position: float = 100.0,
            y_position: float = 100.0,
            config: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Create a new workflow node with the specified parameters.
            
            Args:
                node_type: Type of node (web_scraper, ai_processor, email_trigger, etc.)
                name: Human-readable name for the node
                description: Description of what this node does
                x_position: X coordinate for visual positioning (default: 100.0)
                y_position: Y coordinate for visual positioning (default: 100.0)
                config: Optional configuration dictionary for the node
                
            Returns:
                Dictionary representation of the created node
            """
            try:
                # Validate node type
                try:
                    node_type_enum = NodeType(node_type)
                except ValueError:
                    logger.warning(f"Unknown node type: {node_type}, using web_scraper as default")
                    node_type_enum = NodeType.WEB_SCRAPER
                
                # Get default inputs/outputs based on node type
                node_templates = WorkflowTools._get_node_templates()
                template = node_templates.get(node_type, {
                    "inputs": [], 
                    "outputs": [], 
                    "default_config": {}
                })
                
                # Merge default config with provided config
                final_config = {**template.get("default_config", {})}
                if config:
                    final_config.update(config)
                
                node = WorkflowNodeSchema(
                    node_id=str(uuid.uuid4()),
                    node_type=node_type_enum,
                    name=name,
                    description=description,
                    position=NodePosition(x=x_position, y=y_position),
                    config=final_config,
                    inputs=template.get("inputs", []),
                    outputs=template.get("outputs", [])
                )
                
                result = node.model_dump()
                logger.info(f"Created node: {name} ({node_type})")
                return result
                
            except Exception as e:
                logger.error(f"Failed to create workflow node: {str(e)}")
                return {"error": f"Failed to create node: {str(e)}"}
        
        return FunctionTool.from_defaults(
            fn=create_workflow_node,
            name="create_workflow_node",
            description="Create a new workflow node with specified type, name, description and configuration"
        )
    
    @staticmethod
    def create_connection_tool() -> FunctionTool:
        """Tool to create connections between workflow nodes"""
        
        def create_connection(
            source_node_id: str,
            target_node_id: str,
            source_output: str,
            target_input: str
        ) -> Dict[str, Any]:
            """
            Create a connection between two workflow nodes.
            
            Args:
                source_node_id: ID of the source node
                target_node_id: ID of the target node
                source_output: Output parameter from the source node
                target_input: Input parameter for the target node
                
            Returns:
                Dictionary representation of the created connection
            """
            try:
                connection = WorkflowConnectionSchema(
                    connection_id=str(uuid.uuid4()),
                    source_node_id=source_node_id,
                    target_node_id=target_node_id,
                    source_output=source_output,
                    target_input=target_input
                )
                
                result = connection.model_dump()
                logger.info(f"Created connection: {source_node_id}[{source_output}] -> {target_node_id}[{target_input}]")
                return result
                
            except Exception as e:
                logger.error(f"Failed to create connection: {str(e)}")
                return {"error": f"Failed to create connection: {str(e)}"}
        
        return FunctionTool.from_defaults(
            fn=create_connection,
            name="create_connection",
            description="Create a connection between two workflow nodes"
        )
    
    @staticmethod
    def validate_workflow_tool() -> FunctionTool:
        """Tool to validate a complete workflow structure"""
        
        def validate_workflow(
            nodes: List[Dict[str, Any]],
            connections: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """
            Validate a workflow structure for consistency and completeness.
            
            Args:
                nodes: List of workflow nodes
                connections: List of connections between nodes
                
            Returns:
                Dictionary with validation results
            """
            try:
                issues = []
                warnings = []
                
                # Check for orphaned nodes
                connected_nodes = set()
                for conn in connections:
                    connected_nodes.add(conn.get("source_node_id"))
                    connected_nodes.add(conn.get("target_node_id"))
                
                node_ids = {node.get("node_id") for node in nodes}
                orphaned_nodes = node_ids - connected_nodes
                
                if orphaned_nodes and len(nodes) > 1:
                    warnings.append(f"Orphaned nodes detected: {list(orphaned_nodes)}")
                
                # Check for invalid connections
                for conn in connections:
                    source_id = conn.get("source_node_id")
                    target_id = conn.get("target_node_id")
                    
                    if source_id not in node_ids:
                        issues.append(f"Connection references non-existent source node: {source_id}")
                    if target_id not in node_ids:
                        issues.append(f"Connection references non-existent target node: {target_id}")
                
                # Check for circular dependencies (simple cycle detection)
                # Build adjacency list
                graph = {}
                for node in nodes:
                    graph[node.get("node_id")] = []
                
                for conn in connections:
                    source = conn.get("source_node_id")
                    target = conn.get("target_node_id")
                    if source in graph:
                        graph[source].append(target)
                
                # Simple DFS cycle detection
                visited = set()
                rec_stack = set()
                
                def has_cycle(node):
                    if node in rec_stack:
                        return True
                    if node in visited:
                        return False
                    
                    visited.add(node)
                    rec_stack.add(node)
                    
                    for neighbor in graph.get(node, []):
                        if has_cycle(neighbor):
                            return True
                    
                    rec_stack.remove(node)
                    return False
                
                for node_id in graph:
                    if node_id not in visited:
                        if has_cycle(node_id):
                            issues.append("Circular dependency detected in workflow")
                            break
                
                is_valid = len(issues) == 0
                
                result = {
                    "valid": is_valid,
                    "issues": issues,
                    "warnings": warnings,
                    "node_count": len(nodes),
                    "connection_count": len(connections)
                }
                
                logger.info(f"Workflow validation: {'PASSED' if is_valid else 'FAILED'} ({len(issues)} issues, {len(warnings)} warnings)")
                return result
                
            except Exception as e:
                logger.error(f"Failed to validate workflow: {str(e)}")
                return {
                    "valid": False,
                    "issues": [f"Validation error: {str(e)}"],
                    "warnings": [],
                    "node_count": 0,
                    "connection_count": 0
                }
        
        return FunctionTool.from_defaults(
            fn=validate_workflow,
            name="validate_workflow",
            description="Validate a workflow structure for consistency and completeness"
        )
    
    @staticmethod
    def get_node_template_tool() -> FunctionTool:
        """Tool to get node templates and capabilities"""
        
        def get_node_template(node_type: str) -> Dict[str, Any]:
            """
            Get template information for a specific node type.
            
            Args:
                node_type: Type of node to get template for
                
            Returns:
                Template information including inputs, outputs, and default config
            """
            templates = WorkflowTools._get_node_templates()
            return templates.get(node_type, {
                "inputs": [],
                "outputs": [],
                "default_config": {},
                "description": "Unknown node type"
            })
        
        return FunctionTool.from_defaults(
            fn=get_node_template,
            name="get_node_template",
            description="Get template information for a specific workflow node type"
        )
    
    @staticmethod
    def _get_node_templates() -> Dict[str, Dict[str, Any]]:
        """Get all available node templates"""
        return {
            "web_scraper": {
                "description": "Scrapes content from web pages",
                "inputs": ["url"],
                "outputs": ["scraped_content", "metadata", "links"],
                "default_config": {
                    "timeout": 30,
                    "user_agent": "WorkflowBot/1.0",
                    "selectors": {
                        "title": "h1, title",
                        "content": ".content, article, main",
                        "links": "a[href]"
                    },
                    "follow_redirects": True,
                    "max_retries": 3
                }
            },
            "ai_processor": {
                "description": "Processes content using AI/LLM",
                "inputs": ["content", "prompt"],
                "outputs": ["processed_content", "analysis", "summary"],
                "default_config": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "system_prompt": "You are a helpful content processor."
                }
            },
            "email_trigger": {
                "description": "Monitors email for incoming messages",
                "inputs": [],
                "outputs": ["email_data", "sender", "subject", "body"],
                "default_config": {
                    "check_interval": 300,
                    "email_provider": "gmail",
                    "filters": {
                        "unread_only": True,
                        "from_addresses": [],
                        "subject_keywords": []
                    }
                }
            },
            "notification": {
                "description": "Sends notifications via various channels",
                "inputs": ["message", "subject", "data"],
                "outputs": ["notification_status", "delivery_id"],
                "default_config": {
                    "channels": ["email"],
                    "recipients": [],
                    "template": "default"
                }
            },
            "file_storage": {
                "description": "Stores data to files or cloud storage",
                "inputs": ["content", "filename", "metadata"],
                "outputs": ["file_path", "storage_status", "file_url"],
                "default_config": {
                    "storage_type": "local",
                    "path": "/tmp/workflows",
                    "format": "json",
                    "compression": False
                }
            },
            "http_request": {
                "description": "Makes HTTP requests to external APIs",
                "inputs": ["url", "method", "headers", "payload"],
                "outputs": ["response_data", "status_code", "headers"],
                "default_config": {
                    "method": "GET",
                    "timeout": 30,
                    "follow_redirects": True,
                    "verify_ssl": True
                }
            },
            "data_transformer": {
                "description": "Transforms and processes data",
                "inputs": ["input_data", "transformation_rules"],
                "outputs": ["transformed_data", "metadata"],
                "default_config": {
                    "transformation_type": "json_transform",
                    "validation": True,
                    "error_handling": "continue"
                }
            },
            "condition": {
                "description": "Conditional logic node for workflow branching",
                "inputs": ["input_data", "condition_rules"],
                "outputs": ["condition_result", "matched_branch"],
                "default_config": {
                    "condition_type": "simple",
                    "default_branch": "continue"
                }
            },
            "database_operation": {
                "description": "Performs database operations",
                "inputs": ["query", "data", "operation_type"],
                "outputs": ["result", "affected_rows", "metadata"],
                "default_config": {
                    "database_type": "mongodb",
                    "connection_string": "",
                    "collection": "default"
                }
            }
        }

    @staticmethod
    def get_all_tools() -> List[FunctionTool]:
        """Get all available workflow tools"""
        return [
            WorkflowTools.create_workflow_node_tool(),
            WorkflowTools.create_connection_tool(),
            WorkflowTools.validate_workflow_tool(),
            WorkflowTools.get_node_template_tool()
        ]
