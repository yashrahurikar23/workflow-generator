# Workflow Generator App - Engineering Architecture Document

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                            │
├─────────────────────────────────────────────────────────────┤
│  React Frontend (Vite)                                     │
│  ├── React Flow (Visual Editor)                            │
│  ├── UI Components (shadcn/ui)                             │
│  ├── State Management (Zustand)                            │
│  └── API Client (Axios/Fetch)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTP/WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Application                                        │
│  ├── Authentication & Authorization                         │
│  ├── Rate Limiting & Validation                            │
│  ├── WebSocket for Real-time Updates                       │
│  └── API Documentation (OpenAPI)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Workflow Engine (LlamaIndex + Custom)                     │
│  ├── Workflow Definition Management                         │
│  ├── AI Workflow Generation (LlamaIndex)                   │
│  ├── Execution Engine                                       │
│  ├── Node Type Registry                                     │
│  └── Integration Manager                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  MongoDB                                                    │
│  ├── Workflows Collection                                   │
│  ├── Executions Collection                                  │
│  ├── Users Collection                                       │
│  └── Templates Collection                                   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

#### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite (fast development and building)
- **Visual Editor**: React Flow (@xyflow/react)
- **UI Components**: shadcn/ui + Tailwind CSS
- **State Management**: Zustand (lightweight alternative to Redux)
- **HTTP Client**: Axios with interceptors
- **Form Handling**: React Hook Form + Zod validation

#### Backend
- **Framework**: FastAPI (Python)
- **ASGI Server**: Uvicorn
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens with FastAPI security
- **AI Framework**: LlamaIndex for workflow generation
- **Background Tasks**: Celery with Redis
- **WebSocket**: FastAPI WebSocket support

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Process Management**: PM2 or similar
- **Reverse Proxy**: Nginx (production)
- **Monitoring**: Prometheus + Grafana (future)

## 2. Frontend Architecture

### 2.1 Project Structure

```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── workflow/        # Workflow-specific components
│   │   │   ├── WorkflowEditor.tsx
│   │   │   ├── NodePalette.tsx
│   │   │   ├── NodeConfig.tsx
│   │   │   └── ExecutionMonitor.tsx
│   │   └── layout/          # Layout components
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx
│   │   ├── WorkflowEditor.tsx
│   │   └── WorkflowList.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useWorkflow.ts
│   │   ├── useExecution.ts
│   │   └── useWebSocket.ts
│   ├── stores/              # Zustand stores
│   │   ├── workflowStore.ts
│   │   ├── authStore.ts
│   │   └── executionStore.ts
│   ├── types/               # TypeScript type definitions
│   │   ├── workflow.ts
│   │   ├── node.ts
│   │   └── api.ts
│   ├── services/            # API services
│   │   ├── api.ts
│   │   ├── workflow.ts
│   │   └── auth.ts
│   └── utils/               # Utility functions
│       ├── validation.ts
│       └── constants.ts
├── public/
└── package.json
```

### 2.2 Key React Flow Implementation

```typescript
// components/workflow/WorkflowEditor.tsx
import { useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Node,
  Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { NodePalette } from './NodePalette';
import { NodeConfig } from './NodeConfig';
import { ExecutionMonitor } from './ExecutionMonitor';

export function WorkflowEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeAdd = useCallback((nodeType: string) => {
    const newNode: Node = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType,
      position: { x: 100, y: 100 },
      data: { label: nodeType }
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  return (
    <div className="h-screen flex">
      <NodePalette onNodeAdd={onNodeAdd} />
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
      <NodeConfig />
      <ExecutionMonitor />
    </div>
  );
}
```

### 2.3 State Management with Zustand

