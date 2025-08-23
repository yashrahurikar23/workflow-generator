# 📚 API Documentation - Workflow Generator

## 🎯 Current API Endpoints (v1)

### Base URL
```
http://localhost:8003/api/v1
```

### Authentication
Currently **no authentication required** - all workflows are public.

---

## 📋 Workflow Management

### 1. List Workflows
```http
GET /workflows
```

**Query Parameters:**
- `skip` (int): Number of workflows to skip (default: 0)
- `limit` (int): Number of workflows to return (1-100, default: 50)
- `status` (enum): Filter by status - `draft`, `active`, `inactive`
- `tags` (string): Comma-separated tags to filter by
- `search` (string): Search in workflow name and description

**Response:**
```json
{
  "workflows": [
    {
      "workflow_id": "uuid",
      "name": "Daily Weather Email",
      "description": "Sends daily weather updates via email",
      "steps": [...],
      "tags": ["weather", "email", "daily"],
      "status": "active",
      "created_at": "2024-12-22T10:00:00Z",
      "generated_by_llm": true,
      "llm_provider": "openai"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 10
}
```

### 2. Create Workflow
```http
POST /workflows
```

**Request Body:**
```json
{
  "name": "My Custom Workflow",
  "description": "Description of what this workflow does",
  "steps": [
    {
      "step_id": "step1",
      "name": "API Call",
      "step_type": "api_call",
      "description": "Fetch data from external API",
      "config": {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {"Authorization": "Bearer token"}
      },
      "depends_on": []
    }
  ],
  "tags": ["api", "data"],
  "parallel_execution": false,
  "timeout_minutes": 30
}
```

**Response:** `201 Created`
```json
{
  "workflow_id": "uuid",
  "name": "My Custom Workflow",
  // ... full workflow object
}
```

### 3. Get Workflow
```http
GET /workflows/{workflow_id}
```

**Response:**
```json
{
  "workflow_id": "uuid",
  "name": "Daily Weather Email",
  "description": "Sends daily weather updates via email",
  "steps": [...],
  "tags": ["weather", "email"],
  "status": "active",
  "created_at": "2024-12-22T10:00:00Z",
  "updated_at": "2024-12-22T10:00:00Z"
}
```

### 4. Update Workflow
```http
PUT /workflows/{workflow_id}
```

**Request Body:** Same as create workflow

**Response:**
```json
{
  "workflow_id": "uuid",
  // ... updated workflow object
}
```

### 5. Delete Workflow
```http
DELETE /workflows/{workflow_id}
```

**Response:** `204 No Content`

---

## 🤖 AI-Powered Workflow Generation

### 6. Generate Workflow from Natural Language
```http
POST /workflows/generate
```

**Request Body:**
```json
{
  "prompt": "Send me a daily weather email for New York with a summary",
  "additional_context": "Email: john@example.com, prefer morning delivery"
}
```

**Response:** `201 Created`
```json
{
  "workflow_id": "uuid",
  "name": "Daily Weather Email for New York",
  "description": "AI-generated workflow that fetches weather data for New York and sends daily email summaries",
  "steps": [
    {
      "step_id": "fetch_weather",
      "name": "Get Weather Data",
      "step_type": "api_call",
      "description": "Fetch weather information from API",
      "config": {
        "url": "https://api.openweathermap.org/data/2.5/weather",
        "method": "GET",
        "params": {"q": "New York", "appid": "YOUR_API_KEY"}
      },
      "depends_on": []
    },
    {
      "step_id": "format_weather",
      "name": "Format Weather Report",
      "step_type": "data_transform",
      "description": "Format weather data into readable summary",
      "config": {
        "template": "Today's weather in New York: {{temp}}°F, {{description}}"
      },
      "depends_on": ["fetch_weather"]
    },
    {
      "step_id": "send_email",
      "name": "Send Weather Email",
      "step_type": "email",
      "description": "Send formatted weather report via email",
      "config": {
        "to": "john@example.com",
        "subject": "Daily Weather Report - New York",
        "body": "{{formatted_weather}}"
      },
      "depends_on": ["format_weather"]
    }
  ],
  "tags": ["weather", "email", "daily", "ai-generated"],
  "status": "draft",
  "generated_by_llm": true,
  "generation_prompt": "Send me a daily weather email for New York with a summary",
  "llm_provider": "openai"
}
```

---

## ⚡ Workflow Execution

### 7. Execute Workflow
```http
POST /workflows/{workflow_id}/execute
```

**Request Body:**
```json
{
  "input_data": {
    "user_email": "john@example.com",
    "location": "New York"
  }
}
```

