import logging
from typing import Any, Dict, List

from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class MockDatabase:
    """Mock database for development when MongoDB is not available"""
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {
            "workflows": [],
            "workflow_executions": [],
            "threads": [],
            "messages": [],
            "chat_threads": [],
            "chat_messages": []
        }
        # Create collection attributes for easier access
        self.workflows = MockCollection(self.collections["workflows"])
        self.workflow_executions = MockCollection(self.collections["workflow_executions"])
        self.threads = MockCollection(self.collections["threads"])
        self.messages = MockCollection(self.collections["messages"])
        self.chat_threads = MockCollection(self.collections["chat_threads"])
        self.chat_messages = MockCollection(self.collections["chat_messages"])
    
    def __getitem__(self, collection_name: str):
        return MockCollection(self.collections.setdefault(collection_name, []))

class MockCollection:
    """Mock MongoDB collection"""
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
    
    async def find(self, filter_dict=None, limit=None, skip=None):
        """Mock find operation"""
        result = self.data if filter_dict is None else [item for item in self.data if self._matches_filter(item, filter_dict)]
        if skip:
            result = result[skip:]
        if limit:
            result = result[:limit]
        return MockCursor(result)
    
    async def find_one(self, filter_dict=None):
        """Mock find_one operation"""
        for item in self.data:
            if filter_dict is None or self._matches_filter(item, filter_dict):
                return item
        return None
    
    async def insert_one(self, document):
        """Mock insert_one operation"""
        # Generate a simple ID if not provided
        if "_id" not in document:
            document["_id"] = f"mock_id_{len(self.data)}"
        self.data.append(document)
        return MockInsertResult(document["_id"])
    
    async def update_one(self, filter_dict, update_dict):
        """Mock update_one operation"""
        for item in self.data:
            if self._matches_filter(item, filter_dict):
                if "$set" in update_dict:
                    item.update(update_dict["$set"])
                return MockUpdateResult(True)
        return MockUpdateResult(False)
    
    async def delete_one(self, filter_dict):
        """Mock delete_one operation"""
        for i, item in enumerate(self.data):
            if self._matches_filter(item, filter_dict):
                del self.data[i]
                return MockDeleteResult(True)
        return MockDeleteResult(False)
    
    async def count_documents(self, filter_dict=None):
        """Mock count_documents operation"""
        if filter_dict is None:
            return len(self.data)
        count = 0
        for item in self.data:
            if self._matches_filter(item, filter_dict):
                count += 1
        return count
    
    def sort(self, field, direction=-1):
        """Mock sort operation - returns self for chaining"""
        # Sort the data in place
        reverse = (direction == -1)
        try:
            self.data.sort(key=lambda x: x.get(field, ""), reverse=reverse)
        except (TypeError, KeyError):
            pass  # If sorting fails, just return unsorted
        return self
    
    def skip(self, count):
        """Mock skip operation - returns self for chaining"""
        self.data = self.data[count:]
        return self
    
    def limit(self, count):
        """Mock limit operation - returns self for chaining"""
        self.data = self.data[:count]
        return self
    
    async def aggregate(self, pipeline):
        """Mock aggregate operation - simplified implementation"""
        # For now, just return the original data
        # In a real implementation, this would process the pipeline
        return MockCursor(self.data)

    def _matches_filter(self, item: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Simple filter matching"""
        for key, value in filter_dict.items():
            if key not in item or item[key] != value:
                return False
        return True

class MockCursor:
    """Mock MongoDB cursor"""
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        result = self.data[self.index]
        self.index += 1
        return result
    
    async def to_list(self, length=None):
        return self.data[:length] if length else self.data

class MockInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockUpdateResult:
    def __init__(self, modified):
        self.modified_count = 1 if modified else 0

class MockDeleteResult:
    def __init__(self, deleted):
        self.deleted_count = 1 if deleted else 0

class Database:
    client: AsyncIOMotorClient = None
    database = None
    mock_database: MockDatabase = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    if settings.USE_MOCK_DATABASE:
        logger.info("Using mock database for development")
        db.mock_database = MockDatabase()
        db.database = db.mock_database
        await initialize_mock_data()
        logger.info("Mock database initialized")
    else:
        try:
            logger.info("Connecting to MongoDB...")
            db.client = AsyncIOMotorClient(settings.MONGODB_URL)
            db.database = db.client[settings.DATABASE_NAME]
            
            # Test the connection
            await db.client.admin.command('ping')
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.info("Falling back to mock database")
            db.mock_database = MockDatabase()
            db.database = db.mock_database
            await initialize_mock_data()

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        logger.info("Closing connection to MongoDB...")
        db.client.close()
        logger.info("Disconnected from MongoDB")
    else:
        logger.info("Mock database - no connection to close")

async def get_database():
    """Get database instance"""
    return db.database

async def initialize_mock_data():
    """Initialize mock database with sample data"""
    if not settings.USE_MOCK_DATABASE or not db.mock_database:
        return
    
    logger.info("Initializing mock database with sample data")
    
    # Sample workflows
    sample_workflows = [
        {
            "_id": "workflow_1",
            "workflow_id": "workflow_1",
            "name": "Data Processing Pipeline",
            "description": "Complex data pipeline for ETL operations with parallel processing",
            "tags": ["data", "pipeline", "etl"],
            "workflow_type": "data_processing",
            "status": "active",
            "parallel_execution": True,
            "steps": [
                {
                    "step_id": "step_1",
                    "name": "Collect User Data",
                    "step_type": "data_transform",
                    "description": "Gather user behavior data from various sources",
                    "depends_on": [],
                    "config": {"source": "user_analytics"}
                },
                {
                    "step_id": "step_2", 
                    "name": "Segment Users",
                    "step_type": "condition",
                    "description": "Segment users based on behavior patterns",
                    "depends_on": ["step_1"],
                    "config": {"criteria": "engagement_score"}
                },
                {
                    "step_id": "step_3",
                    "name": "Generate Reports",
                    "step_type": "llm_process", 
                    "description": "Use AI to generate personalized email content",
                    "depends_on": ["step_2"],
                    "config": {"model": "gpt-4"}
                },
                {
                    "step_id": "step_4",
                    "name": "Send Emails",
                    "step_type": "email",
                    "description": "Send personalized emails to segmented users",
                    "depends_on": ["step_3"], 
                    "config": {"template": "marketing_campaign"}
                },
                {
                    "step_id": "step_5",
                    "name": "Track Results",
                    "step_type": "database",
                    "description": "Store campaign results and user responses",
                    "depends_on": ["step_4"],
                    "config": {"table": "campaign_metrics"}
                }
            ],
            "created_at": "2025-08-21T10:00:00Z",
            "updated_at": "2025-08-21T10:00:00Z",
            "execution_count": 15
        },
        {
            "_id": "workflow_2",
            "workflow_id": "workflow_2", 
            "name": "Email Marketing Campaign",
            "description": "Automated email marketing workflow that sends personalized emails based on user behavior",
            "tags": ["marketing", "email", "automation"],
            "workflow_type": "marketing",
            "status": "active",
            "parallel_execution": False,
            "steps": [
                {
                    "step_id": "collect_data",
                    "name": "Collect User Data", 
                    "step_type": "data_transform",
                    "description": "Gather user behavior data from various sources",
                    "depends_on": [],
                    "config": {"source": "user_analytics"}
                },
                {
                    "step_id": "segment_users",
                    "name": "Segment Users",
                    "step_type": "condition", 
                    "description": "Segment users based on behavior patterns",
                    "depends_on": ["collect_data"],
                    "config": {"criteria": "engagement_score"}
                },
                {
                    "step_id": "generate_content",
                    "name": "Generate Content",
                    "step_type": "llm_process",
                    "description": "Use AI to generate personalized email content", 
                    "depends_on": ["segment_users"],
                    "config": {"model": "gpt-4"}
                },
                {
                    "step_id": "send_emails",
                    "name": "Send Emails",
                    "step_type": "email",
                    "description": "Send personalized emails to segmented users",
                    "depends_on": ["generate_content"],
                    "config": {"template": "marketing_campaign"}
                }
            ],
            "created_at": "2025-08-20T14:30:00Z", 
            "updated_at": "2025-08-20T14:30:00Z",
            "execution_count": 8
        },
        {
            "_id": "workflow_3",
            "workflow_id": "workflow_3",
            "name": "Customer Onboarding Flow", 
            "description": "Comprehensive workflow for onboarding new customers with manual approval steps",
            "tags": ["onboarding", "customers"],
            "workflow_type": "customer_management",
            "status": "draft",
            "parallel_execution": False,
            "steps": [
                {
                    "step_id": "welcome_email",
                    "name": "Send Welcome Email",
                    "step_type": "email",
                    "description": "Send welcome email to new customer",
                    "depends_on": [],
                    "config": {"template": "welcome"}
                },
                {
                    "step_id": "setup_account", 
                    "name": "Setup Account",
                    "step_type": "api_call",
                    "description": "Create customer account in CRM",
                    "depends_on": ["welcome_email"],
                    "config": {"endpoint": "/api/customers"}
                },
                {
                    "step_id": "manual_review",
                    "name": "Manual Review",
                    "step_type": "manual", 
                    "description": "Manual review of customer information",
                    "depends_on": ["setup_account"],
                    "config": {"assignee": "customer_success"}
                },
                {
                    "step_id": "send_guidelines",
                    "name": "Send Guidelines",
                    "step_type": "email",
                    "description": "Send usage guidelines and best practices",
                    "depends_on": ["manual_review"],
                    "config": {"template": "guidelines"}
                },
                {
                    "step_id": "log_completion",
                    "name": "Log Completion", 
                    "step_type": "database",
                    "description": "Log successful onboarding completion",
                    "depends_on": ["send_guidelines"],
                    "config": {"table": "onboarding_log"}
                }
            ],
            "created_at": "2025-08-19T09:15:00Z",
            "updated_at": "2025-08-22T16:45:00Z", 
            "execution_count": 3
        }
    ]
    
    # Add sample workflows to mock database
    for workflow in sample_workflows:
        await db.mock_database["workflows"].insert_one(workflow)
    
    logger.info(f"Initialized mock database with {len(sample_workflows)} sample workflows")