```typescript
// stores/workflowStore.ts
import { create } from 'zustand';
import { Node, Edge } from '@xyflow/react';

interface WorkflowState {
  // State
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  isExecuting: boolean;
  executionResult: any;

  // Actions
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  setSelectedNode: (node: Node | null) => void;
  updateNode: (nodeId: string, data: any) => void;
  executeWorkflow: () => Promise<void>;
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  isExecuting: false,
  executionResult: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setSelectedNode: (selectedNode) => set({ selectedNode }),
  
  updateNode: (nodeId, data) => {
    const { nodes } = get();
    const updatedNodes = nodes.map(node => 
      node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
    );
    set({ nodes: updatedNodes });
  },

  executeWorkflow: async () => {
    const { nodes, edges } = get();
    set({ isExecuting: true });
    
    try {
      const response = await workflowService.execute({ nodes, edges });
      set({ executionResult: response.data, isExecuting: false });
    } catch (error) {
      console.error('Workflow execution failed:', error);
      set({ isExecuting: false });
    }
  }
}));
```

## 3. Backend Architecture

### 3.1 Project Structure

```
backend/
├── app/
│   ├── api/                 # API routes
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── workflows.py
│   │   │   ├── executions.py
│   │   │   ├── auth.py
│   │   │   └── ai.py
│   │   └── deps.py         # Dependencies
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration
│   │   ├── security.py     # Security utilities
│   │   └── database.py     # Database connection
│   ├── models/             # Pydantic models
│   │   ├── workflow.py
│   │   ├── execution.py
│   │   └── user.py
│   ├── services/           # Business logic
│   │   ├── workflow_service.py
│   │   ├── execution_service.py
│   │   ├── ai_service.py
│   │   └── node_registry.py
│   ├── nodes/              # Node implementations
│   │   ├── base.py
│   │   ├── trigger.py
│   │   ├── action.py
│   │   └── condition.py
│   └── main.py            # FastAPI app entry point
├── tests/
├── requirements.txt
└── Dockerfile
```

### 3.2 FastAPI Application Setup

```python
# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import workflows, executions, auth, ai
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Workflow Generator API",
    description="API for visual workflow generation and execution",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(executions.router, prefix="/api/v1/executions", tags=["executions"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    # Handle real-time execution updates
    try:
        while True:
            data = await websocket.receive_text()
            # Process WebSocket messages
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
```

### 3.3 Workflow Models

```python
# app/models/workflow.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class NodeData(BaseModel):
    label: str
    config: Dict[str, Any] = {}

class WorkflowNode(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: NodeData

class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class WorkflowDefinition(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    created_by: str
    created_at: str
    updated_at: str
    version: int = 1
    status: str = "draft"  # draft, published, archived

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode] = []
    edges: List[WorkflowEdge] = []

class WorkflowUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[WorkflowNode]] = None
    edges: Optional[List[WorkflowEdge]] = None
```

### 3.4 LlamaIndex Integration

```python
# app/services/ai_service.py
import json
from typing import List, Dict, Any
from llama_index.core import Settings
from llama_index.core.workflow import (
    Workflow, 
    StartEvent, 
    StopEvent, 
    step,
    Context
)
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage

from app.models.workflow import WorkflowNode, WorkflowEdge

class WorkflowGenerationEvent(BaseModel):
    user_prompt: str
    available_nodes: List[str]

class WorkflowGeneratorWorkflow(Workflow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = OpenAI(model="gpt-4")
        
    @step
    async def generate_workflow(
        self, 
        ctx: Context, 
        ev: StartEvent
    ) -> StopEvent:
        """Generate workflow from natural language description"""
        
        system_prompt = """
        You are a workflow generation expert. Convert natural language 
        descriptions into structured workflow definitions using available nodes.
        
        Available Node Types:
        - trigger: Start workflow (webhook, schedule, manual)
        - http_request: Make HTTP API calls
        - transform: Transform/process data
        - condition: If/else logic
        - email: Send emails
        - delay: Wait/pause execution
        
        Return a JSON object with 'nodes' and 'edges' arrays.
        Each node should have: id, type, position {x, y}, data {label, config}
        Each edge should have: id, source, target
        """
        
        user_prompt = ev.get("prompt", "")
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]
        
        response = await self.llm.achat(messages)
        
        try:
            workflow_data = json.loads(response.message.content)
            return StopEvent(result=workflow_data)
        except json.JSONDecodeError:
            # Fallback to simple workflow
            return StopEvent(result={
                "nodes": [
                    {
                        "id": "start",
                        "type": "trigger",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Manual Trigger"}
                    }
                ],
                "edges": []
            })

class AIService:
    def __init__(self):
        self.workflow_generator = WorkflowGeneratorWorkflow()
    
    async def generate_workflow_from_prompt(
        self, 
        prompt: str
    ) -> Dict[str, Any]:
        """Generate workflow from natural language prompt"""
        
        handler = self.workflow_generator.run(prompt=prompt)
        result = await handler
        
        return result

    async def suggest_next_nodes(
        self, 
        current_nodes: List[WorkflowNode],
        context: str = ""
    ) -> List[Dict[str, Any]]:
        """Suggest next possible nodes based on current workflow state"""
        
        # Implementation for node suggestions
        # This could use a simpler LLM call or rule-based logic
        
        suggestions = []
        
        # Simple rule-based suggestions for MVP
        last_node_types = [node.type for node in current_nodes[-3:]]
        
        if "trigger" in last_node_types and "http_request" not in last_node_types:
            suggestions.append({
                "type": "http_request",
                "label": "HTTP Request",
                "description": "Make an API call"
            })
        
        if "http_request" in last_node_types and "transform" not in last_node_types:
            suggestions.append({
                "type": "transform",
                "label": "Transform Data",
                "description": "Process the API response"
            })
        
        return suggestions

ai_service = AIService()
```

