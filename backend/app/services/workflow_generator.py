import json
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.models.workflow import (StepType, Workflow, WorkflowGenerateRequest,
                                 WorkflowStatus, WorkflowStepConfig)
from pydantic import BaseModel, Field

# LlamaIndex imports (will be optional for now)
try:
    from llama_index.core import Settings
    from llama_index.core.llms import ChatMessage
    from llama_index.core.output_parsers import PydanticOutputParser
    from llama_index.core.program import LLMTextCompletionProgram
    from llama_index.llms.openai import OpenAI
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False

# Structured output models for workflow generation
class GeneratedWorkflowStep(BaseModel):
    """Structured output model for a workflow step"""
    step_id: str = Field(description="Unique identifier for the step (lowercase_underscore)")
    name: str = Field(description="Human-readable name for the step")
    step_type: str = Field(description="Type of step: api_call, data_transform, condition, email, file_operation, llm_process, manual")
    description: str = Field(description="Detailed description of what this step does")
    config: Dict[str, Any] = Field(description="Configuration parameters specific to the step type")
    depends_on: List[str] = Field(default=[], description="List of step_ids this step depends on")

class GeneratedWorkflow(BaseModel):
    """Structured output model for the entire workflow"""
    name: str = Field(description="Concise workflow name (max 60 characters)")
    description: str = Field(description="Detailed description of what the workflow accomplishes")
    steps: List[GeneratedWorkflowStep] = Field(description="Ordered list of workflow steps")
    tags: List[str] = Field(default=[], description="Relevant tags for categorization")
    estimated_duration_minutes: int = Field(default=5, description="Estimated execution time in minutes")

class WorkflowGenerator:
    """Service for generating workflows using LLM and LlamaIndex"""
    
    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LlamaIndex LLM based on configured provider"""
        self.use_llm = False
        
        if not LLAMAINDEX_AVAILABLE:
            print("LlamaIndex not available, using template-based generation")
            return
        
        try:
            if self.llm_provider == "openai" and settings.OPENAI_API_KEY:
                self.llm = OpenAI(
                    model=settings.OPENAI_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    api_base=settings.OPENAI_BASE_URL,
                    temperature=0.1
                )
                self.use_llm = True
                print(f"Initialized OpenAI LLM with model: {settings.OPENAI_MODEL}")
                
            elif self.llm_provider == "aiml" and settings.AIML_API_KEY:
                # AIML API is OpenAI-compatible, so we use OpenAI class with custom base URL
                self.llm = OpenAI(
                    model=settings.AIML_MODEL,
                    api_key=settings.AIML_API_KEY,
                    api_base=settings.AIML_BASE_URL,
                    temperature=0.1
                )
                self.use_llm = True
                print(f"Initialized AIML API with model: {settings.AIML_MODEL}")
                
            elif self.llm_provider == "anthropic" and settings.ANTHROPIC_API_KEY:
                # Note: Would need llama-index-llms-anthropic package
                print("Anthropic provider configured but not implemented yet")
                
            else:
                print(f"LLM provider '{self.llm_provider}' not configured or API key missing, using template-based generation")
                return
            
            Settings.llm = self.llm
            self._setup_structured_output_program()
            
        except Exception as e:
            print(f"Warning: Could not initialize LLM ({self.llm_provider}): {e}")
            self.use_llm = False
    
    def _setup_structured_output_program(self):
        """Setup LlamaIndex structured output program for workflow generation"""
        workflow_prompt_template = """
You are an expert workflow automation architect. Your task is to analyze a user's natural language request and create a structured, executable workflow.

{step_type_guidance}

{workflow_examples}

WORKFLOW DESIGN PRINCIPLES:
1. Break complex tasks into discrete, logical steps
2. Consider dependencies between steps (use depends_on)
3. Include validation and error handling where appropriate
4. Make configurations realistic and actionable
5. Optimize for clarity and maintainability
6. Use appropriate step types for each operation
7. Ensure step_ids are descriptive and unique

USER REQUEST: {user_request}
{additional_context}

