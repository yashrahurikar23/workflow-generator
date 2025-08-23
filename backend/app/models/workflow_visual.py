from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# Existing enums and models (keeping backward compatibility)
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
    # New node types for visual editor
    AI_MODEL = "ai_model"
    TRIGGER = "trigger"
    WEBHOOK = "webhook"
    SCHEDULER = "scheduler"
    TEXT_ANALYSIS = "text_analysis"
    IMAGE_GENERATION = "image_generation"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"


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


# Visual workflow models for node-based editor
class NodePosition(BaseModel):
    """Position of a node in the visual editor"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class NodeInput(BaseModel):
    """Input handle for a workflow node"""
    id: str = Field(..., description="Unique input ID")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Data type expected")
    required: bool = Field(True, description="Whether this input is required")
    description: Optional[str] = Field(None, description="Input description")


class NodeOutput(BaseModel):
    """Output handle for a workflow node"""
    id: str = Field(..., description="Unique output ID")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Data type produced")
    description: Optional[str] = Field(None, description="Output description")


class NodeConnection(BaseModel):
    """Connection between two nodes"""
    id: str = Field(..., description="Unique connection ID")
    source_node_id: str = Field(..., description="Source node ID")
    source_handle: str = Field(..., description="Source output handle ID")
    target_node_id: str = Field(..., description="Target node ID")
    target_handle: str = Field(..., description="Target input handle ID")
    
    # Visual properties
    animated: bool = Field(False, description="Whether connection is animated")
    style: Optional[Dict[str, Any]] = Field(None, description="Connection styling")


class ConfigField(BaseModel):
    """Configuration field for a node"""
    key: str = Field(..., description="Configuration key")
    type: str = Field(..., description="Field type (string, number, boolean, select, json)")
    label: str = Field(..., description="Display label")
    description: Optional[str] = Field(None, description="Field description")
    required: bool = Field(True, description="Whether field is required")
    default_value: Optional[Any] = Field(None, description="Default value")
    options: Optional[List[str]] = Field(None, description="Options for select type")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")


class NodeType(BaseModel):
    """Definition of a node type"""
    id: str = Field(..., description="Unique node type ID")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Node description")
    category: str = Field(..., description="Node category")
    icon: str = Field(..., description="Icon name or URL")
    color: str = Field(..., description="Node color theme")
    
    # Node interface
    inputs: List[NodeInput] = Field(default_factory=list, description="Available inputs")
    outputs: List[NodeOutput] = Field(default_factory=list, description="Available outputs")
    config_fields: List[ConfigField] = Field(default_factory=list, description="Configuration fields")
    
    # Metadata
    is_template: bool = Field(False, description="Whether this is a template node")
    tags: List[str] = Field(default_factory=list, description="Node tags")
    version: str = Field("1.0.0", description="Node version")


class NodeCategory(BaseModel):
    """Category for organizing node types"""
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Category description")
    icon: str = Field(..., description="Category icon")
    color: str = Field(..., description="Category color")
    order: int = Field(0, description="Display order")


class WorkflowNode(BaseModel):
    """A node instance in a workflow"""
    node_id: str = Field(..., description="Unique node instance ID")
    node_type_id: str = Field(..., description="Type of node")
    name: str = Field(..., description="Instance name")
    description: Optional[str] = Field(None, description="Instance description")
    
    # Visual properties
    position: NodePosition = Field(..., description="Position in canvas")
    selected: bool = Field(False, description="Whether node is selected")
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Node configuration")
    
    # Runtime properties
    status: StepStatus = Field(StepStatus.PENDING, description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Legacy model for backward compatibility
class WorkflowStepConfig(BaseModel):
    """Configuration for a workflow step (legacy)"""
    step_id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Human-readable name for the step")
    step_type: StepType = Field(..., description="Type of step")
    description: Optional[str] = Field(None, description="Description of what this step does")
    
    # Step configuration - flexible structure for different step types
    config: Dict[str, Any] = Field(default_factory=dict, description="Step-specific configuration")
    
    # Dependencies and flow control
    depends_on: List[str] = Field(default_factory=list, description="List of step IDs this step depends on")
    condition: Optional[Dict[str, Any]] = Field(None, description="Condition for executing this step")
    
    # Execution metadata
    timeout_seconds: Optional[int] = Field(None, description="Timeout for this step")
    retry_count: int = Field(0, description="Number of times to retry on failure")
    
    # For parallel execution
    parallel: bool = Field(False, description="Whether this step can run in parallel")


class VisualWorkflowData(BaseModel):
    """Visual workflow definition using nodes and connections"""
    nodes: List[WorkflowNode] = Field(default_factory=list, description="Workflow nodes")
    connections: List[NodeConnection] = Field(default_factory=list, description="Node connections")
    
    # Canvas properties
    viewport: Dict[str, Any] = Field(default_factory=dict, description="Canvas viewport state")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Workflow settings")


class WorkflowBase(BaseModel):
    """Base model for workflow creation"""
    name: str = Field(..., min_length=1, max_length=200, description="Workflow name")
    description: Optional[str] = Field(None, max_length=1000, description="Workflow description")
    tags: List[str] = Field(default_factory=list, description="Workflow tags")
    
    # Workflow type - supports both legacy and visual formats
    workflow_type: str = Field("legacy", description="Workflow type: 'legacy' or 'visual'")
    
    # Legacy format (steps-based)
    steps: List[WorkflowStepConfig] = Field(default_factory=list, description="Workflow steps (legacy)")
    
    # Visual format (nodes-based)
    visual_data: Optional[VisualWorkflowData] = Field(None, description="Visual workflow data")
    
    # Execution settings
    parallel_execution: bool = Field(False, description="Whether workflow supports parallel execution")
    timeout_minutes: int = Field(60, description="Workflow timeout in minutes")
    
    # Metadata
    is_template: bool = Field(False, description="Whether this is a template workflow")
    version: str = Field("1.0.0", description="Workflow version")


class Workflow(WorkflowBase):
    """Complete workflow model with runtime data"""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: WorkflowStatus = Field(WorkflowStatus.DRAFT, description="Current workflow status")
    
    # Execution tracking
    execution_count: int = Field(0, description="Number of times this workflow has been executed")
    last_executed: Optional[datetime] = Field(None, description="Last execution timestamp")
    
    # User and system metadata
    created_by: Optional[str] = Field(None, description="User who created the workflow")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowRun(BaseModel):
    """Execution run of a workflow"""
    run_id: str = Field(..., description="Unique run identifier")
    workflow_id: str = Field(..., description="ID of the workflow being executed")
    
    # Execution details
    status: WorkflowStatus = Field(..., description="Run status")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Input and output
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the run")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data from the run")
    
    # Step execution details
    step_results: List[Dict[str, Any]] = Field(default_factory=list, description="Results from each step")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if run failed")
    
    # Performance metrics
    execution_time_seconds: Optional[float] = Field(None, description="Total execution time")
    
    # Metadata
    triggered_by: Optional[str] = Field(None, description="What triggered this run")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowExecutionContext(BaseModel):
    """Context passed between workflow steps during execution"""
    run_id: str = Field(..., description="Current run ID")
    workflow_id: str = Field(..., description="Workflow ID")
    current_step: str = Field(..., description="Current step being executed")
    
    # Data flow
    global_variables: Dict[str, Any] = Field(default_factory=dict, description="Global variables")
    step_outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs from previous steps")
    
    # Runtime state
    execution_start_time: datetime = Field(default_factory=datetime.utcnow)
    user_context: Optional[Dict[str, Any]] = Field(None, description="User-specific context")


# Export commonly used models
__all__ = [
    "StepType",
    "StepStatus", 
    "WorkflowStatus",
    "NodePosition",
    "NodeInput",
    "NodeOutput",
    "NodeConnection",
    "ConfigField",
    "NodeType",
    "NodeCategory",
    "WorkflowNode",
    "VisualWorkflowData",
    "WorkflowStepConfig",
    "WorkflowBase",
    "Workflow",
    "WorkflowRun",
    "WorkflowExecutionContext"
]