### 3.5 Execution Engine

```python
# app/services/execution_service.py
import asyncio
import uuid
from typing import Dict, Any, List
from datetime import datetime

from app.models.workflow import WorkflowDefinition, WorkflowNode
from app.models.execution import ExecutionResult, NodeExecution
from app.services.node_registry import node_registry
from app.core.database import get_database

class ExecutionContext:
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.variables = {}
        self.results = {}
        
    def set_variable(self, key: str, value: Any):
        self.variables[key] = value
        
    def get_variable(self, key: str, default=None):
        return self.variables.get(key, default)

class WorkflowExecutionService:
    def __init__(self):
        self.db = None
    
    async def execute_workflow(
        self, 
        workflow: WorkflowDefinition,
        trigger_data: Dict[str, Any] = None
    ) -> ExecutionResult:
        """Execute a complete workflow"""
        
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(execution_id)
        
        if trigger_data:
            context.set_variable("trigger_data", trigger_data)
        
        # Create execution record
        execution = ExecutionResult(
            id=execution_id,
            workflow_id=str(workflow.id),
            status="running",
            started_at=datetime.utcnow(),
            node_executions=[]
        )
        
        try:
            # Find start node(s)
            trigger_nodes = [
                node for node in workflow.nodes 
                if node.type == "trigger"
            ]
            
            if not trigger_nodes:
                raise ValueError("No trigger node found")
            
            # Execute workflow starting from triggers
            for trigger_node in trigger_nodes:
                await self._execute_node_chain(
                    workflow, 
                    trigger_node, 
                    context,
                    execution
                )
            
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
        
        # Save execution result
        await self._save_execution(execution)
        
        return execution
    
    async def _execute_node_chain(
        self,
        workflow: WorkflowDefinition,
        start_node: WorkflowNode,
        context: ExecutionContext,
        execution: ExecutionResult
    ):
        """Execute a chain of nodes starting from start_node"""
        
        current_node = start_node
        
        while current_node:
            # Execute current node
            node_result = await self._execute_single_node(
                current_node, 
                context
            )
            
            # Record node execution
            node_execution = NodeExecution(
                node_id=current_node.id,
                node_type=current_node.type,
                status="completed" if node_result.success else "failed",
                input_data=node_result.input_data,
                output_data=node_result.output_data,
                error=node_result.error,
                started_at=node_result.started_at,
                completed_at=node_result.completed_at
            )
            
            execution.node_executions.append(node_execution)
            
            if not node_result.success:
                break
            
            # Find next node(s)
            next_nodes = self._get_next_nodes(workflow, current_node.id)
            
            # For now, handle simple linear flow
            # TODO: Handle conditional branching and parallel execution
            current_node = next_nodes[0] if next_nodes else None
    
    async def _execute_single_node(
        self, 
        node: WorkflowNode, 
        context: ExecutionContext
    ):
        """Execute a single workflow node"""
        
        node_class = node_registry.get_node(node.type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node.type}")
        
        node_instance = node_class(node.data.config)
        return await node_instance.execute(context)
    
    def _get_next_nodes(
        self, 
        workflow: WorkflowDefinition, 
        current_node_id: str
    ) -> List[WorkflowNode]:
        """Get the next nodes to execute after current_node_id"""
        
        # Find edges from current node
        outgoing_edges = [
            edge for edge in workflow.edges 
            if edge.source == current_node_id
        ]
        
        # Get target nodes
        next_node_ids = [edge.target for edge in outgoing_edges]
        next_nodes = [
            node for node in workflow.nodes 
            if node.id in next_node_ids
        ]
        
        return next_nodes
    
    async def _save_execution(self, execution: ExecutionResult):
        """Save execution result to database"""
        if not self.db:
            self.db = await get_database()
        
        await self.db.executions.insert_one(execution.dict())

execution_service = WorkflowExecutionService()
```