Generate a workflow that accomplishes this request effectively and efficiently. Make the configurations realistic and specific to the user's needs.
"""

        try:
            self.workflow_program = LLMTextCompletionProgram.from_defaults(
                output_parser=PydanticOutputParser(GeneratedWorkflow),
                prompt_template_str=workflow_prompt_template,
                llm=self.llm,
                verbose=True
            )
        except Exception as e:
            print(f"Could not setup structured output program: {e}")
            self.workflow_program = None
    
    async def generate_workflow(self, request: WorkflowGenerateRequest) -> Workflow:
        """Generate a workflow from natural language description"""
        
        workflow_id = str(uuid.uuid4())
        
        if self.use_llm and self.workflow_program:
            # Use LlamaIndex structured output for intelligent workflow generation
            try:
                additional_context = f"Additional context: {request.additional_context}" if request.additional_context else ""
                
                generated_workflow = self.workflow_program(
                    user_request=request.prompt,
                    additional_context=additional_context,
                    step_type_guidance=self._get_step_type_guidance(),
                    workflow_examples=self._get_workflow_examples()
                )
                
                # Convert generated steps to our internal format
                steps = self._convert_generated_steps_to_internal(generated_workflow.steps)
                name = generated_workflow.name[:60]  # Ensure max length
                description = generated_workflow.description
                tags = generated_workflow.tags
                
            except Exception as e:
                print(f"Error with structured generation, falling back to LLM chat: {e}")
                # Fallback to chat-based generation
                steps = await self._generate_steps_with_llm(request.prompt, request.additional_context)
                name = await self._extract_name_with_llm(request.prompt)
                description = f"AI-generated workflow from: {request.prompt[:100]}..."
                tags = self._extract_tags_from_prompt(request.prompt)
        else:
            # Fallback to template-based generation
            steps = await self._analyze_prompt_and_generate_steps(request.prompt, request.additional_context)
            name = self._extract_workflow_name(request.prompt)
            description = f"Template-generated workflow from: {request.prompt[:100]}..."
            tags = self._extract_tags_from_prompt(request.prompt)
        
        # Create workflow
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=steps,
            tags=tags,
            status=WorkflowStatus.DRAFT,
            generated_by_llm=self.use_llm,
            generation_prompt=request.prompt,
            llm_provider=self.llm_provider if self.use_llm else "template",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return workflow
    
    def _convert_generated_steps_to_internal(self, generated_steps: List[GeneratedWorkflowStep]) -> List[WorkflowStepConfig]:
        """Convert generated steps to internal WorkflowStepConfig format"""
        steps = []
        for gen_step in generated_steps:
            try:
                step_type = StepType(gen_step.step_type.lower())
            except ValueError:
                # If step_type is not recognized, default to manual
                step_type = StepType.MANUAL
            
            step = WorkflowStepConfig(
                step_id=gen_step.step_id,
                name=gen_step.name,
                step_type=step_type,
                description=gen_step.description,
                config=gen_step.config,
                depends_on=gen_step.depends_on
            )
            steps.append(step)
        
        return steps
    
    def _extract_tags_from_prompt(self, prompt: str) -> List[str]:
        """Extract relevant tags from the prompt"""
        tags = []
        prompt_lower = prompt.lower()
        
        # Domain-based tags
        if any(word in prompt_lower for word in ["email", "notification", "alert"]):
            tags.append("communication")
        if any(word in prompt_lower for word in ["api", "external", "service"]):
            tags.append("integration")
        if any(word in prompt_lower for word in ["data", "process", "transform"]):
            tags.append("data-processing")
        if any(word in prompt_lower for word in ["ai", "llm", "analyze", "generate"]):
            tags.append("ai-powered")
        if any(word in prompt_lower for word in ["file", "upload", "download"]):
            tags.append("file-handling")
        if any(word in prompt_lower for word in ["schedule", "daily", "weekly", "recurring"]):
            tags.append("scheduled")
        if any(word in prompt_lower for word in ["report", "summary", "document"]):
            tags.append("reporting")
        
        return tags[:5]  # Limit to 5 tags
    
    async def _generate_steps_with_llm(self, prompt: str, additional_context: Optional[str] = None) -> List[WorkflowStepConfig]:
        """Generate workflow steps using LlamaIndex LLM"""
        
        system_prompt = """You are a workflow automation expert. Given a user's natural language description, create a structured workflow.

