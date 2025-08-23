# AI Workflow Generation Architecture

## Overview

This document outlines how we'll implement natural language workflow generation using LlamaIndex to transform user instructions into executable automation workflows.

## Core Architecture

### 1. Natural Language Processing Pipeline

```
User Input → LlamaIndex Parser → Workflow Analyzer → Step Generator → Parameter Extractor → Workflow Builder
```

#### Components:

**LlamaIndex Parser**
- Takes natural language input
- Uses structured prompting to identify workflow intent
- Extracts key entities and actions

**Workflow Analyzer** 
- Determines workflow type and complexity
- Identifies dependencies between steps
- Suggests optimal execution order

**Step Generator**
- Maps identified actions to available step types
- Creates step configurations with default parameters
- Handles step naming and descriptions

**Parameter Extractor**
- Identifies required parameters from context
- Suggests default values where possible
- Creates parameter validation rules

**Workflow Builder**
- Assembles final workflow structure
- Validates workflow completeness
- Generates executable workflow definition

### 2. Supported Step Types

#### Core Step Types (MVP):
1. **API_CALL** - HTTP requests to external services
2. **DATA_TRANSFORM** - Data manipulation and formatting
3. **CONDITION** - Conditional logic and branching
4. **EMAIL** - Send emails and notifications
5. **FILE_OPERATION** - File upload, download, processing
6. **LLM_PROCESS** - AI processing tasks

#### Step Parameters:
- **API_CALL**: url, method, headers, body, auth
- **DATA_TRANSFORM**: input_field, transformation_type, output_field
- **CONDITION**: condition_type, field, operator, value
- **EMAIL**: recipient, subject, body, attachments
- **FILE_OPERATION**: operation_type, source, destination, format
- **LLM_PROCESS**: prompt, model, temperature, max_tokens

### 3. LlamaIndex Integration Strategy

#### Workflow Generation Prompt Template:
```
You are a workflow automation expert. Given a user's natural language description, create a structured workflow.

User Request: "{user_input}"

Analyze this request and break it down into a series of automation steps. For each step:
1. Identify the step type from: api_call, data_transform, condition, email, file_operation, llm_process
2. Determine the step name and description
3. List required parameters with suggested values
4. Identify dependencies on previous steps

Return a JSON structure with the workflow definition.
```

#### Example Processing:

**Input**: "Download a CSV file from a URL, filter rows where status is 'active', and send the results via email"

**LlamaIndex Analysis**:
```json
{
  "workflow_name": "CSV Filter and Email",
  "description": "Download CSV, filter active records, email results",
  "steps": [
    {
      "step_id": "download_csv",
      "name": "Download CSV File",
      "step_type": "api_call",
      "config": {
        "url": "[USER_TO_SPECIFY]",
        "method": "GET",
        "response_type": "csv"
      },
      "depends_on": []
    },
    {
      "step_id": "filter_data",
      "name": "Filter Active Records",
      "step_type": "data_transform",
      "config": {
        "input_field": "download_csv.response",
        "filter_column": "status",
        "filter_value": "active",
        "operation": "filter_rows"
      },
      "depends_on": ["download_csv"]
    },
    {
      "step_id": "send_email",
      "name": "Email Filtered Results",
      "step_type": "email",
      "config": {
        "recipient": "[USER_TO_SPECIFY]",
        "subject": "Filtered CSV Results",
        "body": "Please find the filtered data attached.",
        "attachment_data": "filter_data.output"
      },
      "depends_on": ["filter_data"]
    }
  ]
}
```

### 4. Implementation Plan

#### Phase 1: Basic AI Generation (Current Sprint)
1. **Create Workflow Generator Service** (`app/services/workflow_generator.py`)
2. **Add LlamaIndex Integration** with OpenAI backend
3. **Implement Prompt Templates** for different workflow types
4. **Add API Endpoint** for workflow generation (`POST /api/v1/workflows/generate`)

#### Phase 2: Enhanced Processing (Next Sprint)
1. **Add Parameter Validation** and suggestion logic
2. **Implement Step Dependencies** automatic detection
3. **Add Context Awareness** for related workflows
4. **Enhance Error Handling** and fallback generation

#### Phase 3: Advanced Features (Future)
1. **Multi-turn Conversation** for workflow refinement
2. **Template Learning** from successful workflows
3. **Auto-optimization** suggestions
4. **Integration Discovery** (suggest APIs and services)

### 5. UI Components Required

#### Workflow Generation Interface:
1. **Generation Form**
   - Large textarea for natural language input
   - Optional context fields (data sources, preferred tools)
   - Generate button with loading state

2. **Generated Workflow Review**
   - Step-by-step breakdown display
   - Editable parameters for each step
   - Preview of workflow execution flow
   - Save/Execute buttons

3. **Workflow Library**
   - List of all generated workflows
   - Search and filter capabilities
   - Quick execution from list
   - Workflow details modal

### 6. Example User Flows

#### Flow 1: Social Media Automation
**Input**: "Post to Twitter when I publish a new blog post on my website"

**Generated Steps**:
1. **Webhook Trigger** - Monitor website for new posts
2. **Data Extract** - Get post title, URL, excerpt
3. **Text Transform** - Format tweet with hashtags
4. **API Call** - Post to Twitter API

#### Flow 2: Data Processing
**Input**: "Every day, download sales data from our API, calculate totals, and email a summary to the team"

**Generated Steps**:
1. **Schedule Trigger** - Daily at 9 AM
2. **API Call** - Fetch sales data
3. **Data Transform** - Calculate totals and metrics
4. **Email** - Send formatted summary

#### Flow 3: Content Processing
**Input**: "When someone uploads an image to our shared folder, resize it to different sizes and save to cloud storage"

**Generated Steps**:
1. **File Monitor** - Watch shared folder
2. **Image Resize** - Generate multiple sizes
3. **Cloud Upload** - Save to storage service
4. **Notification** - Notify completion

### 7. Technical Considerations

#### LlamaIndex Configuration:
- **Model**: OpenAI GPT-4 for complex reasoning
- **Embedding**: For workflow similarity and suggestions
- **Memory**: Context awareness for related workflows
- **Streaming**: Real-time generation feedback

#### Error Handling:
- **Invalid Prompts**: Graceful fallback with suggestions
- **Missing Parameters**: Interactive parameter collection
- **Execution Failures**: Detailed error reporting and fixes

#### Performance:
- **Caching**: Common workflow patterns
- **Async Processing**: Non-blocking generation
- **Rate Limiting**: Protect against abuse

### 8. Success Metrics

#### Generation Quality:
- **Accuracy**: Generated workflows match user intent
- **Completeness**: All required steps and parameters included
- **Executability**: Workflows run successfully without modification

#### User Experience:
- **Time to Workflow**: From description to working automation
- **Iteration Count**: How many refinements needed
- **Success Rate**: Percentage of workflows that work as intended

This architecture provides a solid foundation for implementing AI-powered workflow generation while maintaining simplicity and extensibility.