## 4. Node System Architecture

### 4.1 Base Node Implementation

```python
# app/nodes/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel

class NodeExecutionResult(BaseModel):
    success: bool
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = {}
    error: str = None
    started_at: datetime
    completed_at: datetime

class BaseNode(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, context) -> NodeExecutionResult:
        """Execute the node logic"""
        pass
    
    def validate_config(self) -> bool:
        """Validate node configuration"""
        return True
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Return JSON schema for node configuration"""
        return {}
```

### 4.2 Specific Node Implementations

```python
# app/nodes/http_request.py
import aiohttp
from typing import Dict, Any
from app.nodes.base import BaseNode, NodeExecutionResult
from datetime import datetime

class HttpRequestNode(BaseNode):
    @classmethod
    def get_config_schema(cls):
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "headers": {"type": "object"},
                "body": {"type": "object"}
            },
            "required": ["url", "method"]
        }
    
    async def execute(self, context) -> NodeExecutionResult:
        started_at = datetime.utcnow()
        
        try:
            url = self.config.get("url")
            method = self.config.get("method", "GET")
            headers = self.config.get("headers", {})
            body = self.config.get("body")
            
            # Replace variables in config with context values
            url = self._replace_variables(url, context)
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body
                ) as response:
                    result_data = await response.json()
                    
                    # Store result in context for next nodes
                    context.set_variable("last_response", result_data)
                    
                    return NodeExecutionResult(
                        success=True,
                        input_data=self.config,
                        output_data=result_data,
                        started_at=started_at,
                        completed_at=datetime.utcnow()
                    )
                    
        except Exception as e:
            return NodeExecutionResult(
                success=False,
                input_data=self.config,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow()
            )
    
    def _replace_variables(self, text: str, context) -> str:
        """Replace {{variable}} placeholders with context values"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get_variable(var_name, match.group(0)))
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, text)
```

### 4.3 Node Registry

```python
# app/services/node_registry.py
from typing import Dict, Type
from app.nodes.base import BaseNode
from app.nodes.trigger import TriggerNode
from app.nodes.http_request import HttpRequestNode
from app.nodes.transform import TransformNode
from app.nodes.condition import ConditionNode

class NodeRegistry:
    def __init__(self):
        self._nodes: Dict[str, Type[BaseNode]] = {}
        self._register_built_in_nodes()
    
    def _register_built_in_nodes(self):
        """Register all built-in node types"""
        self.register("trigger", TriggerNode)
        self.register("http_request", HttpRequestNode)
        self.register("transform", TransformNode)
        self.register("condition", ConditionNode)
    
    def register(self, node_type: str, node_class: Type[BaseNode]):
        """Register a new node type"""
        self._nodes[node_type] = node_class
    
    def get_node(self, node_type: str) -> Type[BaseNode]:
        """Get node class by type"""
        return self._nodes.get(node_type)
    
    def get_available_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all available node types with their schemas"""
        return {
            node_type: {
                "class": node_class.__name__,
                "config_schema": node_class.get_config_schema()
            }
            for node_type, node_class in self._nodes.items()
        }

node_registry = NodeRegistry()
```

