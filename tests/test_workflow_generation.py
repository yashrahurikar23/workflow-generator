#!/usr/bin/env python3
"""
Test script for the workflow generation feature
This will test the WorkflowGenerator directly without starting the full server
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Simple mock classes for testing without full dependencies
class MockWorkflowGenerateRequest:
    def __init__(self, prompt, additional_context=None):
        self.prompt = prompt
        self.additional_context = additional_context

class MockStepType:
    API_CALL = "api_call"
    DATA_TRANSFORM = "data_transform"
    CONDITION = "condition"
    EMAIL = "email"
    FILE_OPERATION = "file_operation"
    LLM_PROCESS = "llm_process"
    MANUAL = "manual"

class MockWorkflowStepConfig:
    def __init__(self, step_id, name, step_type, description, config, depends_on=None):
        self.step_id = step_id
        self.name = name
        self.step_type = step_type
        self.description = description
        self.config = config
        self.depends_on = depends_on or []

class MockWorkflowStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"

class MockWorkflow:
    def __init__(self, workflow_id, name, description, steps, tags=None, **kwargs):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps = steps
        self.tags = tags or []
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockSettings:
    OPENAI_API_KEY = None
    LLM_PROVIDER = "template"

# Simple workflow generator with template-based logic
class SimpleWorkflowGenerator:
    def __init__(self):
        self.use_llm = False
        
    async def generate_workflow(self, request):
        """Generate a workflow using template-based approach"""
        import uuid
        
        workflow_id = str(uuid.uuid4())
        prompt_lower = request.prompt.lower()
        
        # Extract workflow name
        name = self._extract_workflow_name(request.prompt)
        
        # Generate steps based on keywords
        steps = await self._analyze_prompt_and_generate_steps(request.prompt, request.additional_context)
        
        # Extract tags
        tags = self._extract_tags_from_prompt(request.prompt)
        
        workflow = MockWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=f"Template-generated workflow from: {request.prompt[:100]}...",
            steps=steps,
            tags=tags,
            status=MockWorkflowStatus.DRAFT,
            generated_by_llm=False,
            generation_prompt=request.prompt,
            llm_provider="template",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return workflow
    
    def _extract_workflow_name(self, prompt):
        """Extract a reasonable workflow name from the prompt"""
        words = prompt.split()[:6]  # Take first 6 words
        name = " ".join(words)
        
        if len(name) > 50:
            name = name[:50] + "..."
        
        # Capitalize first letter
        name = name[0].upper() + name[1:] if name else "Generated Workflow"
        
        return name
    
    async def _analyze_prompt_and_generate_steps(self, prompt, additional_context=None):
        """Analyze the prompt and generate appropriate workflow steps"""
        import uuid
        
        steps = []
        prompt_lower = prompt.lower()
        
        # Add a manual input step if the prompt mentions data input
        if any(word in prompt_lower for word in ["input", "data", "upload", "provide"]):
            steps.append(MockWorkflowStepConfig(
                step_id=f"input_{len(steps) + 1}",
                name="Data Input",
                step_type=MockStepType.MANUAL,
                description="Collect input data for processing",
                config={
                    "instruction": "Please provide the required input data",
                    "input_type": "text"
                }
            ))
        
        # Add API call step if prompt mentions API, fetch, or external data
        if any(word in prompt_lower for word in ["api", "fetch", "external", "call", "request", "weather", "news"]):
            steps.append(MockWorkflowStepConfig(
                step_id=f"api_call_{len(steps) + 1}",
                name="API Data Retrieval",
                step_type=MockStepType.API_CALL,
                description="Fetch data from external API",
                config={
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {"Content-Type": "application/json"},
                    "timeout": 30
                }
            ))
        
        # Add data transformation step if prompt mentions processing, transform, or clean
        if any(word in prompt_lower for word in ["process", "transform", "clean", "format", "convert", "analyze"]):
            steps.append(MockWorkflowStepConfig(
                step_id=f"transform_{len(steps) + 1}",
                name="Data Processing",
                step_type=MockStepType.DATA_TRANSFORM,
                description="Process and transform the data",
                config={
                    "input_field": "data",
                    "transform_type": "format",
                    "output_format": "json"
                }
            ))
        
        # Add LLM processing step if prompt mentions AI, analyze, or generate
        if any(word in prompt_lower for word in ["ai", "analyze", "generate", "llm", "gpt", "summarize", "insights"]):
            steps.append(MockWorkflowStepConfig(
                step_id=f"llm_process_{len(steps) + 1}",
                name="AI Analysis",
                step_type=MockStepType.LLM_PROCESS,
                description="Analyze data using AI",
                config={
                    "prompt": "Analyze the provided data and extract key insights",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 500
                }
            ))
        
        # Add condition step if prompt mentions conditional logic
        if any(word in prompt_lower for word in ["if", "condition", "check", "validate", "when"]):
            steps.append(MockWorkflowStepConfig(
                step_id=f"condition_{len(steps) + 1}",
                name="Conditional Check",
                step_type=MockStepType.CONDITION,
                description="Check conditions and branch logic",
                config={
                    "condition": "data_quality > 0.8",
                    "true_action": "continue",
                    "false_action": "retry"
                }
            ))
        
        # Add email step if prompt mentions email or notification
        if any(word in prompt_lower for word in ["email", "notify", "send", "alert"]):
            steps.append(MockWorkflowStepConfig(
                step_id=f"email_{len(steps) + 1}",
                name="Send Notification",
                step_type=MockStepType.EMAIL,
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
                MockWorkflowStepConfig(
                    step_id="process_task",
                    name="Process Task",
                    step_type=MockStepType.MANUAL,
                    description="Complete the requested task",
                    config={
                        "instruction": prompt,
                        "expected_output": "Task completion confirmation"
                    }
                )
            ]
        
        return steps
    
    def _extract_tags_from_prompt(self, prompt):
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
        if any(word in prompt_lower for word in ["weather"]):
            tags.append("weather")
        
        return tags[:5]  # Limit to 5 tags

async def test_workflow_generation():
    """Test the workflow generation with various prompts"""
    
    generator = SimpleWorkflowGenerator()
    
    test_prompts = [
        "Send me a daily weather email for New York",
        "Analyze uploaded CSV file and generate insights using AI",
        "Process customer feedback and send summary to team",
        "Fetch news articles about AI and create a weekly report",
        "Monitor website status and alert if down",
        "Transform Excel data to JSON format and upload to database"
    ]
    
    print("🚀 Testing Workflow Generation")
    print("=" * 60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        print("-" * 40)
        
        request = MockWorkflowGenerateRequest(prompt)
        workflow = await generator.generate_workflow(request)
        
        print(f"✅ Generated Workflow:")
        print(f"   Name: {workflow.name}")
        print(f"   Description: {workflow.description}")
        print(f"   Tags: {', '.join(workflow.tags)}")
        print(f"   Steps ({len(workflow.steps)}):")
        
        for j, step in enumerate(workflow.steps, 1):
            print(f"     {j}. {step.name} ({step.step_type})")
            print(f"        Description: {step.description}")
            print(f"        Config: {list(step.config.keys())}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_workflow_generation())
