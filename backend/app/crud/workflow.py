import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.workflow import (StepExecution, Workflow,
                                 WorkflowCreateRequest, WorkflowExecution,
                                 WorkflowRunSummary, WorkflowStatus,
                                 WorkflowStepConfig, WorkflowUpdateRequest)
from motor.motor_asyncio import AsyncIOMotorDatabase


class WorkflowCRUD:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.workflows
        self.executions_collection = database.workflow_executions

    async def create_workflow(self, workflow_data: WorkflowCreateRequest, created_by: Optional[str] = None) -> Workflow:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_data.name,
            description=workflow_data.description,
            steps=workflow_data.steps,
            tags=workflow_data.tags,
            parallel_execution=workflow_data.parallel_execution,
            timeout_minutes=workflow_data.timeout_minutes,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Convert to dict and insert
        workflow_dict = workflow.model_dump()
        await self.collection.insert_one(workflow_dict)
        
        return workflow

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        workflow_doc = await self.collection.find_one({"workflow_id": workflow_id})
        if workflow_doc:
            # Remove MongoDB's _id field
            workflow_doc.pop("_id", None)
            return Workflow(**workflow_doc)
        return None

    async def update_workflow(
        self, 
        workflow_id: str, 
        workflow_data: WorkflowUpdateRequest, 
        updated_by: Optional[str] = None
    ) -> Optional[Workflow]:
        """Update an existing workflow"""
        update_data = {}
        
        # Only update provided fields
        if workflow_data.name is not None:
            update_data["name"] = workflow_data.name
        if workflow_data.description is not None:
            update_data["description"] = workflow_data.description
        if workflow_data.steps is not None:
            update_data["steps"] = [step.model_dump() for step in workflow_data.steps]
        if workflow_data.tags is not None:
            update_data["tags"] = workflow_data.tags
        if workflow_data.parallel_execution is not None:
            update_data["parallel_execution"] = workflow_data.parallel_execution
        if workflow_data.timeout_minutes is not None:
            update_data["timeout_minutes"] = workflow_data.timeout_minutes
        if workflow_data.status is not None:
            update_data["status"] = workflow_data.status
        if workflow_data.generated_by_llm is not None:
            update_data["generated_by_llm"] = workflow_data.generated_by_llm
        if workflow_data.generation_prompt is not None:
            update_data["generation_prompt"] = workflow_data.generation_prompt
        if workflow_data.llm_provider is not None:
            update_data["llm_provider"] = workflow_data.llm_provider
        
        if update_data:
            update_data["updated_by"] = updated_by
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"workflow_id": workflow_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_workflow(workflow_id)
        
        return None

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        result = await self.collection.delete_one({"workflow_id": workflow_id})
        return result.deleted_count > 0

    async def list_workflows(
        self, 
        skip: int = 0, 
        limit: int = 50, 
        status: Optional[WorkflowStatus] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List workflows with filtering and pagination"""
        query = {}
        
        # Add filters
        if status:
            query["status"] = status
        if tags:
            query["tags"] = {"$in": tags}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Get workflows with pagination
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        workflows = []
        
        async for doc in cursor:
            doc.pop("_id", None)
            workflows.append(Workflow(**doc))
        
        return {
            "workflows": workflows,
            "total": total,
            "page": skip // limit + 1,
            "size": limit
        }

    async def create_execution(self, workflow_id: str, input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Create a new workflow execution"""
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            execution_context=input_data or {},
            started_at=datetime.utcnow()
        )
        
        # Convert to dict and insert
        execution_dict = execution.model_dump()
        await self.executions_collection.insert_one(execution_dict)
        
        # Update workflow's execution count and last executed time
        await self.collection.update_one(
            {"workflow_id": workflow_id},
            {
                "$inc": {"execution_count": 1},
                "$set": {"last_executed_at": datetime.utcnow()}
            }
        )
        
        return execution

    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID"""
        execution_doc = await self.executions_collection.find_one({"execution_id": execution_id})
        if execution_doc:
            execution_doc.pop("_id", None)
            return WorkflowExecution(**execution_doc)
        return None

    async def update_execution(self, execution_id: str, update_data: Dict[str, Any]) -> Optional[WorkflowExecution]:
        """Update a workflow execution"""
        if update_data:
            result = await self.executions_collection.update_one(
                {"execution_id": execution_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_execution(execution_id)
        
        return None

    async def list_executions(
        self, 
        workflow_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> Dict[str, Any]:
        """List workflow executions with pagination"""
        query = {}
        if workflow_id:
            query["workflow_id"] = workflow_id
        
        # Get total count
        total = await self.executions_collection.count_documents(query)
        
        # Get executions with pagination
        cursor = self.executions_collection.find(query).sort("started_at", -1).skip(skip).limit(limit)
        executions = []
        
        async for doc in cursor:
            doc.pop("_id", None)
            executions.append(WorkflowExecution(**doc))
        
        return {
            "executions": executions,
            "total": total,
            "page": skip // limit + 1,
            "size": limit
        }

    async def create_step_execution(
        self, 
        execution_id: str, 
        step_config: WorkflowStepConfig
    ) -> StepExecution:
        """Create a step execution record"""
        import uuid

        from app.models.workflow import StepExecution
        
        step_execution = StepExecution(
            step_execution_id=str(uuid.uuid4()),
            execution_id=execution_id,
            workflow_id=step_config.workflow_id if hasattr(step_config, 'workflow_id') else "",
            step_id=step_config.step_id,
            step_name=step_config.name,
            step_type=step_config.step_type,
            started_at=datetime.utcnow()
        )
        
        # Convert to dict and insert
        step_execution_dict = step_execution.model_dump()
        await self.db.step_executions.insert_one(step_execution_dict)
        
        return step_execution

    async def update_step_execution(
        self, 
        step_execution_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[StepExecution]:
        """Update a step execution record"""
        from app.models.workflow import StepExecution
        
        if update_data:
            result = await self.db.step_executions.update_one(
                {"step_execution_id": step_execution_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                step_doc = await self.db.step_executions.find_one({"step_execution_id": step_execution_id})
                if step_doc:
                    step_doc.pop("_id", None)
                    return StepExecution(**step_doc)
        
        return None

    async def get_execution_steps(self, execution_id: str) -> List[StepExecution]:
        """Get all step executions for a workflow execution"""
        from app.models.workflow import StepExecution
        
        cursor = self.db.step_executions.find({"execution_id": execution_id}).sort("started_at", 1)
        steps = []
        
        async for doc in cursor:
            doc.pop("_id", None)
            steps.append(StepExecution(**doc))
        
        return steps

    async def get_workflow_run_summary(self, workflow_id: str) -> WorkflowRunSummary:
        """Get summary statistics for workflow runs"""
        from app.models.workflow import WorkflowRunSummary

        # Get all executions for this workflow
        executions_cursor = self.executions_collection.find({"workflow_id": workflow_id})
        
        total_runs = 0
        successful_runs = 0
        failed_runs = 0
        running_runs = 0
        durations = []
        last_run_at = None
        
        async for execution in executions_cursor:
            total_runs += 1
            
            if execution.get("status") == "completed":
                successful_runs += 1
                # Calculate duration if both timestamps exist
                if execution.get("started_at") and execution.get("completed_at"):
                    duration = (execution["completed_at"] - execution["started_at"]).total_seconds()
                    durations.append(duration)
            elif execution.get("status") == "failed":
                failed_runs += 1
            elif execution.get("status") in ["running", "pending"]:
                running_runs += 1
            
            # Track latest run
            if execution.get("started_at"):
                if last_run_at is None or execution["started_at"] > last_run_at:
                    last_run_at = execution["started_at"]
        
        # Calculate averages
        average_duration = sum(durations) / len(durations) if durations else None
        success_rate = (successful_runs / total_runs) if total_runs > 0 else 0.0
        
        return WorkflowRunSummary(
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            running_runs=running_runs,
            average_duration_seconds=average_duration,
            last_run_at=last_run_at,
            success_rate=success_rate
        )