## 5. Database Design

### 5.1 MongoDB Collections

```javascript
// Workflows Collection
{
  "_id": ObjectId,
  "name": "My Workflow",
  "description": "Description of workflow",
  "nodes": [
    {
      "id": "node-1",
      "type": "trigger",
      "position": {"x": 100, "y": 100},
      "data": {
        "label": "Manual Trigger",
        "config": {}
      }
    },
    {
      "id": "node-2", 
      "type": "http_request",
      "position": {"x": 300, "y": 100},
      "data": {
        "label": "API Call",
        "config": {
          "url": "https://api.example.com/data",
          "method": "GET"
        }
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2"
    }
  ],
  "created_by": "user-id",
  "created_at": ISODate,
  "updated_at": ISODate,
  "version": 1,
  "status": "published"
}

// Executions Collection
{
  "_id": ObjectId,
  "workflow_id": ObjectId,
  "status": "completed", // running, completed, failed
  "started_at": ISODate,
  "completed_at": ISODate,
  "trigger_data": {},
  "node_executions": [
    {
      "node_id": "node-1",
      "node_type": "trigger",
      "status": "completed",
      "input_data": {},
      "output_data": {},
      "error": null,
      "started_at": ISODate,
      "completed_at": ISODate
    }
  ],
  "final_result": {},
  "error": null
}

// Users Collection  
{
  "_id": ObjectId,
  "email": "user@example.com",
  "hashed_password": "...",
  "full_name": "User Name",
  "is_active": true,
  "created_at": ISODate,
  "last_login": ISODate
}
```

### 5.2 Database Indexes

```python
# app/core/database.py
import motor.motor_asyncio
from app.core.config import settings

async def create_indexes():
    """Create database indexes for performance"""
    db = await get_database()
    
    # Workflows indexes
    await db.workflows.create_index([("created_by", 1), ("created_at", -1)])
    await db.workflows.create_index([("name", "text"), ("description", "text")])
    await db.workflows.create_index("status")
    
    # Executions indexes
    await db.executions.create_index([("workflow_id", 1), ("started_at", -1)])
    await db.executions.create_index("status")
    await db.executions.create_index("started_at")
    
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
```

## 6. API Design

### 6.1 REST API Endpoints

```python
# app/api/v1/workflows.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.workflow import (
    WorkflowDefinition, 
    WorkflowCreateRequest, 
    WorkflowUpdateRequest
)
from app.services.workflow_service import workflow_service
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[WorkflowDefinition])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """List all workflows for the current user"""
    return await workflow_service.list_workflows(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=WorkflowDefinition)
async def create_workflow(
    workflow_data: WorkflowCreateRequest,
    current_user = Depends(get_current_user)
):
    """Create a new workflow"""
    return await workflow_service.create_workflow(
        workflow_data=workflow_data,
        user_id=current_user.id
    )

@router.get("/{workflow_id}", response_model=WorkflowDefinition)
async def get_workflow(
    workflow_id: str,
    current_user = Depends(get_current_user)
):
    """Get a specific workflow"""
    workflow = await workflow_service.get_workflow(
        workflow_id=workflow_id,
        user_id=current_user.id
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowDefinition)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdateRequest,
    current_user = Depends(get_current_user)
):
    """Update a workflow"""
    return await workflow_service.update_workflow(
        workflow_id=workflow_id,
        workflow_data=workflow_data,
        user_id=current_user.id
    )

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a workflow"""
    await workflow_service.delete_workflow(
        workflow_id=workflow_id,
        user_id=current_user.id
    )
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    trigger_data: dict = {},
    current_user = Depends(get_current_user)
):
    """Execute a workflow"""
    return await workflow_service.execute_workflow(
        workflow_id=workflow_id,
        trigger_data=trigger_data,
        user_id=current_user.id
    )
```

### 6.2 WebSocket API

```python
# app/api/v1/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_execution_update(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

## 7. Development Setup

### 7.1 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - MONGODB_URL=mongodb://mongo:27017/workflow_generator
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mongo_data:
```

