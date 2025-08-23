"""
Enhanced Visual Workflow Execution Engine with Real-time Status Tracking
Focused on Customer Support Email Automation
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.models.workflow_visual import NodeConnection, Workflow, WorkflowNode
from app.services.node_registry import NodeTypeRegistry
from llama_index.core.workflow import (Context, Event, StartEvent, StopEvent,
                                       Workflow, step)

logger = logging.getLogger(__name__)

class ExecutionStatus(str, Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class NodeStatus(str, Enum):
    """Node execution status enumeration"""
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ExecutionEvent(Event):
    """Event for execution status updates"""
    execution_id: str
    node_id: Optional[str] = None
    status: ExecutionStatus
    data: Dict[str, Any] = {}
    timestamp: datetime = datetime.utcnow()

class NodeExecutionEvent(Event):
    """Event for node execution results"""
    node_id: str
    result: Any
    status: NodeStatus
    execution_time: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class StepProgress:
    """Track progress of individual workflow steps"""
    def __init__(self, node_id: str, node_name: str):
        self.node_id = node_id
        self.node_name = node_name
        self.status = NodeStatus.WAITING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.execution_time: Optional[float] = None
        self.result: Any = None
        self.error: Optional[str] = None
        self.progress_percentage: int = 0
        self.logs: List[Dict[str, Any]] = []
    
    def start(self):
        """Mark step as started"""
        self.status = NodeStatus.RUNNING
        self.start_time = datetime.utcnow()
        self.log("Step started")
    
    def complete(self, result: Any = None):
        """Mark step as completed"""
        self.status = NodeStatus.COMPLETED
        self.end_time = datetime.utcnow()
        self.result = result
        self.progress_percentage = 100
        if self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
        self.log("Step completed successfully")
    
    def fail(self, error: str):
        """Mark step as failed"""
        self.status = NodeStatus.FAILED
        self.end_time = datetime.utcnow()
        self.error = error
        if self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
        self.log(f"Step failed: {error}")
    
    def log(self, message: str, level: str = "info"):
        """Add log entry"""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        })
    
    def update_progress(self, percentage: int, message: str = ""):
        """Update progress percentage"""
        self.progress_percentage = max(0, min(100, percentage))
        if message:
            self.log(f"Progress: {percentage}% - {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "progress_percentage": self.progress_percentage,
            "result": self.result,
            "error": self.error,
            "logs": self.logs[-10:]  # Keep last 10 logs
        }

class WorkflowExecutionContext:
    """Enhanced context for workflow execution with real-time tracking"""
    def __init__(self, workflow_id: str, execution_id: str, workflow_name: str = ""):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.workflow_name = workflow_name
        self.status = ExecutionStatus.PENDING
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.execution_time: Optional[float] = None
        
        # Step tracking
        self.steps: Dict[str, StepProgress] = {}
        self.current_step: Optional[str] = None
        self.completed_steps: List[str] = []
        self.failed_steps: List[str] = []
        
        # Results and logs
        self.node_results: Dict[str, Any] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self.global_data: Dict[str, Any] = {}
        
        # Progress tracking
        self.total_steps: int = 0
        self.completed_step_count: int = 0
        self.overall_progress: int = 0
        
        # Status callbacks
        self.status_callbacks: List = []
    
    def initialize_steps(self, nodes: List[WorkflowNode]):
        """Initialize step tracking for all nodes"""
        self.total_steps = len(nodes)
        for node in nodes:
            self.steps[node.node_id] = StepProgress(node.node_id, node.name)
    
    def start_execution(self):
        """Start workflow execution"""
        self.status = ExecutionStatus.RUNNING
        self.start_time = datetime.utcnow()
        self.log("Workflow execution started")
    
    def complete_execution(self):
        """Complete workflow execution"""
        self.status = ExecutionStatus.COMPLETED
        self.end_time = datetime.utcnow()
        self.execution_time = (self.end_time - self.start_time).total_seconds()
        self.overall_progress = 100
        self.log("Workflow execution completed")
    
    def fail_execution(self, error: str):
        """Fail workflow execution"""
        self.status = ExecutionStatus.FAILED
        self.end_time = datetime.utcnow()
        self.execution_time = (self.end_time - self.start_time).total_seconds()
        self.log(f"Workflow execution failed: {error}")
    
    def start_step(self, node_id: str):
        """Start a workflow step"""
        if node_id in self.steps:
            self.current_step = node_id
            self.steps[node_id].start()
            self._update_progress()
            self.log(f"Started step: {self.steps[node_id].node_name}")
    
    def complete_step(self, node_id: str, result: Any = None):
        """Complete a workflow step"""
        if node_id in self.steps:
            self.steps[node_id].complete(result)
            self.node_results[node_id] = result
            self.completed_steps.append(node_id)
            self.completed_step_count += 1
            self._update_progress()
            self.log(f"Completed step: {self.steps[node_id].node_name}")
    
    def fail_step(self, node_id: str, error: str):
        """Fail a workflow step"""
        if node_id in self.steps:
            self.steps[node_id].fail(error)
            self.failed_steps.append(node_id)
            self._update_progress()
            self.log(f"Failed step: {self.steps[node_id].node_name} - {error}")
    
    def _update_progress(self):
        """Update overall progress"""
        if self.total_steps > 0:
            self.overall_progress = int((self.completed_step_count / self.total_steps) * 100)
    
    def log(self, message: str, level: str = "info", node_id: str = None):
        """Add execution log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "node_id": node_id
        }
        self.execution_log.append(log_entry)
        
        # Also log to specific step if node_id provided
        if node_id and node_id in self.steps:
            self.steps[node_id].log(message, level)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "overall_progress": self.overall_progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": len(self.completed_steps),
            "failed_steps": len(self.failed_steps),
            "steps": {node_id: step.to_dict() for node_id, step in self.steps.items()},
            "execution_log": self.execution_log[-20:],  # Last 20 log entries
            "global_data": self.global_data
        }

