from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
from app.models.workflow import (
    Workflow, WorkflowExecution, WorkflowStepConfig, 
    StepStatus, WorkflowStatus, StepType
)
from app.crud.workflow import WorkflowCRUD

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """Service for executing workflows"""
    
    def __init__(self, workflow_crud: WorkflowCRUD):
        self.crud = workflow_crud
    
    async def execute_workflow(self, execution_id: str) -> WorkflowExecution:
        """Execute a workflow asynchronously"""
        execution = await self.crud.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        workflow = await self.crud.get_workflow(execution.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {execution.workflow_id} not found")
        
        try:
            # Update execution status to running
            await self.crud.update_execution(execution_id, {
                "status": WorkflowStatus.RUNNING,
                "current_step": None
            })
            
            # Execute steps sequentially (simple implementation)
            # In a more advanced implementation, we'd support parallel execution
            execution_context = execution.execution_context.copy()
            
            for step in workflow.steps:
                try:
                    logger.info(f"Executing step {step.step_id} for execution {execution_id}")
                    
                    # Update execution with current step
                    await self.crud.update_execution(execution_id, {
                        "current_step": step.step_id
                    })
                    
                    # Execute the step
                    step_result = await self._execute_step(step, execution_context)
                    
                    # Update execution context with step result
                    execution_context.update(step_result.get("output", {}))
                    
                    # Mark step as completed
                    await self.crud.update_execution(execution_id, {
                        "completed_steps": execution.completed_steps + [step.step_id],
                        "execution_context": execution_context
                    })
                    
                    execution.completed_steps.append(step.step_id)
                    
                except Exception as step_error:
                    logger.error(f"Step {step.step_id} failed: {str(step_error)}")
                    
                    # Mark step as failed
                    await self.crud.update_execution(execution_id, {
                        "failed_steps": execution.failed_steps + [step.step_id],
                        "error_message": str(step_error),
                        "error_step": step.step_id,
                        "status": WorkflowStatus.FAILED
                    })
                    
                    return await self.crud.get_execution(execution_id)
            
            # Mark execution as completed
            await self.crud.update_execution(execution_id, {
                "status": WorkflowStatus.COMPLETED,
                "completed_at": datetime.utcnow(),
                "current_step": None
            })
            
            return await self.crud.get_execution(execution_id)
            
        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed: {str(e)}")
            
            await self.crud.update_execution(execution_id, {
                "status": WorkflowStatus.FAILED,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
            
            return await self.crud.get_execution(execution_id)
    
    async def _execute_step(self, step: WorkflowStepConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        logger.info(f"Executing step {step.step_id} of type {step.step_type}")
        
        # Simulate step execution based on step type
        # In a real implementation, this would dispatch to specific step handlers
        
        if step.step_type == StepType.API_CALL:
            return await self._execute_api_call_step(step, context)
        elif step.step_type == StepType.DATA_TRANSFORM:
            return await self._execute_data_transform_step(step, context)
        elif step.step_type == StepType.CONDITION:
            return await self._execute_condition_step(step, context)
        elif step.step_type == StepType.MANUAL:
            return await self._execute_manual_step(step, context)
        elif step.step_type == StepType.LLM_PROCESS:
            return await self._execute_llm_step(step, context)
        else:
            # Default: just pass through the context
            await asyncio.sleep(1)  # Simulate processing time
            return {"output": {"message": f"Executed {step.step_type} step: {step.name}"}}
    
    async def _execute_api_call_step(self, step: WorkflowStepConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API call step"""
        # Simulate API call
        await asyncio.sleep(2)
        
        config = step.config
        url = config.get("url", "https://api.example.com/data")
        method = config.get("method", "GET")
        
        # In a real implementation, we'd make the actual HTTP request
        result = {
            "status_code": 200,
            "data": {"message": f"API call to {url} with {method} method successful"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {"output": {"api_result": result}}
    
    async def _execute_data_transform_step(self, step: WorkflowStepConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data transformation step"""
        # Simulate data transformation
        await asyncio.sleep(1)
        
        config = step.config
        input_field = config.get("input_field", "data")
        transform_type = config.get("transform_type", "uppercase")
        
        input_data = context.get(input_field, "default_data")
        
        if transform_type == "uppercase":
            transformed_data = str(input_data).upper()
        elif transform_type == "lowercase":
            transformed_data = str(input_data).lower()
        else:
            transformed_data = str(input_data)
        
        return {"output": {"transformed_data": transformed_data}}
    
    async def _execute_condition_step(self, step: WorkflowStepConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a conditional step"""
        await asyncio.sleep(0.5)
        
        config = step.config
        condition = config.get("condition", "true")
        
        # Simple condition evaluation (in real implementation, use a proper expression evaluator)
        if condition == "true":
            result = True
        else:
            result = False
        
        return {"output": {"condition_result": result}}
    
    async def _execute_manual_step(self, step: WorkflowStepConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a manual step (requires human intervention)"""
        # In a real implementation, this would pause execution and wait for human input
        await asyncio.sleep(1)
        
        return {"output": {"message": "Manual step completed (simulated)"}}
    
    async def _execute_llm_step(self, step: WorkflowStepConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an LLM processing step"""
        # Simulate LLM processing
        await asyncio.sleep(3)
        
        config = step.config
        prompt = config.get("prompt", "Process this data")
        input_data = config.get("input_data", context)
        
        # In a real implementation, we'd call the actual LLM service
        llm_result = f"LLM processed: {prompt} with data: {str(input_data)[:100]}..."
        
        return {"output": {"llm_result": llm_result}}