### 7.2 Environment Configuration

```python
# backend/app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Workflow Generator"
    DEBUG: bool = False
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017/workflow_generator"
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI/LLM
    OPENAI_API_KEY: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 8. Deployment Strategy

### 8.1 Production Architecture

```
Internet
    │
    ▼
┌─────────────────┐
│   Load Balancer │  (Nginx/Cloudflare)
│   (SSL/HTTPS)   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Frontend      │  (React Build)
│   (Static Files)│  (Nginx/CDN)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   API Gateway   │  (FastAPI)
│   (Multiple     │  (Load Balanced)
│   Instances)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Database      │  (MongoDB)
│   (Replica Set) │  (3 nodes)
└─────────────────┘
```

### 8.2 Scaling Considerations

1. **Horizontal Scaling**
   - Multiple FastAPI instances behind load balancer
   - Stateless application design
   - Session data in Redis/Database

2. **Database Scaling**
   - MongoDB replica sets for read scaling
   - Sharding for large datasets
   - Proper indexing strategy

3. **Caching Strategy**
   - Redis for session storage
   - CDN for static assets
   - Application-level caching for frequent queries

4. **Background Processing**
   - Celery workers for long-running workflows
   - Queue-based execution for scalability
   - Monitoring and retry mechanisms

## 9. Security Considerations

### 9.1 Authentication & Authorization

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

### 9.2 Input Validation & Sanitization

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from app.core.security import verify_token
from app.services.user_service import user_service

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await user_service.get_user(user_id)
    if user is None:
        raise credentials_exception
    
    return user
```

## 10. Testing Strategy

### 10.1 Frontend Testing

```typescript
// frontend/src/components/workflow/__tests__/WorkflowEditor.test.tsx
import { render, screen } from '@testing-library/react';
import { WorkflowEditor } from '../WorkflowEditor';

describe('WorkflowEditor', () => {
  test('renders workflow editor with basic elements', () => {
    render(<WorkflowEditor />);
    
    expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument();
    expect(screen.getByTestId('node-palette')).toBeInTheDocument();
    expect(screen.getByTestId('minimap')).toBeInTheDocument();
  });

  test('adds node when dropped on canvas', async () => {
    render(<WorkflowEditor />);
    
    // Simulate drag and drop
    const triggerNode = screen.getByTestId('node-trigger');
    const canvas = screen.getByTestId('workflow-canvas');
    
    // Test drag and drop interaction
    // Implementation depends on testing library capabilities
  });
});
```

### 10.2 Backend Testing

```python
# backend/tests/test_workflow_service.py
import pytest
from app.services.workflow_service import workflow_service
from app.models.workflow import WorkflowCreateRequest

@pytest.mark.asyncio
async def test_create_workflow():
    # Test workflow creation
    workflow_data = WorkflowCreateRequest(
        name="Test Workflow",
        description="A test workflow",
        nodes=[{
            "id": "test-node",
            "type": "trigger",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Test Trigger"}
        }],
        edges=[]
    )
    
    result = await workflow_service.create_workflow(
        workflow_data=workflow_data,
        user_id="test-user"
    )
    
    assert result.name == "Test Workflow"
    assert len(result.nodes) == 1
    assert result.nodes[0].type == "trigger"

@pytest.mark.asyncio 
async def test_execute_simple_workflow():
    # Test workflow execution
    # Implementation of execution test
    pass
```

## 11. Monitoring & Observability

### 11.1 Logging Strategy

```python
# app/core/logging.py
import logging
import structlog
from app.core.config import settings

def configure_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

### 11.2 Metrics & Health Checks

```python
# app/api/v1/health.py
from fastapi import APIRouter
from app.core.database import get_database

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check including dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "checks": {}
    }
    
    # Check database connectivity
    try:
        db = await get_database()
        await db.command("ping")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity
    try:
        # Redis health check implementation
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {e}"
    
    return health_status
```

---

**Document Version**: 1.0  
**Last Updated**: August 20, 2025  
**Next Review**: September 20, 2025