Available step types:
- api_call: HTTP requests to external services
- data_transform: Data manipulation and formatting  
- condition: Conditional logic and branching
- email: Send emails and notifications
- file_operation: File upload, download, processing
- llm_process: AI processing tasks

For each step, provide:
1. step_id: unique identifier (lowercase, underscore)
2. name: human-readable name
3. step_type: one of the available types
4. description: what this step does
5. config: step-specific configuration parameters
6. depends_on: array of step_ids this step depends on

Return ONLY a JSON array of steps, no additional text."""

        user_prompt = f"""Create workflow steps for: "{prompt}"

{f"Additional context: {additional_context}" if additional_context else ""}

Return as JSON array of step objects."""

        try:
            # Create chat messages
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt)
            ]
            
            # Get response from LLM
            response = await self.llm.achat(messages)
            response_text = response.message.content
            
            # Parse JSON response
            steps_data = json.loads(response_text)
            
            # Convert to WorkflowStepConfig objects
            steps = []
            for step_data in steps_data:
                step = WorkflowStepConfig(
                    step_id=step_data.get("step_id", f"step_{len(steps) + 1}"),
                    name=step_data.get("name", "Unnamed Step"),
                    step_type=StepType(step_data.get("step_type", "api_call")),
                    description=step_data.get("description"),
                    config=step_data.get("config", {}),
                    depends_on=step_data.get("depends_on", [])
                )
                steps.append(step)
            
            return steps
            
        except Exception as e:
            print(f"Error generating steps with LLM: {e}")
            # Fallback to template-based generation
            return await self._analyze_prompt_and_generate_steps(prompt, additional_context)
    
    async def _extract_name_with_llm(self, prompt: str) -> str:
        """Extract a workflow name using LLM"""
        
        name_prompt = f"""Given this workflow description, create a short, descriptive name (max 50 characters):

"{prompt}"

