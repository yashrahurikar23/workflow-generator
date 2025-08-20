"""
Integration tests for workflow API endpoints.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime

from app.models.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowExecuteRequest,
    WorkflowGenerateRequest,
    StepType,
    WorkflowStepConfig,
    WorkflowStatus
)


class TestWorkflowAPI:
    """Test workflow API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_workflow_success(self, client: AsyncClient, sample_workflow_data):
        """Test successful workflow creation via API."""
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "workflow_id" in data
        assert data["name"] == sample_workflow_data["name"]
        assert data["description"] == sample_workflow_data["description"]
        assert len(data["steps"]) == len(sample_workflow_data["steps"])
        assert data["tags"] == sample_workflow_data["tags"]
        assert data["parallel_execution"] == sample_workflow_data["parallel_execution"]
        assert data["timeout_minutes"] == sample_workflow_data["timeout_minutes"]
        assert data["status"] == "draft"
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_workflow_invalid_data(self, client: AsyncClient):
        """Test workflow creation with invalid data."""
        invalid_data = {
            "name": "",  # Invalid: empty name
            "steps": [],
            "tags": [],
            "parallel_execution": False,
            "timeout_minutes": 30
        }
        
        response = await client.post("/api/v1/workflows/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_workflow_success(self, client: AsyncClient, sample_workflow_data):
        """Test getting an existing workflow."""
        # First create a workflow
        create_response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert create_response.status_code == 201
        workflow_id = create_response.json()["workflow_id"]
        
        # Then get it
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["workflow_id"] == workflow_id
        assert data["name"] == sample_workflow_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, client: AsyncClient):
        """Test getting a non-existent workflow."""
        response = await client.get("/api/v1/workflows/nonexistent_id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_workflow_success(self, client: AsyncClient, sample_workflow_data):
        """Test updating an existing workflow."""
        # First create a workflow
        create_response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert create_response.status_code == 201
        workflow_id = create_response.json()["workflow_id"]
        
        # Update it
        update_data = {
            "name": "Updated Workflow Name",
            "description": "Updated description",
            "tags": ["updated", "test"]
        }
        
        response = await client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Workflow Name"
        assert data["description"] == "Updated description"
        assert data["tags"] == ["updated", "test"]
    
    @pytest.mark.asyncio
    async def test_update_workflow_not_found(self, client: AsyncClient):
        """Test updating a non-existent workflow."""
        update_data = {"name": "New Name"}
        response = await client.put("/api/v1/workflows/nonexistent_id", json=update_data)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_workflows_empty(self, client: AsyncClient):
        """Test listing workflows when none exist."""
        response = await client.get("/api/v1/workflows/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["workflows"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 50
    
    @pytest.mark.asyncio
    async def test_list_workflows_with_data(self, client: AsyncClient, sample_workflow_data):
        """Test listing workflows with existing data."""
        # Create a few workflows
        for i in range(3):
            workflow_data = sample_workflow_data.copy()
            workflow_data["name"] = f"Test Workflow {i+1}"
            create_response = await client.post("/api/v1/workflows/", json=workflow_data)
            assert create_response.status_code == 201
        
        # List workflows
        response = await client.get("/api/v1/workflows/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["workflows"]) == 3
        assert data["total"] == 3
        assert all("workflow_id" in wf for wf in data["workflows"])
    
    @pytest.mark.asyncio
    async def test_list_workflows_with_pagination(self, client: AsyncClient, sample_workflow_data):
        """Test listing workflows with pagination."""
        # Create 5 workflows
        for i in range(5):
            workflow_data = sample_workflow_data.copy()
            workflow_data["name"] = f"Test Workflow {i+1}"
            create_response = await client.post("/api/v1/workflows/", json=workflow_data)
            assert create_response.status_code == 201
        
        # Test pagination
        response = await client.get("/api/v1/workflows/?skip=2&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["workflows"]) == 2
        assert data["total"] == 5
    
    @pytest.mark.asyncio
    async def test_delete_workflow_success(self, client: AsyncClient, sample_workflow_data):
        """Test successful workflow deletion."""
        # First create a workflow
        create_response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert create_response.status_code == 201
        workflow_id = create_response.json()["workflow_id"]
        
        # Delete it
        response = await client.delete(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self, client: AsyncClient):
        """Test deleting a non-existent workflow."""
        response = await client.delete("/api/v1/workflows/nonexistent_id")
        assert response.status_code == 404


class TestWorkflowExecutionAPI:
    """Test workflow execution API endpoints."""
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, client: AsyncClient, sample_workflow_data):
        """Test successful workflow execution."""
        # First create a workflow
        create_response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert create_response.status_code == 201
        workflow_id = create_response.json()["workflow_id"]
        
        # Activate the workflow so it can be executed
        update_data = {"status": "active"}
        update_response = await client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
        assert update_response.status_code == 200
        
        # Execute it
        execute_data = {
            "input_data": {"user_id": "123", "action": "process"}
        }
        
        response = await client.post(f"/api/v1/workflows/{workflow_id}/execute", json=execute_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "execution_id" in data
        assert data["workflow_id"] == workflow_id
        assert data["status"] == "running"
        assert data["execution_context"] == execute_data["input_data"]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, client: AsyncClient):
        """Test executing a non-existent workflow."""
        execute_data = {"input_data": {}}
        response = await client.post("/api/v1/workflows/nonexistent_id/execute", json=execute_data)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_execution_success(self, client: AsyncClient, sample_workflow_data):
        """Test getting an execution."""
        # Create workflow and execute it
        create_response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert create_response.status_code == 201
        workflow_id = create_response.json()["workflow_id"]
        
        # Activate the workflow so it can be executed
        update_data = {"status": "active"}
        update_response = await client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
        assert update_response.status_code == 200
        
        execute_data = {"input_data": {"test": "data"}}
        execute_response = await client.post(f"/api/v1/workflows/{workflow_id}/execute", json=execute_data)
        assert execute_response.status_code == 201
        execution_id = execute_response.json()["execution_id"]
        
        # Get the execution
        response = await client.get(f"/api/v1/workflows/executions/{execution_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["execution_id"] == execution_id
        assert data["workflow_id"] == workflow_id
    
    @pytest.mark.asyncio
    async def test_get_execution_not_found(self, client: AsyncClient):
        """Test getting a non-existent execution."""
        response = await client.get("/api/v1/workflows/executions/nonexistent_id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_executions_for_workflow(self, client: AsyncClient, sample_workflow_data):
        """Test listing executions for a workflow."""
        # Create workflow
        create_response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert create_response.status_code == 201
        workflow_id = create_response.json()["workflow_id"]
        
        # Activate the workflow so it can be executed
        update_data = {"status": "active"}
        update_response = await client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
        assert update_response.status_code == 200
        
        # Create multiple executions
        for i in range(3):
            execute_data = {"input_data": {"run": i}}
            execute_response = await client.post(f"/api/v1/workflows/{workflow_id}/execute", json=execute_data)
            assert execute_response.status_code == 201
        
        # List executions
        response = await client.get(f"/api/v1/workflows/{workflow_id}/executions")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["executions"]) == 3
        assert data["total"] == 3
        assert all(exec["workflow_id"] == workflow_id for exec in data["executions"])


class TestWorkflowGenerationAPI:
    """Test workflow generation API endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_workflow_success(self, client: AsyncClient):
        """Test successful workflow generation."""
        generate_data = {
            "prompt": "Create a workflow that processes user data from an API, validates it, and sends email notifications",
            "additional_context": "Focus on data validation and error handling",
            "preferred_steps": ["api_call", "data_transform", "email"]
        }
        
        response = await client.post("/api/v1/workflows/generate", json=generate_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "workflow_id" in data
        assert data["generated_by_llm"] is True
        assert data["generation_prompt"] == generate_data["prompt"]
        assert len(data["steps"]) > 0
        
        # Check that the generated steps include some of the preferred types
        step_types = [step["step_type"] for step in data["steps"]]
        assert any(step_type in generate_data["preferred_steps"] for step_type in step_types)
    
    @pytest.mark.asyncio
    async def test_generate_workflow_invalid_prompt(self, client: AsyncClient):
        """Test workflow generation with invalid prompt."""
        generate_data = {
            "prompt": "short"  # Too short
        }
        
        response = await client.post("/api/v1/workflows/generate", json=generate_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_generate_workflow_minimal_data(self, client: AsyncClient):
        """Test workflow generation with minimal required data."""
        generate_data = {
            "prompt": "Create a simple workflow that sends an email notification when a user signs up"
        }
        
        response = await client.post("/api/v1/workflows/generate", json=generate_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "workflow_id" in data
        assert data["generated_by_llm"] is True
        assert data["generation_prompt"] == generate_data["prompt"]
        assert len(data["steps"]) > 0
