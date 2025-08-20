from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
from app.models.workflow import (
    Workflow, WorkflowStepConfig, StepType, WorkflowStatus,
    WorkflowGenerateRequest
)
from app.core.config import settings

class WorkflowGenerator:
    """Service for generating workflows using LLM"""
    
    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
    
    async def generate_workflow(self, request: WorkflowGenerateRequest) -> Workflow:
        """Generate a workflow from natural language description"""
        
        # For now, we'll create a simple template-based generation
        # In a real implementation, this would use LlamaIndex or another LLM service
        
        workflow_id = str(uuid.uuid4())
        
        # Analyze the prompt to determine workflow type and steps
        steps = await self._analyze_prompt_and_generate_steps(request.prompt, request.additional_context)
        
        # Extract a name from the prompt (simple heuristic)
        name = self._extract_workflow_name(request.prompt)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=f"Generated from prompt: {request.prompt[:200]}...",
            steps=steps,
            status=WorkflowStatus.DRAFT,
            generated_by_llm=True,
            generation_prompt=request.prompt,
            llm_provider=self.llm_provider,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return workflow
    
    async def _analyze_prompt_and_generate_steps(
        self, 
        prompt: str, 
        additional_context: Optional[str] = None
    ) -> List[WorkflowStepConfig]:
        """Analyze the prompt and generate appropriate workflow steps"""
        
        # Simple keyword-based step generation
        # In a real implementation, this would use a sophisticated LLM
        
        steps = []
        prompt_lower = prompt.lower()
        
        # Add a manual input step if the prompt mentions data input
        if any(word in prompt_lower for word in ["input", "data", "upload", "provide"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Data Input",
                step_type=StepType.MANUAL,
                description="Collect input data for processing",
                config={
                    "instruction": "Please provide the required input data",
                    "input_type": "text"
                }
            ))
        
        # Add API call step if prompt mentions API, fetch, or external data
        if any(word in prompt_lower for word in ["api", "fetch", "external", "call", "request"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="API Data Retrieval",
                step_type=StepType.API_CALL,
                description="Fetch data from external API",
                config={
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {},
                    "timeout": 30
                }
            ))
        
        # Add data transformation step if prompt mentions processing, transform, or clean
        if any(word in prompt_lower for word in ["process", "transform", "clean", "format", "convert"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Data Processing",
                step_type=StepType.DATA_TRANSFORM,
                description="Process and transform the data",
                config={
                    "input_field": "data",
                    "transform_type": "format",
                    "output_format": "json"
                }
            ))
        
        # Add LLM processing step if prompt mentions AI, analyze, or generate
        if any(word in prompt_lower for word in ["ai", "analyze", "generate", "llm", "gpt", "summarize"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="AI Analysis",
                step_type=StepType.LLM_PROCESS,
                description="Analyze data using AI",
                config={
                    "prompt": "Analyze the provided data and extract key insights",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 500
                }
            ))
        
        # Add condition step if prompt mentions conditional logic
        if any(word in prompt_lower for word in ["if", "condition", "check", "validate", "when"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Conditional Check",
                step_type=StepType.CONDITION,
                description="Check conditions and branch logic",
                config={
                    "condition": "data_quality > 0.8",
                    "true_action": "continue",
                    "false_action": "retry"
                }
            ))
        
        # Add email step if prompt mentions email or notification
        if any(word in prompt_lower for word in ["email", "notify", "send", "alert"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Send Notification",
                step_type=StepType.EMAIL,
                description="Send email notification with results",
                config={
                    "to": "user@example.com",
                    "subject": "Workflow Completed",
                    "template": "workflow_completion"
                }
            ))
        
        # If no specific steps were detected, create a generic workflow
        if not steps:
            steps = [
                WorkflowStepConfig(
                    step_id=str(uuid.uuid4()),
                    name="Process Task",
                    step_type=StepType.MANUAL,
                    description="Complete the requested task",
                    config={
                        "instruction": prompt,
                        "expected_output": "Task completion confirmation"
                    }
                )
            ]
        
        return steps
    
    def _extract_workflow_name(self, prompt: str) -> str:
        """Extract a reasonable workflow name from the prompt"""
        # Simple heuristic to create a name
        words = prompt.split()[:6]  # Take first 6 words
        name = " ".join(words)
        
        # Clean up the name
        if len(name) > 50:
            name = name[:50] + "..."
        
        # Capitalize first letter
        name = name[0].upper() + name[1:] if name else "Generated Workflow"
        
        return name
    
    async def enhance_workflow_with_llm(self, workflow: Workflow, enhancement_request: str) -> Workflow:
        """Enhance an existing workflow using LLM suggestions"""
        # This would use LLM to suggest improvements to the workflow
        # For now, we'll just add a simple enhancement
        
        if "optimization" in enhancement_request.lower():
            # Add a performance optimization step
            optimization_step = WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Performance Optimization",
                step_type=StepType.DATA_TRANSFORM,
                description="Optimize workflow performance",
                config={
                    "optimization_type": "parallel_processing",
                    "cache_enabled": True
                }
            )
            workflow.steps.append(optimization_step)
        
        workflow.updated_at = datetime.utcnow()
        return workflow
    
    async def generate_step_parameters(self, step_type: StepType, context: str) -> Dict[str, Any]:
        """Generate parameters for a specific step type using LLM"""
        # This would use LLM to generate appropriate parameters for a step
        
        base_configs = {
            StepType.API_CALL: {
                "url": "https://api.example.com",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 30
            },
            StepType.DATA_TRANSFORM: {
                "input_field": "data",
                "transform_type": "format",
                "output_format": "json"
            },
            StepType.CONDITION: {
                "condition": "true",
                "true_action": "continue",
                "false_action": "stop"
            },
            StepType.LLM_PROCESS: {
                "prompt": "Process the data",
                "model": "gpt-3.5-turbo",
                "max_tokens": 500
            },
            StepType.EMAIL: {
                "to": "user@example.com",
                "subject": "Workflow Update",
                "template": "default"
            }
        }
        
        return base_configs.get(step_type, {})