Return ONLY the name, no additional text."""

        try:
            messages = [ChatMessage(role="user", content=name_prompt)]
            response = await self.llm.achat(messages)
            name = response.message.content.strip().strip('"')
            return name[:50]  # Ensure max length
            
        except Exception as e:
            print(f"Error extracting name with LLM: {e}")
            return self._extract_workflow_name(prompt)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=f"Generated from prompt: {request.prompt[:200]}...",
            steps=steps,
            status=WorkflowStatus.DRAFT,
            generated_by_llm=True,
            generation_prompt=request.prompt,
            llm_provider=self.llm_provider,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return workflow
    
    async def _analyze_prompt_and_generate_steps(
        self, 
        prompt: str, 
        additional_context: Optional[str] = None
    ) -> List[WorkflowStepConfig]:
        """Analyze the prompt and generate appropriate workflow steps"""
        
        # Simple keyword-based step generation
        # In a real implementation, this would use a sophisticated LLM
        
        steps = []
        prompt_lower = prompt.lower()
        
        # Add a manual input step if the prompt mentions data input
        if any(word in prompt_lower for word in ["input", "data", "upload", "provide"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Data Input",
                step_type=StepType.MANUAL,
                description="Collect input data for processing",
                config={
                    "instruction": "Please provide the required input data",
                    "input_type": "text"
                }
            ))
        
        # Add API call step if prompt mentions API, fetch, or external data
        if any(word in prompt_lower for word in ["api", "fetch", "external", "call", "request"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="API Data Retrieval",
                step_type=StepType.API_CALL,
                description="Fetch data from external API",
                config={
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {},
                    "timeout": 30
                }
            ))
        
        # Add data transformation step if prompt mentions processing, transform, or clean
        if any(word in prompt_lower for word in ["process", "transform", "clean", "format", "convert"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Data Processing",
                step_type=StepType.DATA_TRANSFORM,
                description="Process and transform the data",
                config={
                    "input_field": "data",
                    "transform_type": "format",
                    "output_format": "json"
                }
            ))
        
        # Add LLM processing step if prompt mentions AI, analyze, or generate
        if any(word in prompt_lower for word in ["ai", "analyze", "generate", "llm", "gpt", "summarize"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="AI Analysis",
                step_type=StepType.LLM_PROCESS,
                description="Analyze data using AI",
                config={
                    "prompt": "Analyze the provided data and extract key insights",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 500
                }
            ))
        
        # Add condition step if prompt mentions conditional logic
        if any(word in prompt_lower for word in ["if", "condition", "check", "validate", "when"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Conditional Check",
                step_type=StepType.CONDITION,
                description="Check conditions and branch logic",
                config={
                    "condition": "data_quality > 0.8",
                    "true_action": "continue",
                    "false_action": "retry"
                }
            ))
        
        # Add email step if prompt mentions email or notification
        if any(word in prompt_lower for word in ["email", "notify", "send", "alert"]):
            steps.append(WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Send Notification",
                step_type=StepType.EMAIL,
                description="Send email notification with results",
                config={
                    "to": "user@example.com",
                    "subject": "Workflow Completed",
                    "template": "workflow_completion"
                }
            ))
        
        # If no specific steps were detected, create a generic workflow
        if not steps:
            steps = [
                WorkflowStepConfig(
                    step_id=str(uuid.uuid4()),
                    name="Process Task",
                    step_type=StepType.MANUAL,
                    description="Complete the requested task",
                    config={
                        "instruction": prompt,
                        "expected_output": "Task completion confirmation"
                    }
                )
            ]
        
        return steps
    
    def _extract_workflow_name(self, prompt: str) -> str:
        """Extract a reasonable workflow name from the prompt"""
        # Simple heuristic to create a name
        words = prompt.split()[:6]  # Take first 6 words
        name = " ".join(words)
        
        # Clean up the name
        if len(name) > 50:
            name = name[:50] + "..."
        
        # Capitalize first letter
        name = name[0].upper() + name[1:] if name else "Generated Workflow"
        
        return name
    
    async def enhance_workflow_with_llm(self, workflow: Workflow, enhancement_request: str) -> Workflow:
        """Enhance an existing workflow using LLM suggestions"""
        # This would use LLM to suggest improvements to the workflow
        # For now, we'll just add a simple enhancement
        
        if "optimization" in enhancement_request.lower():
            # Add a performance optimization step
            optimization_step = WorkflowStepConfig(
                step_id=str(uuid.uuid4()),
                name="Performance Optimization",
                step_type=StepType.DATA_TRANSFORM,
                description="Optimize workflow performance",
                config={
                    "optimization_type": "parallel_processing",
                    "cache_enabled": True
                }
            )
            workflow.steps.append(optimization_step)
        
        workflow.updated_at = datetime.utcnow()
        return workflow
    
    async def generate_step_parameters(self, step_type: StepType, context: str) -> Dict[str, Any]:
        """Generate parameters for a specific step type using LLM"""
        # This would use LLM to generate appropriate parameters for a step
        
        base_configs = {
            StepType.API_CALL: {
                "url": "https://api.example.com",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 30
            },
            StepType.DATA_TRANSFORM: {
                "input_field": "data",
                "transform_type": "format",
                "output_format": "json"
            },
            StepType.CONDITION: {
                "condition": "true",
                "true_action": "continue",
                "false_action": "stop"
            },
            StepType.LLM_PROCESS: {
                "prompt": "Process the data",
                "model": "gpt-3.5-turbo",
                "max_tokens": 500
            },
            StepType.EMAIL: {
                "to": "user@example.com",
                "subject": "Workflow Update",
                "template": "default"
            }
        }
        
        return base_configs.get(step_type, {})
    
    def _get_workflow_examples(self) -> str:
        """Get example workflows to help the LLM understand the expected format"""
        return """
EXAMPLE WORKFLOWS:

