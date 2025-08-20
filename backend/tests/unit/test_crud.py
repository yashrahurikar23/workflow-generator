"""
Unit tests for workflow CRUD operations.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.crud.workflow import WorkflowCRUD
from app.models.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowStatus,
    StepType,
    WorkflowStepConfig,
    Workflow,
    WorkflowExecution
)


@pytest.fixture
def mock_database():
    """Create a mock database."""
    db = MagicMock()
    
    # Create collection mocks with proper async/sync method separation
    workflows_collection = MagicMock()
    executions_collection = MagicMock()
    
    # Async methods
    workflows_collection.insert_one = AsyncMock()
    workflows_collection.find_one = AsyncMock()
    workflows_collection.update_one = AsyncMock()
    workflows_collection.delete_one = AsyncMock()
    workflows_collection.count_documents = AsyncMock()
    
    executions_collection.insert_one = AsyncMock()
    executions_collection.find_one = AsyncMock()
    executions_collection.update_one = AsyncMock()
    executions_collection.delete_one = AsyncMock()
    executions_collection.count_documents = AsyncMock()
    
    # Sync methods (find returns a cursor)
    workflows_collection.find = MagicMock()
    executions_collection.find = MagicMock()
    
    db.workflows = workflows_collection
    db.workflow_executions = executions_collection
    return db


@pytest.fixture
def workflow_crud(mock_database):
    """Create a WorkflowCRUD instance with mock database."""
    return WorkflowCRUD(mock_database)


@pytest.fixture
def sample_workflow_create_request():
    """Sample workflow create request."""
    steps = [
        WorkflowStepConfig(
            step_id="step_1",
            name="API Call",
            step_type=StepType.API_CALL,
            config={"url": "https://api.example.com"}
        )
    ]
    
    return WorkflowCreateRequest(
        name="Test Workflow",
        description="A test workflow",
        steps=steps,
        tags=["test"],
        parallel_execution=False,
        timeout_minutes=30
    )


class TestWorkflowCRUD:
    """Test WorkflowCRUD class."""
    
    @pytest.mark.asyncio
    async def test_create_workflow_success(self, workflow_crud, sample_workflow_create_request, mock_database):
        """Test successful workflow creation."""
        # Mock the database insert
        mock_database.workflows.insert_one.return_value = AsyncMock()
        
        # Create workflow
        workflow = await workflow_crud.create_workflow(
            sample_workflow_create_request, 
            created_by="test_user"
        )
        
        # Assertions
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "API Call"
        assert workflow.tags == ["test"]
        assert workflow.parallel_execution is False
        assert workflow.timeout_minutes == 30
        assert workflow.created_by == "test_user"
        assert workflow.status == WorkflowStatus.DRAFT
        assert isinstance(workflow.workflow_id, str)
        assert isinstance(workflow.created_at, datetime)
        assert isinstance(workflow.updated_at, datetime)
        
        # Verify database was called
        mock_database.workflows.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_workflow_found(self, workflow_crud, mock_database):
        """Test getting an existing workflow."""
        # Mock database response
        workflow_doc = {
            "workflow_id": "test_id",
            "name": "Test Workflow",
            "description": "A test workflow",
            "steps": [],
            "tags": ["test"],
            "parallel_execution": False,
            "timeout_minutes": 30,
            "status": "draft",
            "version": 1,
            "generated_by_llm": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "execution_count": 0
        }
        mock_database.workflows.find_one.return_value = workflow_doc
        
        # Get workflow
        workflow = await workflow_crud.get_workflow("test_id")
        
        # Assertions
        assert workflow is not None
        assert isinstance(workflow, Workflow)
        assert workflow.workflow_id == "test_id"
        assert workflow.name == "Test Workflow"
        
        # Verify database was called
        mock_database.workflows.find_one.assert_called_once_with({"workflow_id": "test_id"})
    
    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, workflow_crud, mock_database):
        """Test getting a non-existent workflow."""
        # Mock database response
        mock_database.workflows.find_one.return_value = None
        
        # Get workflow
        workflow = await workflow_crud.get_workflow("nonexistent_id")
        
        # Assertions
        assert workflow is None
        
        # Verify database was called
        mock_database.workflows.find_one.assert_called_once_with({"workflow_id": "nonexistent_id"})
    
    @pytest.mark.asyncio
    async def test_update_workflow_success(self, workflow_crud, mock_database):
        """Test successful workflow update."""
        # Mock existing workflow
        existing_workflow = {
            "workflow_id": "test_id",
            "name": "Old Name",
            "description": "Old description",
            "steps": [],
            "tags": [],
            "parallel_execution": False,
            "timeout_minutes": 60,
            "status": "draft",
            "version": 1,
            "generated_by_llm": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "execution_count": 0
        }
        
        # Mock database response for update_one (need to return object with modified_count)
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_database.workflows.update_one.return_value = mock_result
        
        # Mock the get_workflow call after update - return the updated workflow
        updated_workflow = existing_workflow.copy()
        updated_workflow.update({
            "name": "New Name",
            "description": "New description",
            "tags": ["updated"]
        })
        # The update method calls get_workflow after updating, so return the updated workflow
        mock_database.workflows.find_one.return_value = updated_workflow
        
        # Update request
        update_request = WorkflowUpdateRequest(
            name="New Name",
            description="New description",
            tags=["updated"]
        )
        
        # Update workflow
        workflow = await workflow_crud.update_workflow("test_id", update_request)
        
        # Assertions
        assert workflow is not None
        assert workflow.name == "New Name"
        assert workflow.description == "New description"
        assert workflow.tags == ["updated"]
        
        # Verify database was called
        assert mock_database.workflows.find_one.call_count == 1
        mock_database.workflows.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_workflows_success(self, workflow_crud, mock_database):
        """Test listing workflows with pagination."""
        # Mock database response
        workflow_docs = [
            {
                "workflow_id": "wf_1",
                "name": "Workflow 1",
                "description": "First workflow",
                "steps": [],
                "tags": [],
                "parallel_execution": False,
                "timeout_minutes": 60,
                "status": "draft",
                "version": 1,
                "generated_by_llm": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "execution_count": 0
            },
            {
                "workflow_id": "wf_2",
                "name": "Workflow 2",
                "description": "Second workflow",
                "steps": [],
                "tags": [],
                "parallel_execution": False,
                "timeout_minutes": 60,
                "status": "active",
                "version": 1,
                "generated_by_llm": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "execution_count": 0
            }
        ]
        
        # Mock the cursor behavior for async iteration
        async def mock_async_iter():
            for doc in workflow_docs:
                yield doc
        
        # Create a proper mock for the cursor that supports method chaining
        final_cursor = MagicMock()
        final_cursor.__aiter__ = lambda self: mock_async_iter()
        
        # Create mock objects for the chain
        limit_mock = MagicMock()
        limit_mock.limit.return_value = final_cursor
        
        skip_mock = MagicMock()
        skip_mock.skip.return_value = limit_mock
        
        sort_mock = MagicMock()
        sort_mock.sort.return_value = skip_mock
        
        # Set up the find method to return the sort mock
        mock_database.workflows.find.return_value = sort_mock
        mock_database.workflows.count_documents.return_value = 2
        
        # List workflows
        result = await workflow_crud.list_workflows(skip=0, limit=10)
        workflows = result["workflows"]
        total = result["total"]
        
        # Assertions
        assert len(workflows) == 2
        assert total == 2
        assert all(isinstance(wf, Workflow) for wf in workflows)
        assert workflows[0].workflow_id == "wf_1"
        assert workflows[1].workflow_id == "wf_2"
        
        # Verify database was called
        mock_database.workflows.find.assert_called_once()
        mock_database.workflows.count_documents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_workflow_success(self, workflow_crud, mock_database):
        """Test successful workflow deletion."""
        # Mock database response
        mock_database.workflows.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Delete workflow
        result = await workflow_crud.delete_workflow("test_id")
        
        # Assertions
        assert result is True
        
        # Verify database was called
        mock_database.workflows.delete_one.assert_called_once_with({"workflow_id": "test_id"})
    
    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self, workflow_crud, mock_database):
        """Test deleting a non-existent workflow."""
        # Mock database response
        mock_database.workflows.delete_one.return_value = MagicMock(deleted_count=0)
        
        # Delete workflow
        result = await workflow_crud.delete_workflow("nonexistent_id")
        
        # Assertions
        assert result is False
        
        # Verify database was called
        mock_database.workflows.delete_one.assert_called_once_with({"workflow_id": "nonexistent_id"})


class TestWorkflowExecutionCRUD:
    """Test workflow execution CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_execution_success(self, workflow_crud, mock_database):
        """Test successful execution creation."""
        # Mock database insert
        mock_database.workflow_executions.insert_one.return_value = AsyncMock()
        
        # Create execution
        execution = await workflow_crud.create_execution(
            workflow_id="test_workflow",
            input_data={"key": "value"}
        )
        
        # Assertions
        assert isinstance(execution, WorkflowExecution)
        assert execution.workflow_id == "test_workflow"
        assert execution.execution_context == {"key": "value"}
        assert execution.status == WorkflowStatus.RUNNING
        assert isinstance(execution.execution_id, str)
        assert isinstance(execution.started_at, datetime)
        
        # Verify database was called
        mock_database.workflow_executions.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_execution_found(self, workflow_crud, mock_database):
        """Test getting an existing execution."""
        # Mock database response
        execution_doc = {
            "execution_id": "exec_123",
            "workflow_id": "wf_456",
            "status": "running",
            "current_step": None,
            "completed_steps": [],
            "failed_steps": [],
            "execution_context": {"key": "value"},
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "error_message": None,
            "error_step": None
        }
        mock_database.workflow_executions.find_one.return_value = execution_doc
        
        # Get execution
        execution = await workflow_crud.get_execution("exec_123")
        
        # Assertions
        assert execution is not None
        assert isinstance(execution, WorkflowExecution)
        assert execution.execution_id == "exec_123"
        assert execution.workflow_id == "wf_456"
        
        # Verify database was called
        mock_database.workflow_executions.find_one.assert_called_once_with({"execution_id": "exec_123"})
    
    @pytest.mark.asyncio
    async def test_update_execution_status(self, workflow_crud, mock_database):
        """Test updating execution status."""
        # Mock database update
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_database.workflow_executions.update_one.return_value = mock_result
        
        # Mock the get_execution call to return None (simulating the workflow updates without verification)
        mock_database.workflow_executions.find_one.return_value = None
        
        # Update execution using the general update_execution method
        update_data = {
            "status": "completed",
            "current_step": None,
            "completed_steps": ["step_1", "step_2"]
        }
        
        result = await workflow_crud.update_execution("exec_123", update_data)
        
        # Since we return None from find_one, the result should be None
        assert result is None
        
        # Verify database was called with correct parameters
        mock_database.workflow_executions.update_one.assert_called_once()
        call_args = mock_database.workflow_executions.update_one.call_args
        assert call_args[0][0] == {"execution_id": "exec_123"}
        update_set = call_args[0][1]["$set"]
        assert update_set["status"] == "completed"
        assert update_set["completed_steps"] == ["step_1", "step_2"]