class EmailAutomationWorkflow(Workflow):
    """Specialized workflow for email automation with real-time tracking"""
    
    def __init__(self, workflow: Workflow, node_registry: NodeTypeRegistry):
        super().__init__()
        self.workflow = workflow
        self.node_registry = node_registry
        self.execution_context = WorkflowExecutionContext(
            workflow_id=workflow.workflow_id,
            execution_id=str(uuid.uuid4()),
            workflow_name=workflow.name
        )
        
        # Initialize step tracking
        self.execution_context.initialize_steps(workflow.visual_data.nodes)
        
        # Build execution graph
        self.execution_graph = self._build_execution_graph()
        self.trigger_nodes = self._find_trigger_nodes()
    
    def _build_execution_graph(self) -> Dict[str, List[str]]:
        """Build execution graph from node connections"""
        graph = {}
        
        # Initialize all nodes
        for node in self.visual_workflow.visual_data.nodes:
            graph[node.node_id] = []
        
        # Add connections
        for connection in self.visual_workflow.visual_data.connections:
            source_id = connection.source_node_id
            target_id = connection.target_node_id
            
            if source_id not in graph:
                graph[source_id] = []
            graph[source_id].append(target_id)
        
        return graph
    
    def _find_trigger_nodes(self) -> List[WorkflowNode]:
        """Find trigger nodes (nodes with no incoming connections)"""
        incoming_connections = set()
        for connection in self.visual_workflow.visual_data.connections:
            incoming_connections.add(connection.target_node_id)
        
        trigger_nodes = []
        for node in self.visual_workflow.visual_data.nodes:
            if node.node_id not in incoming_connections:
                node_type = self.node_registry.get_node_type(node.node_type_id)
                if node_type and (node_type.category == "triggers" or node.node_type_id.endswith("_trigger")):
                    trigger_nodes.append(node)
        
        return trigger_nodes
    
    @step
    async def process_start(self, ctx: Context, ev: StartEvent) -> NodeExecutionEvent:
        """Process workflow start event"""
        logger.info(f"Starting email automation workflow: {self.execution_context.execution_id}")
        self.execution_context.start_execution()
        
        # Find and execute first trigger node
        if self.trigger_nodes:
            first_trigger = self.trigger_nodes[0]
            self.execution_context.start_step(first_trigger.node_id)
            
            try:
                result = await self._execute_email_trigger_node(first_trigger, ev.get("input_data", {}))
                self.execution_context.complete_step(first_trigger.node_id, result)
                
                return NodeExecutionEvent(
                    node_id=first_trigger.node_id,
                    result=result,
                    status=NodeStatus.COMPLETED,
                    execution_time=0.0,
                    metadata={"is_trigger": True}
                )
            except Exception as e:
                self.execution_context.fail_step(first_trigger.node_id, str(e))
                return NodeExecutionEvent(
                    node_id=first_trigger.node_id,
                    result=None,
                    status=NodeStatus.FAILED,
                    execution_time=0.0,
                    error=str(e)
                )
        else:
            # No trigger nodes found
            self.execution_context.fail_execution("No trigger nodes found")
            return StopEvent(result={"error": "No trigger nodes found"})
    
    @step
    async def process_node_execution(self, ctx: Context, ev: NodeExecutionEvent) -> List[NodeExecutionEvent]:
        """Process node execution results and trigger dependent nodes"""
        node_id = ev.node_id
        
        if ev.status == NodeStatus.FAILED:
            # Handle node failure
            self.execution_context.fail_execution(f"Node {node_id} failed: {ev.error}")
            return [StopEvent(result=self.execution_context.get_status_summary())]
        
        # Get dependent nodes
        dependent_node_ids = self.execution_graph.get(node_id, [])
        
        if not dependent_node_ids:
            # No dependent nodes, workflow complete
            self.execution_context.complete_execution()
            return [StopEvent(result=self.execution_context.get_status_summary())]
        
        # Execute dependent nodes
        dependent_events = []
        for dependent_id in dependent_node_ids:
            dependent_node = self._find_node_by_id(dependent_id)
            if dependent_node:
                # Check if all dependencies are satisfied
                if await self._are_dependencies_satisfied(dependent_node):
                    try:
                        self.execution_context.start_step(dependent_id)
                        
                        # Get input data from previous nodes
                        input_data = self._gather_input_data(dependent_node)
                        
                        # Execute dependent node
                        start_time = datetime.utcnow()
                        dependent_result = await self._execute_node(dependent_node, input_data)
                        execution_time = (datetime.utcnow() - start_time).total_seconds()
                        
                        self.execution_context.complete_step(dependent_id, dependent_result)
                        
                        dependent_events.append(NodeExecutionEvent(
                            node_id=dependent_id,
                            result=dependent_result,
                            status=NodeStatus.COMPLETED,
                            execution_time=execution_time
                        ))
                    except Exception as e:
                        self.execution_context.fail_step(dependent_id, str(e))
                        dependent_events.append(NodeExecutionEvent(
                            node_id=dependent_id,
                            result=None,
                            status=NodeStatus.FAILED,
                            execution_time=0.0,
                            error=str(e)
                        ))
        
        return dependent_events
    
    async def _execute_email_trigger_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email trigger node - fetch emails"""
        config = node.config
        
        # Mock email fetching for now
        # In production, this would connect to email service
        mock_email = {
            "email_id": f"email-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "sender": "customer@example.com",
            "recipient": "support@company.com",
            "subject": "Need help with my account",
            "content": "Hello, I'm having trouble accessing my account. Can you please help?",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "mock",
                "priority": "normal"
            }
        }
        
        return {
            "email_data": mock_email,
            "trigger_timestamp": datetime.utcnow().isoformat(),
            "source": "email_trigger"
        }
    
    async def _execute_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Any:
        """Execute a node based on its type"""
        node_type = self.node_registry.get_node_type(node.node_type_id)
        if not node_type:
            raise ValueError(f"Unknown node type: {node.node_type_id}")
        
        logger.info(f"Executing node: {node.node_id} (type: {node.node_type_id})")
        
        # Update step progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(25, "Starting execution")
        
        try:
            # Execute based on node type
            if node.node_type_id == "ai_model":
                result = await self._execute_ai_model_node(node, input_data)
            elif node.node_type_id == "condition":
                result = await self._execute_condition_node(node, input_data)
            elif node.node_type_id == "notification":
                result = await self._execute_notification_node(node, input_data)
            elif node.node_type_id == "approval":
                result = await self._execute_approval_node(node, input_data)
            elif node.node_type_id == "email_sender":
                result = await self._execute_email_sender_node(node, input_data)
            elif node.node_type_id == "data_logger":
                result = await self._execute_data_logger_node(node, input_data)
            elif node.node_type_id == "url_input":
                result = await self._execute_url_input_node(node, input_data)
            elif node.node_type_id == "web_scraper":
                result = await self._execute_web_scraper_node(node, input_data)
            elif node.node_type_id == "data_formatter":
                result = await self._execute_data_formatter_node(node, input_data)
            else:
                # Generic node execution
                result = await self._execute_generic_node(node, input_data)
            
            # Update progress to 100%
            if node.node_id in self.execution_context.steps:
                self.execution_context.steps[node.node_id].update_progress(100, "Execution completed")
            
            return result
            
        except Exception as e:
            logger.error(f"Node execution failed: {node.node_id} - {str(e)}")
            if node.node_id in self.execution_context.steps:
                self.execution_context.steps[node.node_id].update_progress(0, f"Execution failed: {str(e)}")
            raise
    
    async def _execute_ai_model_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI model node for email classification or response generation"""
        config = node.config
        
        # Update progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(50, "Processing with AI model")
        
        # Extract configuration
        provider = config.get("provider", "OpenAI")
        model = config.get("model", "gpt-4")
        prompt = config.get("prompt", "")
        temperature = config.get("temperature", 0.7)
        response_format = config.get("response_format", "text")
        
        # Get input content
        email_content = ""
        if "email_data" in input_data:
            email_data = input_data["email_data"]
            email_content = f"From: {email_data.get('sender', '')}\\nSubject: {email_data.get('subject', '')}\\nContent: {email_data.get('content', '')}"
        elif "email_content" in input_data:
            email_content = str(input_data["email_content"])
        else:
            email_content = str(input_data)
        
        # Build full prompt
        full_prompt = prompt.format(email_content=email_content, **input_data)
        
        # Simulate AI processing delay
        await asyncio.sleep(1)
        
        # Mock AI response based on node purpose
        if "classifier" in node.name.lower():
            # Email classification
            result = {
                "category": "technical_issue",
                "priority": "high",
                "sentiment": "neutral",
                "requires_human": False,
                "estimated_response_time": "1_hour",
                "key_topics": ["account", "access", "login"]
            }
        elif "response" in node.name.lower() or "generator" in node.name.lower():
            # Response generation
            result = {
                "response": "Thank you for contacting us. We understand you're having trouble accessing your account. Our technical team will investigate this issue and get back to you within 1 hour with a solution.",
                "tone": "professional",
                "word_count": 35
            }
        else:
            # Generic AI response
            result = {
                "ai_response": f"Processed: {email_content[:100]}...",
                "confidence": 0.85
            }
        
        return {
            "provider": provider,
            "model": model,
            "prompt": full_prompt[:200] + "..." if len(full_prompt) > 200 else full_prompt,
            "result": result,
            "temperature": temperature,
            "response_format": response_format,
            "processing_time": 1.0,
            "usage": {
                "prompt_tokens": len(full_prompt.split()),
                "completion_tokens": 50,
                "total_tokens": len(full_prompt.split()) + 50
            }
        }
    
    async def _execute_condition_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute condition node for routing decisions"""
        config = node.config
        
        # Update progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(75, "Evaluating conditions")
        
        conditions = config.get("conditions", [])
        default_route = config.get("default_route", "default")
        
        # Simulate condition evaluation
        await asyncio.sleep(0.2)
        
        # Mock condition evaluation - route based on classification
        selected_route = default_route
        if "classification" in input_data:
            classification = input_data["classification"]
            if isinstance(classification, dict):
                priority = classification.get("priority", "medium")
                requires_human = classification.get("requires_human", False)
                
                if priority == "urgent":
                    selected_route = "urgent-handler"
                elif requires_human:
                    selected_route = "human-review"
                else:
                    selected_route = "auto-responder"
        
        return {
            "condition_result": True,
            "selected_route": selected_route,
            "evaluation_details": {
                "conditions_checked": len(conditions),
                "matched_condition": selected_route != default_route,
                "routing_decision": selected_route
            },
            "input_data": input_data
        }
    
    async def _execute_notification_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification node"""
        config = node.config
        
        # Simulate notification sending
        await asyncio.sleep(0.5)
        
        return {
            "notification_sent": True,
            "notification_type": config.get("notification_type", "email"),
            "channel": config.get("channel", "default"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_approval_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute approval node"""
        config = node.config
        
        # Simulate approval process
        await asyncio.sleep(1)
        
        return {
            "approval_status": "pending",
            "assigned_to": config.get("reviewers", ["support-team"])[0],
            "timeout": config.get("escalation_timeout", 240),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_email_sender_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email sender node"""
        config = node.config
        
        # Update progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(75, "Sending email")
        
        # Simulate email sending
        await asyncio.sleep(0.8)
        
        return {
            "email_sent": True,
            "message_id": f"msg-{uuid.uuid4()}",
            "sent_at": datetime.utcnow().isoformat(),
            "from_address": config.get("from_address", "support@company.com"),
            "delivery_status": "delivered"
        }
    
    async def _execute_data_logger_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data logger node"""
        config = node.config
        
        # Simulate data logging
        await asyncio.sleep(0.3)
        
        metrics = config.get("metrics", [])
        logged_data = {}
        
        for metric in metrics:
            if metric == "response_time":
                logged_data[metric] = self.execution_context.execution_time or 0
            elif metric == "classification_accuracy":
                logged_data[metric] = 0.92
            elif metric == "customer_satisfaction":
                logged_data[metric] = 4.2
            elif metric == "resolution_rate":
                logged_data[metric] = 0.87
        
        return {
            "logged": True,
            "destination": config.get("log_destination", "analytics_db"),
            "metrics": logged_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_url_input_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute URL input node"""
        config = node.config
        url = config.get("url", "https://example.com")
        
        # Update progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(50, "Validating URL")
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")
        
        return {
            "url": url,
            "validation_status": "valid",
            "node_id": node.node_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_web_scraper_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web scraper node to extract content from a URL"""
        config = node.config
        target_url = input_data.get("url") or input_data.get("target_url")
        
        if not target_url:
            raise ValueError("No target URL provided for web scraping")
        
        # Update progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(25, "Fetching webpage")
        
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            # Mock scraping for now if libraries aren't available
            return await self._mock_web_scraper(target_url, config, node.node_id)
        
        try:
            # Configure request
            headers = {
                'User-Agent': config.get('user_agent', 'Mozilla/5.0 (compatible; WebScraper/1.0)')
            }
            timeout = config.get('timeout', 30)
            
            # Update progress
            if node.node_id in self.execution_context.steps:
                self.execution_context.steps[node.node_id].update_progress(50, "Downloading content")
            
            # Fetch the webpage
            response = requests.get(target_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Update progress
            if node.node_id in self.execution_context.steps:
                self.execution_context.steps[node.node_id].update_progress(75, "Parsing content")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles if configured
            if config.get('remove_scripts', True):
                for script in soup(["script", "style"]):
                    script.decompose()
            
            # Extract content based on configuration
            if config.get('extract_text_only', True):
                content = soup.get_text()
                # Clean up whitespace
                content = ' '.join(content.split())
            else:
                content = str(soup)
            
            # Limit content length if specified
            max_length = config.get('max_content_length', 10000)
            if max_length and len(content) > max_length:
                content = content[:max_length] + "... [truncated]"
            
            # Extract metadata
            metadata = {
                'title': soup.title.string if soup.title else '',
                'meta_description': '',
                'content_length': len(content),
                'response_status': response.status_code,
                'content_type': response.headers.get('content-type', '')
            }
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['meta_description'] = meta_desc.get('content', '')
            
            return {
                "content": content,
                "metadata": metadata,
                "source_url": target_url,
                "scrape_timestamp": datetime.utcnow().isoformat(),
                "node_id": node.node_id
            }
            
        except Exception as e:
            logger.error(f"Web scraping failed for {target_url}: {str(e)}")
            # Fall back to mock data if real scraping fails
            return await self._mock_web_scraper(target_url, config, node.node_id)
    
    async def _mock_web_scraper(self, url: str, config: Dict[str, Any], node_id: str) -> Dict[str, Any]:
        """Mock web scraper for testing when libraries aren't available"""
        await asyncio.sleep(1)  # Simulate network delay
        
        mock_content = f"""Welcome to Example Website
        
        This is a sample webpage content from {url}. 
        
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
        nisi ut aliquip ex ea commodo consequat.
        
        Key Features:
        - Feature 1: High performance web scraping
        - Feature 2: AI-powered content analysis  
        - Feature 3: Real-time data processing
        
        Contact us at info@example.com for more information.
        """
        
        metadata = {
            'title': 'Example Website - Mock Content',
            'meta_description': 'This is mock content for testing web scraping workflows',
            'content_length': len(mock_content),
            'response_status': 200,
            'content_type': 'text/html'
        }
        
        return {
            "content": mock_content,
            "metadata": metadata,
            "source_url": url,
            "scrape_timestamp": datetime.utcnow().isoformat(),
            "node_id": node_id,
            "mock_data": True
        }
    
    async def _execute_data_formatter_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data formatter node to structure output"""
        config = node.config
        summary_data = input_data.get("summary_data") or input_data.get("response")
        
        # Update progress
        if node.node_id in self.execution_context.steps:
            self.execution_context.steps[node.node_id].update_progress(50, "Formatting data")
        
        output_format = config.get("output_format", "structured")
        include_metadata = config.get("include_metadata", True)
        
        # Parse JSON if it's a string
        if isinstance(summary_data, str):
            try:
                import json
                summary_data = json.loads(summary_data)
            except json.JSONDecodeError:
                # If it's not JSON, treat as plain text
                summary_data = {"content": summary_data}
        
        # Structure the output
        formatted_output = {
            "summary": summary_data.get("summary", ""),
            "key_topics": summary_data.get("key_topics", []),
            "main_takeaways": summary_data.get("main_takeaways", []),
            "content_type": summary_data.get("content_type", "unknown"),
            "word_count": summary_data.get("word_count", 0),
            "reading_time": summary_data.get("reading_time", "unknown")
        }
        
        if include_metadata:
            formatted_output["metadata"] = {
                "processed_at": datetime.utcnow().isoformat(),
                "formatter_node": node.node_id,
                "output_format": output_format
            }
        
        return {
            "formatted_output": formatted_output,
            "node_id": node.node_id,
            "timestamp": datetime.utcnow().isoformat()
        }

class EnhancedVisualWorkflowExecutor:
    """Enhanced Visual Workflow Executor for managing workflow execution"""
    
    def __init__(self, node_registry):
        self.node_registry = node_registry
        self.active_executions = {}
        self.execution_logs = {}
    
    async def execute_workflow(self, workflow_id: str, visual_data: dict) -> dict:
        """Execute a visual workflow"""
        try:
            # Mock execution for now
            execution_id = f"exec_{workflow_id}_{datetime.utcnow().timestamp()}"
            
            self.active_executions[execution_id] = {
                "workflow_id": workflow_id,
                "status": ExecutionStatus.RUNNING,
                "started_at": datetime.utcnow().isoformat(),
                "progress": 0
            }
            
            # Simulate execution completion
            await asyncio.sleep(0.1)
            
            self.active_executions[execution_id].update({
                "status": ExecutionStatus.COMPLETED,
                "completed_at": datetime.utcnow().isoformat(),
                "progress": 100,
                "result": {"message": "Workflow executed successfully"}
            })
            
            return self.active_executions[execution_id]
            
        except Exception as e:
            return {
                "status": ExecutionStatus.FAILED,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def get_execution_status(self, execution_id: str) -> dict:
        """Get execution status"""
        return self.active_executions.get(execution_id, {"status": "not_found"})
    
    async def cancel_execution(self, execution_id: str) -> dict:
        """Cancel workflow execution"""
        if execution_id in self.active_executions:
            self.active_executions[execution_id]["status"] = ExecutionStatus.CANCELLED
            return {"message": "Execution cancelled", "execution_id": execution_id}
        return {"error": "Execution not found"}
    
    async def get_execution_logs(self, execution_id: str) -> list:
        """Get execution logs"""
        return self.execution_logs.get(execution_id, [])
