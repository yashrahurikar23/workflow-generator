from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Types of workflow steps"""
    API_CALL = "api_call"
    DATA_TRANSFORM = "data_transform"
    CONDITION = "condition"
    LOOP = "loop"
    MANUAL = "manual"
    LLM_PROCESS = "llm_process"
    EMAIL = "email"
    DATABASE = "database"
    FILE_OPERATION = "file_operation"

class StepStatus(str, Enum):
    """Status of a workflow step during execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowStatus(str, Enum):
    """Status of an entire workflow"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class WorkflowStepConfig(BaseModel):
    """Configuration for a workflow step"""
    step_id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Human-readable name for the step")
    step_type: StepType = Field(..., description="Type of step")
    description: Optional[str] = Field(None, description="Description of what this step does")
    
    # Step configuration - flexible structure for different step types
    config: Dict[str, Any] = Field(default_factory=dict, description="Step-specific configuration")
    
    # Dependencies and flow control
    depends_on: List[str] = Field(default_factory=list, description="List of step IDs this step depends on")
    condition: Optional[Dict[str, Any]] = Field(None, description="Condition for executing this step")
    
    # Execution tracking
    status: StepStatus = Field(default=StepStatus.PENDING, description="Current status of the step")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    max_retries: int = Field(default=3, description="Maximum number of retries allowed")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowExecution(BaseModel):
    """Execution instance of a workflow"""
    execution_id: str = Field(..., description="Unique identifier for this execution")
    workflow_id: str = Field(..., description="ID of the workflow being executed")
    status: WorkflowStatus = Field(default=WorkflowStatus.RUNNING)
    
    # Execution state
    current_step: Optional[str] = Field(None, description="Currently executing step ID")
    completed_steps: List[str] = Field(default_factory=list, description="List of completed step IDs")
    failed_steps: List[str] = Field(default_factory=list, description="List of failed step IDs")
    
    # Execution data - context that flows between steps
    execution_context: Dict[str, Any] = Field(default_factory=dict, description="Data context for the execution")
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    error_step: Optional[str] = None

class WorkflowRunSummary(BaseModel):
    """Summary model for workflow run statistics"""
    total_runs: int
    successful_runs: int
    failed_runs: int
    running_runs: int
    average_duration_seconds: Optional[float]
    last_run_at: Optional[datetime]
    success_rate: float

class StepExecution(BaseModel):
    """Detailed execution tracking for individual workflow steps"""
    step_execution_id: str = Field(..., description="Unique identifier for this step execution")
    execution_id: str = Field(..., description="Parent workflow execution ID")
    workflow_id: str = Field(..., description="Parent workflow ID")
    step_id: str = Field(..., description="ID of the step being executed")
    step_name: str = Field(..., description="Name of the step")
    step_type: StepType = Field(..., description="Type of step")
    
    # Execution state
    status: StepStatus = Field(default=StepStatus.PENDING)
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for this step")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data from this step")
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Error tracking
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    
    # Metadata
    logs: List[str] = Field(default_factory=list, description="Execution logs for this step")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")

class Workflow(BaseModel):
    """Main workflow model"""
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    name: str = Field(..., description="Human-readable name for the workflow")
    description: Optional[str] = Field(None, description="Description of what this workflow does")
    
    # Workflow definition
    steps: List[WorkflowStepConfig] = Field(default_factory=list, description="List of workflow steps")
    
    # Visual workflow data (for visual workflow editor)
    visual_data: Optional[Dict[str, Any]] = Field(None, description="Visual workflow data including nodes and connections")
    
    # Workflow metadata
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT, description="Current status of the workflow")
    version: int = Field(default=1, description="Version number of the workflow")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing workflows")
    
    # Execution settings
    parallel_execution: bool = Field(default=False, description="Whether steps can be executed in parallel")
    timeout_minutes: int = Field(default=60, description="Timeout for the entire workflow in minutes")
    
    # LLM generation metadata (if generated by AI)
    generated_by_llm: bool = Field(default=False, description="Whether this workflow was generated by LLM")
    generation_prompt: Optional[str] = Field(None, description="Original prompt used to generate this workflow")
    llm_provider: Optional[str] = Field(None, description="LLM provider used for generation")
    
    # Audit fields
    created_by: Optional[str] = Field(None, description="User who created the workflow")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(None, description="User who last updated the workflow")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Execution history
    execution_count: int = Field(default=0, description="Number of times this workflow has been executed")
    last_executed_at: Optional[datetime] = None

# Request/Response models for API
class WorkflowCreateRequest(BaseModel):
    """Request model for creating a new workflow"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    steps: List[WorkflowStepConfig] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    parallel_execution: bool = Field(default=False)
    timeout_minutes: int = Field(default=60, ge=1, le=1440)  # 1 minute to 24 hours

class WorkflowUpdateRequest(BaseModel):
    """Request model for updating an existing workflow"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    steps: Optional[List[WorkflowStepConfig]] = None
    tags: Optional[List[str]] = None
    parallel_execution: Optional[bool] = None
    timeout_minutes: Optional[int] = Field(None, ge=1, le=1440)
    status: Optional[WorkflowStatus] = None
    generated_by_llm: Optional[bool] = None
    generation_prompt: Optional[str] = None
    llm_provider: Optional[str] = None
    visual_data: Optional[Dict[str, Any]] = None
    updated_at: Optional[str] = None

class WorkflowExecuteRequest(BaseModel):
    """Request model for executing a workflow"""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the workflow execution")

class WorkflowGenerateRequest(BaseModel):
    """Request model for LLM-generated workflows"""
    prompt: str = Field(..., min_length=10, max_length=2000, description="Description of the desired workflow")
    additional_context: Optional[str] = Field(None, max_length=1000, description="Additional context or requirements")
    preferred_steps: Optional[List[StepType]] = Field(None, description="Preferred types of steps to include")

# Response models
class WorkflowResponse(Workflow):
    """Response model for workflow data"""
    pass

class WorkflowListResponse(BaseModel):
    """Response model for listing workflows"""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    size: int

class WorkflowExecutionResponse(WorkflowExecution):
    """Response model for workflow execution data"""
    pass
