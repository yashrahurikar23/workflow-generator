"""
Visual Workflow API endpoints with Enhanced Real-time Execution
"""
import uuid
from datetime import datetime
from typing import AsyncGenerator, List, Optional

from app.core.database import get_database
from app.models.workflow_visual import (NodeCategory, NodeType,
                                        VisualWorkflowData, Workflow,
                                        WorkflowBase, WorkflowNode,
                                        WorkflowStatus)
from app.services.enhanced_workflow_executor import (
    EnhancedVisualWorkflowExecutor, ExecutionStatus, NodeStatus)
from app.services.node_registry import node_registry
from fastapi import (APIRouter, Depends, HTTPException, Query, WebSocket,
                     WebSocketDisconnect)
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

# Create enhanced executor instance
workflow_executor = EnhancedVisualWorkflowExecutor(node_registry)


@router.get("/node-types", response_model=List[NodeType])
async def get_node_types(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search node types")
) -> List[NodeType]:
    """Get available node types for the visual editor"""
    
    if search:
        return node_registry.search_node_types(search)
    elif category:
        return node_registry.get_node_types_by_category(category)
    else:
        return node_registry.get_all_node_types()


@router.get("/node-types/{node_type_id}", response_model=NodeType)
async def get_node_type(node_type_id: str) -> NodeType:
    """Get details of a specific node type"""
    
    node_type = node_registry.get_node_type(node_type_id)
    if not node_type:
        raise HTTPException(status_code=404, detail="Node type not found")
    
    return node_type


@router.get("/categories", response_model=List[NodeCategory])
async def get_node_categories() -> List[NodeCategory]:
    """Get all node categories"""
    return node_registry.get_all_categories()


@router.get("/categories/{category_id}", response_model=NodeCategory)
async def get_node_category(category_id: str) -> NodeCategory:
    """Get details of a specific node category"""
    
    category = node_registry.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