Example 1 - "Send me a daily weather email"
{
  "name": "Daily Weather Email",
  "description": "Fetches weather data and sends daily email summary",
  "steps": [
    {
      "step_id": "fetch_weather",
      "name": "Get Weather Data",
      "step_type": "api_call",
      "description": "Fetch weather information from API",
      "config": {
        "url": "https://api.openweathermap.org/data/2.5/weather",
        "method": "GET",
        "params": {"q": "San Francisco", "appid": "YOUR_API_KEY"},
        "timeout": 30
      },
      "depends_on": []
    },
    {
      "step_id": "format_weather",
      "name": "Format Weather Report",
      "step_type": "data_transform",
      "description": "Format weather data into readable format",
      "config": {
        "input_field": "weather_data",
        "transform_type": "template",
        "template": "Today's weather: {{temp}}°F, {{description}}, Humidity: {{humidity}}%"
      },
      "depends_on": ["fetch_weather"]
    },
    {
      "step_id": "send_email",
      "name": "Send Weather Email",
      "step_type": "email",
      "description": "Send formatted weather report via email",
      "config": {
        "to": "user@example.com",
        "subject": "Daily Weather Report",
        "body": "{{formatted_weather}}"
      },
      "depends_on": ["format_weather"]
    }
  ],
  "tags": ["weather", "email", "daily", "automation"],
  "estimated_duration_minutes": 2
}

Example 2 - "Analyze uploaded CSV and generate insights"
{
  "name": "CSV Data Analysis",
  "description": "Processes uploaded CSV file and generates AI-powered insights",
  "steps": [
    {
      "step_id": "validate_file",
      "name": "Validate CSV File",
      "step_type": "condition",
      "description": "Check if uploaded file is valid CSV format",
      "config": {
        "condition": "file_type == 'csv' AND file_size < 10MB",
        "true_action": "continue",
        "false_action": "stop_with_error"
      },
      "depends_on": []
    },
    {
      "step_id": "parse_csv",
      "name": "Parse CSV Data",
      "step_type": "file_operation",
      "description": "Parse CSV file and extract data",
      "config": {
        "operation": "parse",
        "format": "csv",
        "output_format": "json"
      },
      "depends_on": ["validate_file"]
    },
    {
      "step_id": "analyze_data",
      "name": "Generate Data Insights",
      "step_type": "llm_process",
      "description": "Use AI to analyze data and generate insights",
      "config": {
        "prompt": "Analyze this CSV data and provide key insights, trends, and recommendations: {{csv_data}}",
        "model": "gpt-4",
        "max_tokens": 1000
      },
      "depends_on": ["parse_csv"]
    },
    {
      "step_id": "create_report",
      "name": "Create Analysis Report",
      "step_type": "data_transform",
      "description": "Format insights into a structured report",
      "config": {
        "input_field": "insights",
        "transform_type": "report",
        "format": "html"
      },
      "depends_on": ["analyze_data"]
    }
  ],
  "tags": ["data-analysis", "csv", "ai", "reporting"],
  "estimated_duration_minutes": 5
}
"""

    def _get_step_type_guidance(self) -> str:
        """Get detailed guidance on when to use each step type"""
        return """
STEP TYPE USAGE GUIDANCE:

1. api_call: 
   - External API requests, webhooks
   - Data fetching from third-party services
   - Config: url, method, headers, params, timeout

2. data_transform:
   - Data formatting, filtering, aggregation
   - Template rendering, data mapping
   - Config: input_field, transform_type, template/rules

3. condition:
   - Branching logic, validation checks
   - Error handling, flow control
   - Config: condition, true_action, false_action

4. email:
   - Send notifications, reports, alerts
   - Config: to, subject, body/template

5. file_operation:
   - File upload/download, format conversion
   - Config: operation, format, input/output paths

6. llm_process:
   - AI analysis, content generation
   - Text summarization, classification
   - Config: prompt, model, max_tokens, temperature

7. manual:
   - User input required, approval steps
   - Config: instruction, input_type, validation
"""
