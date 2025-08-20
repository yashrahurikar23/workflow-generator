from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.database import get_database
from app.crud.workflow import WorkflowCRUD
from app.models.workflow import (
    Workflow, WorkflowExecution, WorkflowCreateRequest, 
    WorkflowUpdateRequest, WorkflowExecuteRequest, WorkflowGenerateRequest,
    WorkflowResponse, WorkflowListResponse, WorkflowExecutionResponse,
    WorkflowStatus
)
from app.services.workflow_generator import WorkflowGenerator

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
