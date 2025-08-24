import logging
from typing import Any, Dict, List, Optional

from app.core.database import get_database
from app.crud.workflow import WorkflowCRUD
from app.models.workflow import (Workflow, WorkflowCreateRequest,
                                 WorkflowExecuteRequest, WorkflowExecution,
                                 WorkflowExecutionResponse,
                                 WorkflowGenerateRequest, WorkflowListResponse,
                                 WorkflowResponse, WorkflowStatus,
                                 WorkflowUpdateRequest)
from app.services.workflow_generator import WorkflowGenerator
from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_workflow_crud(db = Depends(get_database)) -> WorkflowCRUD:
    """Dependency to get workflow CRUD instance"""
    return WorkflowCRUD(db)

@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow_data: WorkflowCreateRequest,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Create a new workflow"""
    try:
        workflow = await crud.create_workflow(workflow_data)
        return WorkflowResponse(**workflow.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    skip: int = Query(0, ge=0, description="Number of workflows to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of workflows to return"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    search: Optional[str] = Query(None, description="Search in workflow name and description"),
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """List workflows with filtering and pagination"""
    try:
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        result = await crud.list_workflows(
            skip=skip,
            limit=limit,
            status=status,
            tags=tag_list,
            search=search
        )
        
        return WorkflowListResponse(
            workflows=[WorkflowResponse(**w.model_dump()) for w in result["workflows"]],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Get a specific workflow by ID"""
    workflow = await crud.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowResponse(**workflow.model_dump())

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdateRequest,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Update an existing workflow"""
    workflow = await crud.update_workflow(workflow_id, workflow_data)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowResponse(**workflow.model_dump())

@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: str,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Delete a workflow"""
    success = await crud.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse, status_code=201)