**Response:** `201 Created`
```json
{
  "execution_id": "uuid",
  "workflow_id": "uuid",
  "status": "running",
  "input_data": {...},
  "started_at": "2024-12-22T10:00:00Z",
  "current_step": "fetch_weather"
}
```

### 8. List Workflow Executions
```http
GET /workflows/{workflow_id}/executions
```

**Query Parameters:**
- `skip` (int): Number to skip (default: 0)
- `limit` (int): Number to return (default: 50)

**Response:**
```json
{
  "executions": [
    {
      "execution_id": "uuid",
      "workflow_id": "uuid",
      "status": "completed",
      "started_at": "2024-12-22T10:00:00Z",
      "completed_at": "2024-12-22T10:01:30Z",
      "duration_seconds": 90
    }
  ],
  "total": 15,
  "page": 1,
  "size": 10
}
```

### 9. Get Execution Details
```http
GET /executions/{execution_id}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "workflow_id": "uuid",
  "status": "completed",
  "input_data": {...},
  "output_data": {...},
  "started_at": "2024-12-22T10:00:00Z",
  "completed_at": "2024-12-22T10:01:30Z",
  "step_executions": [
    {
      "step_id": "fetch_weather",
      "status": "completed",
      "started_at": "2024-12-22T10:00:00Z",
      "completed_at": "2024-12-22T10:00:30Z",
      "output_data": {"temp": "72°F", "description": "Sunny"}
    }
  ]
}
```

---

## 📊 Supported Step Types

### 1. API Call (`api_call`)
```json
{
  "step_type": "api_call",
  "config": {
    "url": "https://api.example.com/endpoint",
    "method": "GET|POST|PUT|DELETE",
    "headers": {"Authorization": "Bearer token"},
    "params": {"key": "value"},
    "body": {"data": "value"},
    "timeout": 30
  }
}
```

### 2. Data Transform (`data_transform`)
```json
{
  "step_type": "data_transform",
  "config": {
    "input_field": "api_response",
    "transform_type": "template|filter|map|aggregate",
    "template": "Result: {{data.value}}",
    "filter_condition": "value > 10",
    "output_format": "json|csv|xml"
  }
}
```

### 3. Condition (`condition`)
```json
{
  "step_type": "condition",
  "config": {
    "condition": "temperature > 75",
    "true_action": "continue",
    "false_action": "stop|retry|skip",
    "retry_count": 3
  }
}
```

### 4. Email (`email`)
```json
{
  "step_type": "email",
  "config": {
    "to": "user@example.com",
    "cc": ["manager@example.com"],
    "subject": "Workflow Notification",
    "body": "{{message_content}}",
    "template": "notification_template",
    "attachments": ["file_path"]
  }
}
```

### 5. File Operation (`file_operation`)
```json
{
  "step_type": "file_operation",
  "config": {
    "operation": "upload|download|convert|process",
    "source_path": "/path/to/file",
    "destination_path": "/path/to/output",
    "format": "csv|json|xml|pdf",
    "options": {"delimiter": ",", "encoding": "utf-8"}
  }
}
```

### 6. LLM Process (`llm_process`)
```json
{
  "step_type": "llm_process",
  "config": {
    "prompt": "Analyze this data and provide insights: {{input_data}}",
    "model": "gpt-4o|claude-3|llama-3",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "You are a data analyst"
  }
}
```

### 7. Manual (`manual`)
```json
{
  "step_type": "manual",
  "config": {
    "instruction": "Please review and approve the data",
    "input_type": "text|file|approval",
    "validation": "required|email|number",
    "timeout_minutes": 60
  }
}
```

---

## 🔮 Planned API Endpoints (Future)

### Workflow Templates
```http
GET /templates                    # List pre-built templates
POST /templates                   # Create template from workflow
GET /templates/{id}              # Get template details
POST /templates/{id}/instantiate # Create workflow from template
```

### Workflow Scheduling
```http
POST /workflows/{id}/schedule    # Schedule workflow execution
GET /workflows/{id}/schedules    # List schedules
PUT /schedules/{id}              # Update schedule
DELETE /schedules/{id}           # Cancel schedule
```

### Webhook Integration
```http
POST /workflows/{id}/webhooks    # Create webhook trigger
GET /workflows/{id}/webhooks     # List webhooks
POST /webhooks/{id}/test         # Test webhook
```

### Analytics & Monitoring
```http
GET /workflows/{id}/analytics    # Workflow performance metrics
GET /executions/stats            # Execution statistics
GET /health                      # System health check
```

