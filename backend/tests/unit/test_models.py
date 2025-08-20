"""
Unit tests for workflow models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.workflow import (
    StepType,
    StepStatus,
    WorkflowStatus,
    WorkflowStepConfig,
    WorkflowExecution,
    Workflow,
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowExecuteRequest,
    WorkflowGenerateRequest,
)


class TestStepType:
    """Test StepType enum."""
    
    def test_step_type_values(self):
        """Test that all step types have correct values."""
        assert StepType.API_CALL == "api_call"
        assert StepType.DATA_TRANSFORM == "data_transform"
        assert StepType.CONDITION == "condition"
        assert StepType.LOOP == "loop"
        assert StepType.MANUAL == "manual"
        assert StepType.LLM_PROCESS == "llm_process"
        assert StepType.EMAIL == "email"
        assert StepType.DATABASE == "database"
        assert StepType.FILE_OPERATION == "file_operation"


class TestStepStatus:
    """Test StepStatus enum."""
    
    def test_step_status_values(self):
        """Test that all step statuses have correct values."""
        assert StepStatus.PENDING == "pending"
        assert StepStatus.RUNNING == "running"
        assert StepStatus.COMPLETED == "completed"
        assert StepStatus.FAILED == "failed"
        assert StepStatus.SKIPPED == "skipped"


class TestWorkflowStatus:
    """Test WorkflowStatus enum."""
    
    def test_workflow_status_values(self):
        """Test that all workflow statuses have correct values."""
        assert WorkflowStatus.DRAFT == "draft"
        assert WorkflowStatus.ACTIVE == "active"
        assert WorkflowStatus.RUNNING == "running"
        assert WorkflowStatus.COMPLETED == "completed"
        assert WorkflowStatus.FAILED == "failed"
        assert WorkflowStatus.PAUSED == "paused"


class TestWorkflowStepConfig:
    """Test WorkflowStepConfig model."""
    
    def test_create_minimal_step(self):
        """Test creating a step with minimal required fields."""
        step = WorkflowStepConfig(
            step_id="test_step",
            name="Test Step",
            step_type=StepType.API_CALL
        )
        
        assert step.step_id == "test_step"
        assert step.name == "Test Step"
        assert step.step_type == StepType.API_CALL
        assert step.description is None
        assert step.config == {}
        assert step.depends_on == []
        assert step.condition is None
        assert step.status == StepStatus.PENDING
        assert step.retry_count == 0
        assert step.max_retries == 3
        assert isinstance(step.created_at, datetime)
        assert isinstance(step.updated_at, datetime)
    
    def test_create_full_step(self):
        """Test creating a step with all fields."""
        config = {"url": "https://api.example.com", "method": "GET"}
        condition = {"field": "status", "operator": "equals", "value": "active"}
        
        step = WorkflowStepConfig(
            step_id="api_step",
            name="API Call Step",
            step_type=StepType.API_CALL,
            description="Make an API call to external service",
            config=config,
            depends_on=["previous_step"],
            condition=condition,
            status=StepStatus.RUNNING,
            retry_count=1,
            max_retries=5
        )
        
        assert step.step_id == "api_step"
        assert step.name == "API Call Step"
        assert step.step_type == StepType.API_CALL
        assert step.description == "Make an API call to external service"
        assert step.config == config
        assert step.depends_on == ["previous_step"]
        assert step.condition == condition
        assert step.status == StepStatus.RUNNING
        assert step.retry_count == 1
        assert step.max_retries == 5
    
    def test_invalid_step_type(self):
        """Test that invalid step type raises validation error."""
        with pytest.raises(ValidationError):
            WorkflowStepConfig(
                step_id="test_step",
                name="Test Step",
                step_type="invalid_type"
            )


class TestWorkflowExecution:
    """Test WorkflowExecution model."""
    
    def test_create_minimal_execution(self):
        """Test creating an execution with minimal required fields."""
        execution = WorkflowExecution(
            execution_id="exec_123",
            workflow_id="workflow_456"
        )
        
        assert execution.execution_id == "exec_123"
        assert execution.workflow_id == "workflow_456"
        assert execution.status == WorkflowStatus.RUNNING
        assert execution.current_step is None
        assert execution.completed_steps == []
        assert execution.failed_steps == []
        assert execution.execution_context == {}
        assert isinstance(execution.started_at, datetime)
        assert execution.completed_at is None
        assert execution.error_message is None
        assert execution.error_step is None
    
    def test_create_full_execution(self):
        """Test creating an execution with all fields."""
        context = {"user_id": "123", "environment": "prod"}
        completed_at = datetime.now()
        
        execution = WorkflowExecution(
            execution_id="exec_123",
            workflow_id="workflow_456",
            status=WorkflowStatus.COMPLETED,
            current_step="step_2",
            completed_steps=["step_1", "step_2"],
            failed_steps=[],
            execution_context=context,
            completed_at=completed_at,
            error_message=None,
            error_step=None
        )
        
        assert execution.execution_id == "exec_123"
        assert execution.workflow_id == "workflow_456"
        assert execution.status == WorkflowStatus.COMPLETED
        assert execution.current_step == "step_2"
        assert execution.completed_steps == ["step_1", "step_2"]
        assert execution.failed_steps == []
        assert execution.execution_context == context
        assert execution.completed_at == completed_at
        assert execution.error_message is None
        assert execution.error_step is None


class TestWorkflow:
    """Test Workflow model."""
    
    def test_create_minimal_workflow(self):
        """Test creating a workflow with minimal required fields."""
        workflow = Workflow(
            workflow_id="wf_123",
            name="Test Workflow"
        )
        
        assert workflow.workflow_id == "wf_123"
        assert workflow.name == "Test Workflow"
        assert workflow.description is None
        assert workflow.steps == []
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.version == 1
        assert workflow.tags == []
        assert workflow.parallel_execution is False
        assert workflow.timeout_minutes == 60
        assert workflow.generated_by_llm is False
        assert workflow.generation_prompt is None
        assert workflow.llm_provider is None
        assert workflow.created_by is None
        assert isinstance(workflow.created_at, datetime)
        assert workflow.updated_by is None
        assert isinstance(workflow.updated_at, datetime)
        assert workflow.execution_count == 0
        assert workflow.last_executed_at is None
    
    def test_create_full_workflow(self):
        """Test creating a workflow with all fields."""
        steps = [
            WorkflowStepConfig(
                step_id="step_1",
                name="First Step",
                step_type=StepType.API_CALL
            ),
            WorkflowStepConfig(
                step_id="step_2",
                name="Second Step",
                step_type=StepType.DATA_TRANSFORM,
                depends_on=["step_1"]
            )
        ]
        
        last_executed = datetime.now()
        
        workflow = Workflow(
            workflow_id="wf_123",
            name="Complex Workflow",
            description="A complex workflow for testing",
            steps=steps,
            status=WorkflowStatus.ACTIVE,
            version=2,
            tags=["test", "complex"],
            parallel_execution=True,
            timeout_minutes=120,
            generated_by_llm=True,
            generation_prompt="Create a workflow for data processing",
            llm_provider="openai",
            created_by="user_123",
            updated_by="user_456",
            execution_count=5,
            last_executed_at=last_executed
        )
        
        assert workflow.workflow_id == "wf_123"
        assert workflow.name == "Complex Workflow"
        assert workflow.description == "A complex workflow for testing"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].step_id == "step_1"
        assert workflow.steps[1].step_id == "step_2"
        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.version == 2
        assert workflow.tags == ["test", "complex"]
        assert workflow.parallel_execution is True
        assert workflow.timeout_minutes == 120
        assert workflow.generated_by_llm is True
        assert workflow.generation_prompt == "Create a workflow for data processing"
        assert workflow.llm_provider == "openai"
        assert workflow.created_by == "user_123"
        assert workflow.updated_by == "user_456"
        assert workflow.execution_count == 5
        assert workflow.last_executed_at == last_executed


class TestWorkflowCreateRequest:
    """Test WorkflowCreateRequest model."""
    
    def test_create_valid_request(self):
        """Test creating a valid workflow create request."""
        steps = [
            WorkflowStepConfig(
                step_id="step_1",
                name="Test Step",
                step_type=StepType.API_CALL
            )
        ]
        
        request = WorkflowCreateRequest(
            name="Test Workflow",
            description="A test workflow",
            steps=steps,
            tags=["test"],
            parallel_execution=False,
            timeout_minutes=30
        )
        
        assert request.name == "Test Workflow"
        assert request.description == "A test workflow"
        assert len(request.steps) == 1
        assert request.tags == ["test"]
        assert request.parallel_execution is False
        assert request.timeout_minutes == 30
    
    def test_invalid_name_length(self):
        """Test that invalid name length raises validation error."""
        with pytest.raises(ValidationError):
            WorkflowCreateRequest(name="")  # Too short
        
        with pytest.raises(ValidationError):
            WorkflowCreateRequest(name="x" * 201)  # Too long
    
    def test_invalid_timeout(self):
        """Test that invalid timeout raises validation error."""
        with pytest.raises(ValidationError):
            WorkflowCreateRequest(
                name="Test Workflow",
                timeout_minutes=0  # Too small
            )
        
        with pytest.raises(ValidationError):
            WorkflowCreateRequest(
                name="Test Workflow",
                timeout_minutes=1441  # Too large (more than 24 hours)
            )


class TestWorkflowGenerateRequest:
    """Test WorkflowGenerateRequest model."""
    
    def test_create_valid_request(self):
        """Test creating a valid workflow generate request."""
        request = WorkflowGenerateRequest(
            prompt="Create a workflow that processes user data",
            additional_context="Focus on data validation and transformation",
            preferred_steps=[StepType.API_CALL, StepType.DATA_TRANSFORM]
        )
        
        assert request.prompt == "Create a workflow that processes user data"
        assert request.additional_context == "Focus on data validation and transformation"
        assert request.preferred_steps == [StepType.API_CALL, StepType.DATA_TRANSFORM]
    
    def test_invalid_prompt_length(self):
        """Test that invalid prompt length raises validation error."""
        with pytest.raises(ValidationError):
            WorkflowGenerateRequest(prompt="short")  # Too short
        
        with pytest.raises(ValidationError):
            WorkflowGenerateRequest(prompt="x" * 2001)  # Too long
