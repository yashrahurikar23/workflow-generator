"""
Test configuration and fixtures for pytest.
"""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from app.main import app
from app.core.config import Settings, settings
from app.core.database import get_database


class TestSettings(Settings):
    """Test configuration settings."""
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "workflow_generator_test"
    PROJECT_NAME: str = "Workflow Generator Test"
    
    class Config:
        env_file = ".env.test"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """Create test settings."""
    return TestSettings()


@pytest_asyncio.fixture(scope="function")
async def mock_db() -> AsyncGenerator[AsyncMongoMockClient, None]:
    """Create a mock MongoDB database for testing."""
    client = AsyncMongoMockClient()
    db = client.workflow_generator_test
    yield db
    client.close()


@pytest_asyncio.fixture(scope="function")
async def app_with_mock_db(mock_db: AsyncMongoMockClient):
    """Create FastAPI app with mocked database."""
    # Override the database dependency
    async def get_test_database():
        return mock_db
    
    app.dependency_overrides[get_database] = get_test_database
    yield app
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(app_with_mock_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app_with_mock_db), 
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_workflow_data() -> dict:
    """Sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for unit testing",
        "steps": [
            {
                "step_id": "step_1",
                "name": "API Call Step",
                "step_type": "api_call",
                "description": "Make an API call",
                "config": {
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {"Authorization": "Bearer token"}
                },
                "depends_on": [],
                "condition": None
            },
            {
                "step_id": "step_2",
                "name": "Data Transform Step",
                "step_type": "data_transform",
                "description": "Transform the data",
                "config": {
                    "transformation": "filter",
                    "criteria": {"status": "active"}
                },
                "depends_on": ["step_1"],
                "condition": None
            }
        ],
        "tags": ["test", "api"],
        "parallel_execution": False,
        "timeout_minutes": 30
    }


@pytest.fixture
def sample_workflow_execution_data() -> dict:
    """Sample workflow execution data for testing."""
    return {
        "workflow_id": "test_workflow_id",
        "trigger": "manual",
        "input_data": {"user_id": "123", "action": "process"},
        "context": {"environment": "test"}
    }


@pytest.fixture
def sample_step_results() -> list:
    """Sample step execution results."""
    return [
        {
            "step_id": "step_1",
            "status": "completed",
            "output": {"data": [1, 2, 3], "count": 3},
            "error": None,
            "execution_time": 1.5,
            "started_at": "2024-01-01T10:00:00",
            "completed_at": "2024-01-01T10:00:01.5"
        },
        {
            "step_id": "step_2",
            "status": "completed",
            "output": {"filtered_data": [1, 2], "count": 2},
            "error": None,
            "execution_time": 0.8,
            "started_at": "2024-01-01T10:00:02",
            "completed_at": "2024-01-01T10:00:02.8"
        }
    ]


# Utility functions for tests
def assert_workflow_structure(workflow: dict) -> None:
    """Assert that a workflow has the expected structure."""
    required_fields = ["id", "name", "description", "steps", "tags", "parallel_execution", 
                      "timeout_minutes", "created_at", "updated_at", "is_active"]
    for field in required_fields:
        assert field in workflow, f"Missing required field: {field}"
    
    assert isinstance(workflow["steps"], list), "Steps should be a list"
    assert isinstance(workflow["tags"], list), "Tags should be a list"
    assert isinstance(workflow["parallel_execution"], bool), "parallel_execution should be boolean"
    assert isinstance(workflow["timeout_minutes"], int), "timeout_minutes should be integer"


def assert_execution_structure(execution: dict) -> None:
    """Assert that an execution has the expected structure."""
    required_fields = ["id", "workflow_id", "status", "trigger", "input_data", 
                      "context", "step_results", "created_at", "started_at"]
    for field in required_fields:
        assert field in execution, f"Missing required field: {field}"
    
    assert isinstance(execution["step_results"], list), "step_results should be a list"
    assert execution["status"] in ["pending", "running", "completed", "failed", "cancelled"], \
        f"Invalid status: {execution['status']}"