### Workflow Sharing & Collaboration
```http
POST /workflows/{id}/share       # Generate shareable link
GET /workflows/shared/{token}    # Access shared workflow
POST /workflows/{id}/fork        # Create copy of workflow
```

---

## 🤖 AIML API Integration

### Overview
**AIML API** (https://aimlapi.com) is an OpenAI-compatible API provider that offers access to 200+ AI models including:
- **Text Models**: GPT-4o, Claude, Llama, DeepSeek, Gemini
- **Image Models**: FLUX, Stable Diffusion, DALL-E
- **Video Models**: Sora, Runway, Luma
- **Voice Models**: ElevenLabs, OpenAI TTS

### Key Benefits for Our Project
1. **OpenAI-Compatible**: Drop-in replacement for OpenAI API
2. **200+ Models**: Access to latest AI models
3. **Cost-Effective**: Competitive pricing vs OpenAI
4. **LlamaIndex Compatible**: Works with existing LlamaIndex setup

### Integration Setup

#### 1. Basic AIML API Configuration
```python
from openai import OpenAI

# AIML API configuration
base_url = "https://api.aimlapi.com/v1"
api_key = "YOUR_AIML_API_KEY"  # From https://aimlapi.com/app/keys

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)
```

#### 2. LlamaIndex Integration
```python
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# Configure LlamaIndex to use AIML API
llm = OpenAI(
    model="gpt-4o",  # or any AIML-supported model
    api_key="YOUR_AIML_API_KEY",
    api_base="https://api.aimlapi.com/v1",
    temperature=0.1
)

Settings.llm = llm
```

#### 3. Enhanced Workflow Generator with AIML
```python
class WorkflowGenerator:
    def __init__(self):
        self.aiml_api_key = settings.AIML_API_KEY
        self.use_aiml = bool(self.aiml_api_key)
        
        if self.use_aiml:
            self.llm = OpenAI(
                model="gpt-4o",  # Latest GPT-4 via AIML
                api_key=self.aiml_api_key,
                api_base="https://api.aimlapi.com/v1",
                temperature=0.1
            )
            Settings.llm = self.llm
    
    async def generate_workflow_with_aiml(self, prompt: str):
        """Generate workflow using AIML API's latest models"""
        # Use structured output with latest models
        # Access to GPT-4o, Claude-3, Llama-3, etc.
```

### Available Models for Workflow Generation
```python
AIML_MODELS = {
    "gpt-4o": "Latest GPT-4 Omni - Best for complex reasoning",
    "gpt-4o-mini": "Faster, cost-effective GPT-4",
    "claude-3-sonnet": "Anthropic's Claude - Great for structured output",
    "llama-3-70b": "Meta's Llama 3 - Open source alternative",
    "deepseek-v3": "DeepSeek V3 - Excellent for code generation",
    "gemini-1.5-pro": "Google's Gemini - Multimodal capabilities"
}
```

### Configuration Updates Needed

#### backend/app/core/config.py
```python
class Settings(BaseSettings):
    # Existing settings...
    
    # AIML API Integration
    AIML_API_KEY: Optional[str] = None
    AIML_BASE_URL: str = "https://api.aimlapi.com/v1"
    AIML_MODEL: str = "gpt-4o"  # Default model
    
    # LLM Provider Selection
    LLM_PROVIDER: str = "aiml"  # aiml, openai, anthropic, local
```

### Benefits Over OpenAI Direct
1. **Cost**: Up to 90% cheaper than OpenAI direct
2. **Models**: Access to 200+ models beyond just OpenAI
3. **Reliability**: Multiple fallback models
4. **Features**: Latest models often available sooner

### Implementation Priority
- **Phase 1**: Add AIML as LLM provider option
- **Phase 2**: Multi-model workflow generation (try multiple models)
- **Phase 3**: Model-specific optimizations (e.g., Claude for structured output, Llama for open-source)

---

## 🔧 Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "WORKFLOW_NOT_FOUND",
  "timestamp": "2024-12-22T10:00:00Z"
}
```

**Common HTTP Status Codes:**
- `400` - Bad Request (invalid input)
- `404` - Not Found (workflow/execution doesn't exist)
- `422` - Validation Error (invalid data format)
- `500` - Internal Server Error (system error)

---

**Next Steps:**
1. ✅ Document current APIs (DONE)
2. 🔄 Add AIML API integration
3. ⏳ Implement frontend API client
4. ⏳ Add advanced workflow features (templates, scheduling)

---
*Last Updated: December 22, 2024*