@router.post("/visual-workflows", response_model=Workflow)
async def create_visual_workflow(
    workflow_data: WorkflowBase,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Workflow:
    """Create a new visual workflow"""
    
    # Validate that it's a visual workflow
    if workflow_data.workflow_type != "visual" or not workflow_data.visual_data:
        raise HTTPException(status_code=400, detail="Invalid visual workflow data")
    
    # Validate nodes and connections
    await _validate_visual_workflow(workflow_data.visual_data)
    
    # Generate workflow ID and create workflow
    import uuid
    from datetime import datetime
    
    workflow = Workflow(
        workflow_id=str(uuid.uuid4()),
        **workflow_data.dict(),
        status=WorkflowStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    await db.workflows.insert_one(workflow.dict())
    
    return workflow


@router.put("/visual-workflows/{workflow_id}", response_model=Workflow)
async def update_visual_workflow(
    workflow_id: str,
    workflow_data: WorkflowBase,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Workflow:
    """Update an existing visual workflow"""
    
    # Check if workflow exists
    existing_workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not existing_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Validate visual workflow data
    if workflow_data.workflow_type == "visual" and workflow_data.visual_data:
        await _validate_visual_workflow(workflow_data.visual_data)
    
    # Update workflow
    update_data = workflow_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.workflows.update_one(
        {"workflow_id": workflow_id},
        {"$set": update_data}
    )
    
    # Return updated workflow
    updated_workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    return Workflow(**updated_workflow)


@router.get("/visual-workflows/{workflow_id}", response_model=Workflow)
async def get_visual_workflow(
    workflow_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Workflow:
    """Get a specific visual workflow"""
    
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return Workflow(**workflow)


@router.post("/visual-workflows/{workflow_id}/validate")
async def validate_visual_workflow(
    workflow_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Validate a visual workflow for errors"""
    
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_obj = Workflow(**workflow)
    
    if workflow_obj.workflow_type != "visual" or not workflow_obj.visual_data:
        raise HTTPException(status_code=400, detail="Not a visual workflow")
    
    validation_result = await _validate_visual_workflow(workflow_obj.visual_data)
    
    return {
        "valid": validation_result["valid"],
        "errors": validation_result["errors"],
        "warnings": validation_result["warnings"]
    }


@router.post("/visual-workflows/{workflow_id}/execute")
async def execute_visual_workflow(
    workflow_id: str,
    input_data: dict = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Execute a visual workflow"""
    
    # Get workflow
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_obj = Workflow(**workflow)
    
    # Check if it's a visual workflow
    if workflow_obj.workflow_type != "visual" or not workflow_obj.visual_data:
        raise HTTPException(status_code=400, detail="Not a visual workflow")
    
    try:
        # Execute workflow
        result = await workflow_executor.execute_workflow(workflow_obj, input_data or {})
        
        # Update execution count
        await db.workflows.update_one(
            {"workflow_id": workflow_id},
            {"$inc": {"execution_count": 1}, "$set": {"last_executed_at": datetime.utcnow()}}
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/visual-workflows/{workflow_id}/nodes/{node_id}/execute")
async def execute_node_preview(
    workflow_id: str,
    node_id: str,
    input_data: dict = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Execute a single node for preview/testing"""
    
    # Get workflow
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_obj = Workflow(**workflow)
    
    # Check if it's a visual workflow
    if workflow_obj.workflow_type != "visual" or not workflow_obj.visual_data:
        raise HTTPException(status_code=400, detail="Not a visual workflow")
    
    # Find the node
    node = None
    for n in workflow_obj.visual_data.nodes:
        if n.node_id == node_id:
            node = n
            break
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    try:
        # Execute node preview
        result = await workflow_executor.execute_node_preview(node, input_data or {})
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node execution failed: {str(e)}")


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str) -> dict:
    """Get workflow execution status"""
    
    result = workflow_executor.get_execution_status(execution_id)
    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return result


@router.get("/executions")
async def list_active_executions() -> List[dict]:
    """List all active workflow executions"""
    return workflow_executor.list_active_executions()


@router.post("/visual-workflows/{workflow_id}/convert-to-llamaindex")
async def convert_to_llamaindex_workflow(
    workflow_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Convert visual workflow to LlamaIndex workflow format for export"""
    
    # Get workflow
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_obj = Workflow(**workflow)
    
    # Check if it's a visual workflow
    if workflow_obj.workflow_type != "visual" or not workflow_obj.visual_data:
        raise HTTPException(status_code=400, detail="Not a visual workflow")
    
    try:
        # Convert to LlamaIndex format
        llamaindex_workflow = await _convert_to_llamaindex_format(workflow_obj)
        return {
            "workflow_id": workflow_id,
            "llamaindex_workflow": llamaindex_workflow,
            "conversion_time": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


# Enhanced Execution Control Endpoints

@router.post("/visual-workflows/{workflow_id}/execute-enhanced")
async def execute_visual_workflow_enhanced(
    workflow_id: str,
    input_data: dict = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Execute a visual workflow with enhanced real-time tracking"""
    
    # Get workflow
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_obj = Workflow(**workflow)
    
    # Check if it's a visual workflow
    if workflow_obj.workflow_type != "visual" or not workflow_obj.visual_data:
        raise HTTPException(status_code=400, detail="Not a visual workflow")
    
    try:
        # Start enhanced execution
        execution_id = await workflow_executor.start_execution(
            workflow_obj, input_data or {}
        )
        
        # Update execution count
        await db.workflows.update_one(
            {"workflow_id": workflow_id},
            {"$inc": {"execution_count": 1}, "$set": {"last_executed_at": datetime.utcnow()}}
        )
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Workflow execution started successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/visual-workflows/{workflow_id}/status")
async def get_workflow_status(
    workflow_id: str,
    execution_id: Optional[str] = Query(None, description="Specific execution ID")
) -> dict:
    """Get current execution status of a workflow"""
    
    try:
        if execution_id:
            status = await workflow_executor.get_execution_status(execution_id)
        else:
            # Get latest execution status for the workflow
            executions = workflow_executor.list_active_executions()
            workflow_executions = [e for e in executions if e.get("workflow_id") == workflow_id]
            if not workflow_executions:
                return {"status": "no_active_executions", "workflow_id": workflow_id}
            status = workflow_executions[0]  # Most recent
        
        return status
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/visual-workflows/{workflow_id}/pause")
async def pause_workflow_execution(
    workflow_id: str,
    execution_id: str = Query(..., description="Execution ID to pause")
) -> dict:
    """Pause an active workflow execution"""
    
    try:
        success = await workflow_executor.pause_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be paused")
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "paused",
            "message": "Workflow execution paused successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause execution: {str(e)}")


@router.post("/visual-workflows/{workflow_id}/resume")
async def resume_workflow_execution(
    workflow_id: str,
    execution_id: str = Query(..., description="Execution ID to resume")
) -> dict:
    """Resume a paused workflow execution"""
    
    try:
        success = await workflow_executor.resume_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be resumed")
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "resumed",
            "message": "Workflow execution resumed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume execution: {str(e)}")


@router.post("/visual-workflows/{workflow_id}/cancel")
async def cancel_workflow_execution(
    workflow_id: str,
    execution_id: str = Query(..., description="Execution ID to cancel")
) -> dict:
    """Cancel an active workflow execution"""
    
    try:
        success = await workflow_executor.cancel_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "cancelled",
            "message": "Workflow execution cancelled successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel execution: {str(e)}")


@router.get("/visual-workflows/{workflow_id}/logs")
async def get_workflow_execution_logs(
    workflow_id: str,
    execution_id: Optional[str] = Query(None, description="Specific execution ID"),
    limit: int = Query(100, description="Maximum number of log entries"),
    offset: int = Query(0, description="Offset for pagination")
) -> dict:
    """Get execution logs for a workflow"""
    
    try:
        logs = await workflow_executor.get_execution_logs(
            workflow_id=workflow_id,
            execution_id=execution_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "logs": logs,
            "total_count": len(logs),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.websocket("/visual-workflows/{workflow_id}/stream")
async def workflow_status_websocket(
    websocket: WebSocket,
    workflow_id: str,
    execution_id: Optional[str] = Query(None, description="Specific execution ID to monitor")
):
    """WebSocket endpoint for real-time workflow status updates"""
    
    await websocket.accept()
    
    try:
        # Stream real-time status updates
        async for status_update in workflow_executor.get_status_stream(
            workflow_id=workflow_id,
            execution_id=execution_id
        ):
            await websocket.send_json({
                "execution_id": status_update.execution_id,
                "node_id": status_update.node_id,
                "status": status_update.status,
                "timestamp": status_update.timestamp.isoformat(),
                "data": status_update.data
            })
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for workflow {workflow_id}")
    except Exception as e:
        print(f"WebSocket error for workflow {workflow_id}: {str(e)}")
        try:
            await websocket.send_json({
                "error": f"WebSocket error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
        except:
            pass  # Connection may already be closed
    finally:
        try:
            await websocket.close()
        except:
            pass  # Connection may already be closed


async def _validate_visual_workflow(visual_data: VisualWorkflowData) -> dict:
    """Validate visual workflow data"""
    errors = []
    warnings = []
    
    # Check if there are nodes
    if not visual_data.nodes:
        errors.append("Workflow must have at least one node")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    # Validate each node
    node_ids = set()
    for node in visual_data.nodes:
        # Check for duplicate node IDs
        if node.node_id in node_ids:
            errors.append(f"Duplicate node ID: {node.node_id}")
        node_ids.add(node.node_id)
        
        # Check if node type exists
        node_type = node_registry.get_node_type(node.node_type_id)
        if not node_type:
            errors.append(f"Unknown node type: {node.node_type_id} for node {node.node_id}")
            continue
        
        # Validate node configuration
        for field in node_type.config_fields:
            if field.required and field.key not in node.config:
                errors.append(f"Missing required field '{field.key}' in node {node.node_id}")
    
    # Validate connections
    for connection in visual_data.connections:
        # Check if source and target nodes exist
        if connection.source_node_id not in node_ids:
            errors.append(f"Connection references non-existent source node: {connection.source_node_id}")
        
        if connection.target_node_id not in node_ids:
            errors.append(f"Connection references non-existent target node: {connection.target_node_id}")
    
    # Check for isolated nodes (nodes with no connections)
    connected_nodes = set()
    for connection in visual_data.connections:
        connected_nodes.add(connection.source_node_id)
        connected_nodes.add(connection.target_node_id)
    
    isolated_nodes = node_ids - connected_nodes
    if len(isolated_nodes) > 1:  # Allow one isolated node (could be trigger)
        warnings.append(f"Isolated nodes detected: {', '.join(isolated_nodes)}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


async def _convert_visual_to_llamaindex(visual_data: VisualWorkflowData) -> dict:
    """Convert visual workflow to LlamaIndex workflow format"""
    
    # This is a placeholder implementation
    # In a real implementation, this would generate actual LlamaIndex workflow code
    
    steps = []
    events = []
    
    # Generate events for each node type
    for node in visual_data.nodes:
        event_name = f"{node.name.replace(' ', '')}Event"
        events.append({
            "name": event_name,
            "node_id": node.node_id,
            "node_type": node.node_type_id
        })
    
    # Generate steps for each node
    for node in visual_data.nodes:
        step = {
            "step_name": f"step_{node.node_id}",
            "node_id": node.node_id,
            "node_type": node.node_type_id,
            "config": node.config,
            "dependencies": []
        }
        
        # Find dependencies from connections
        for connection in visual_data.connections:
            if connection.target_node_id == node.node_id:
                step["dependencies"].append(connection.source_node_id)
        
        steps.append(step)
    
    return {
        "events": events,
        "steps": steps,
        "workflow_class": "GeneratedWorkflow",
        "metadata": {
            "node_count": len(visual_data.nodes),
            "connection_count": len(visual_data.connections)
        }
    }


async def _convert_to_llamaindex_format(workflow: Workflow) -> dict:
    """Convert visual workflow to LlamaIndex workflow format"""
    
    # Build LlamaIndex workflow structure
    llamaindex_workflow = {
        "workflow_name": workflow.name,
        "description": workflow.description,
        "steps": [],
        "connections": []
    }
    
    # Convert nodes to steps
    for node in workflow.visual_data.nodes:
        node_type = node_registry.get_node_type(node.node_type_id)
        
        step = {
            "step_id": node.node_id,
            "name": node.name,
            "step_type": node.node_type_id,
            "description": f"Visual node: {node.name}",
            "config": node.config,
            "depends_on": [],  # Will be filled from connections
            "node_type_info": {
                "category": node_type.category if node_type else "unknown",
                "description": node_type.description if node_type else "",
                "inputs": [input.dict() for input in node_type.inputs] if node_type else [],
                "outputs": [output.dict() for output in node_type.outputs] if node_type else []
            }
        }
        
        llamaindex_workflow["steps"].append(step)
    
    # Convert connections to dependencies
    for connection in workflow.visual_data.connections:
        # Find target step and add source as dependency
        for step in llamaindex_workflow["steps"]:
            if step["step_id"] == connection.target_node_id:
                if connection.source_node_id not in step["depends_on"]:
                    step["depends_on"].append(connection.source_node_id)
        
        # Add connection info
        llamaindex_workflow["connections"].append({
            "source": connection.source_node_id,
            "target": connection.target_node_id,
            "source_output": connection.source_output,
            "target_input": connection.target_input
        })
    
    return llamaindex_workflow


@router.get("/visual-workflows/{workflow_id}/execution-preview")
async def get_workflow_execution_preview(
    workflow_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """Get a preview of how the workflow would execute"""
    
    workflow = await db.workflows.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_obj = Workflow(**workflow)
    
    if workflow_obj.workflow_type != "visual" or not workflow_obj.visual_data:
        raise HTTPException(status_code=400, detail="Not a visual workflow")
    
    # Generate execution preview
    execution_order = []
    node_map = {node.node_id: node for node in workflow_obj.visual_data.nodes}
    
    # Simple topological sort for execution order
    dependencies = {}
    for connection in workflow_obj.visual_data.connections:
        if connection.target_node_id not in dependencies:
            dependencies[connection.target_node_id] = []
        dependencies[connection.target_node_id].append(connection.source_node_id)
    
    # Find nodes with no dependencies (starting points)
    start_nodes = [node.node_id for node in workflow_obj.visual_data.nodes 
                   if node.node_id not in dependencies]
    
    execution_order.extend(start_nodes)
    
    # Add remaining nodes based on dependencies (simplified)
    remaining_nodes = [node.node_id for node in workflow_obj.visual_data.nodes 
                      if node.node_id not in start_nodes]
    execution_order.extend(remaining_nodes)
    
    return {
        "execution_order": execution_order,
        "estimated_steps": len(execution_order),
        "parallel_opportunities": len([node for node in workflow_obj.visual_data.nodes 
                                     if node.node_id not in dependencies]) - 1,
        "preview": [
            {
                "step": i + 1,
                "node_id": node_id,
                "node_name": node_map[node_id].name,
                "node_type": node_map[node_id].node_type_id
            }
            for i, node_id in enumerate(execution_order)
        ]
    }