async def execute_workflow(
    workflow_id: str,
    execute_data: WorkflowExecuteRequest,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Execute a workflow"""
    # First check if workflow exists
    workflow = await crud.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.status != WorkflowStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Workflow must be active to execute")
    
    try:
        execution = await crud.create_execution(workflow_id, execute_data.input_data)
        # TODO: Here we would start the actual workflow execution in the background
        # For now, we just return the execution record
        return WorkflowExecutionResponse(**execution.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {str(e)}")

@router.get("/{workflow_id}/executions")
async def list_workflow_executions(
    workflow_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """List executions for a specific workflow"""
    # Check if workflow exists
    workflow = await crud.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        result = await crud.list_executions(workflow_id=workflow_id, skip=skip, limit=limit)
        return {
            "executions": [WorkflowExecutionResponse(**e.model_dump()) for e in result["executions"]],
            "total": result["total"],
            "page": result["page"],
            "size": result["size"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list executions: {str(e)}")

@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(
    execution_id: str,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Get a specific workflow execution by ID"""
    execution = await crud.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return WorkflowExecutionResponse(**execution.model_dump())

@router.post("/generate", response_model=WorkflowResponse, status_code=201)
async def generate_workflow(
    generate_request: WorkflowGenerateRequest,
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Generate a new workflow using LLM based on natural language description"""
    try:
        generator = WorkflowGenerator()
        workflow = await generator.generate_workflow(generate_request)
        
        # Save the generated workflow
        create_request = WorkflowCreateRequest(
            name=workflow.name,
            description=workflow.description,
            steps=workflow.steps,
            tags=workflow.tags,
            parallel_execution=workflow.parallel_execution,
            timeout_minutes=workflow.timeout_minutes
        )
        
        saved_workflow = await crud.create_workflow(create_request)
        
        # Update with generation metadata
        await crud.update_workflow(
            saved_workflow.workflow_id,
            WorkflowUpdateRequest(
                status=WorkflowStatus.DRAFT,
                generated_by_llm=True,
                generation_prompt=generate_request.prompt,
                llm_provider="mock_llm"  # TODO: Use actual LLM provider info
            )
        )
        
        # Fetch the updated workflow to return with all metadata
        updated_workflow = await crud.get_workflow(saved_workflow.workflow_id)
        
        return WorkflowResponse(**updated_workflow.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate workflow: {str(e)}")

@router.post("/{workflow_id}/chat", response_model=Dict[str, Any])
async def chat_with_workflow(
    workflow_id: str,
    request_data: Dict[str, Any],
    crud: WorkflowCRUD = Depends(get_workflow_crud)
):
    """Chat with AI to update a workflow using LlamaIndex agents"""
    try:
        # Import here to avoid circular imports
        from app.agents.base_agent import WorkflowAgentOrchestrator
        from app.agents.workflow_builder import WorkflowBuilderAgent
        from app.agents.workflow_planner import WorkflowPlannerAgent

        # Get the current workflow
        workflow = await crud.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        message = request_data.get("message", "")
        current_workflow = request_data.get("current_workflow", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize the agent orchestrator
        orchestrator = WorkflowAgentOrchestrator()
        
        # Register agents
        planner_agent = WorkflowPlannerAgent()
        builder_agent = WorkflowBuilderAgent()
        
        orchestrator.register_agent(planner_agent)
        orchestrator.register_agent(builder_agent)
        
        # Prepare workflow context
        workflow_context = {
            "current_workflow": current_workflow,
            "workflow_id": workflow_id,
            "user_message": message
        }
        
        # Process the workflow request using LlamaIndex agents
        agent_result = await orchestrator.process_workflow_request(message, workflow_context)
        
        if agent_result["success"]:
            # Extract the generated workflow and AI message
            ai_message = agent_result["ai_message"]
            generated_workflow = agent_result.get("generated_workflow", {})
            
            # Add the user message to the conversation
            current_messages = current_workflow.get("messages", [])
            user_message = {
                "id": f"msg_{int(__import__('time').time() * 1000)}",
                "role": "user",
                "content": message,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
            
            # Update messages array
            updated_messages = current_messages + [user_message, ai_message]
            
            # Merge the generated workflow with current workflow
            updated_workflow = {
                **current_workflow,
                "messages": updated_messages
            }
            
            # If we have a new workflow structure, update the visual data
            if generated_workflow and "visual_data" in generated_workflow:
                updated_workflow.update({
                    "visual_data": generated_workflow["visual_data"],
                    "updated_at": __import__('datetime').datetime.utcnow().isoformat()
                })
                
                # Update workflow in database with new structure
                workflow_update = WorkflowUpdateRequest(
                    visual_data=generated_workflow["visual_data"],
                    updated_at=__import__('datetime').datetime.utcnow().isoformat()
                )
                await crud.update_workflow(workflow_id, workflow_update)
            
            return {
                "success": True,
                "ai_message": ai_message,
                "updated_workflow": updated_workflow,
                "workflow_plan": agent_result.get("workflow_plan"),
                "message": "Workflow chat processed successfully with AI agents"
            }
        else:
            # Agent processing failed, return error but with helpful message
            error_message = {
                "id": f"msg_{int(__import__('time').time() * 1000)}",
                "role": "assistant",
                "content": f"I encountered an issue while processing your request: {agent_result.get('error', 'Unknown error')}. Please try rephrasing your request or providing more specific details.",
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
            
            current_messages = current_workflow.get("messages", [])
            user_message = {
                "id": f"msg_{int(__import__('time').time() * 1000) - 1}",
                "role": "user",
                "content": message,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
            
            updated_workflow = {
                **current_workflow,
                "messages": current_messages + [user_message, error_message]
            }
            
            return {
                "success": False,
                "ai_message": error_message,
                "updated_workflow": updated_workflow,
                "error": agent_result.get("error"),
                "message": "Workflow chat processing encountered an error"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        
        # Create error response
        error_message = {
            "id": f"msg_{int(__import__('time').time() * 1000)}",
            "role": "assistant",
            "content": f"I'm sorry, I encountered a technical error while processing your request. Please try again or contact support if the issue persists. Error: {str(e)}",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
        
        return {
            "success": False,
            "ai_message": error_message,
            "updated_workflow": current_workflow,
            "error": str(e),
            "message": "Technical error occurred during chat processing"
        }
