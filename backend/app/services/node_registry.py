"""
Node Type Registry - Manages available node types for the visual workflow editor
"""
from typing import Dict, List, Optional

from app.models.workflow_visual import (ConfigField, NodeCategory, NodeInput,
                                        NodeOutput, NodeType)


class NodeTypeRegistry:
    """Registry for managing available node types and categories"""
    
    def __init__(self):
        self._node_types: Dict[str, NodeType] = {}
        self._categories: Dict[str, NodeCategory] = {}
        self._initialize_default_types()
    
    def _initialize_default_types(self):
        """Initialize default node types and categories"""
        self._register_categories()
        self._register_ai_nodes()
        self._register_data_nodes()
        self._register_trigger_nodes()
        self._register_integration_nodes()
        self._register_logic_nodes()
        self._register_web_scraping_nodes()
    
    def _register_categories(self):
        """Register node categories"""
        categories = [
            NodeCategory(
                id="ai_models",
                name="AI Models",
                description="Large Language Models and AI processing nodes",
                icon="brain",
                color="#8B5CF6",
                order=1
            ),
            NodeCategory(
                id="data_processing",
                name="Data Processing",
                description="Transform, filter, and manipulate data",
                icon="database",
                color="#10B981",
                order=2
            ),
            NodeCategory(
                id="triggers",
                name="Triggers",
                description="Events that start workflow execution",
                icon="zap",
                color="#F59E0B",
                order=3
            ),
            NodeCategory(
                id="integrations",
                name="Integrations",
                description="Connect to external services and APIs",
                icon="plug",
                color="#3B82F6",
                order=4
            ),
            NodeCategory(
                id="logic",
                name="Logic & Control",
                description="Conditional logic, loops, and flow control",
                icon="git-branch",
                color="#EF4444",
                order=5
            ),
            NodeCategory(
                id="communications",
                name="Communications",
                description="Email, messaging, and notifications",
                icon="mail",
                color="#06B6D4",
                order=6
            ),
            NodeCategory(
                id="web_scraping",
                name="Web Scraping",
                description="Extract and process content from websites",
                icon="globe",
                color="#22C55E",
                order=7
            )
        ]
        
        for category in categories:
            self._categories[category.id] = category
    
    def _register_ai_nodes(self):
        """Register AI and LLM related nodes"""
        
        # AI Model Node - Main LLM processing node
        ai_model_node = NodeType(
            id="ai_model",
            name="AI Model",
            description="Process text using Large Language Models like GPT, Claude, or Llama",
            category="ai_models",
            icon="brain",
            color="#8B5CF6",
            inputs=[
                NodeInput(
                    id="prompt",
                    label="Prompt",
                    type="string",
                    required=True,
                    description="Input prompt for the AI model"
                ),
                NodeInput(
                    id="context",
                    label="Context",
                    type="string",
                    required=False,
                    description="Additional context for the AI model"
                )
            ],
            outputs=[
                NodeOutput(
                    id="response",
                    label="Response",
                    type="string",
                    description="AI model response"
                ),
                NodeOutput(
                    id="tokens_used",
                    label="Tokens Used",
                    type="number",
                    description="Number of tokens consumed"
                )
            ],
            config_fields=[
                ConfigField(
                    key="provider",
                    type="select",
                    label="AI Provider",
                    description="Choose your AI model provider",
                    required=True,
                    default_value="openai",
                    options=["openai", "anthropic", "google", "mistral", "local"]
                ),
                ConfigField(
                    key="model",
                    type="select",
                    label="Model",
                    description="Specific model to use",
                    required=True,
                    default_value="gpt-4",
                    options=["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "gemini-pro"]
                ),
                ConfigField(
                    key="temperature",
                    type="number",
                    label="Temperature",
                    description="Controls randomness (0.0 = deterministic, 1.0 = creative)",
                    required=False,
                    default_value=0.7
                ),
                ConfigField(
                    key="max_tokens",
                    type="number",
                    label="Max Tokens",
                    description="Maximum length of the response",
                    required=False,
                    default_value=1000
                ),
                ConfigField(
                    key="system_prompt",
                    type="string",
                    label="System Prompt",
                    description="System instructions for the AI model",
                    required=False,
                    default_value=""
                )
            ],
            is_template=True,
            tags=["ai", "llm", "text-processing"],
            version="1.0.0"
        )
        
        # Text Analysis Node
        text_analysis_node = NodeType(
            id="text_analysis",
            name="Text Analysis",
            description="Analyze text for sentiment, entities, keywords, and other insights",
            category="ai_models",
            icon="search",
            color="#8B5CF6",
            inputs=[
                NodeInput(
                    id="text",
                    label="Text",
                    type="string",
                    required=True,
                    description="Text to analyze"
                )
            ],
            outputs=[
                NodeOutput(
                    id="sentiment",
                    label="Sentiment",
                    type="object",
                    description="Sentiment analysis results"
                ),
                NodeOutput(
                    id="entities",
                    label="Entities", 
                    type="array",
                    description="Extracted entities"
                ),
                NodeOutput(
                    id="keywords",
                    label="Keywords",
                    type="array",
                    description="Key phrases and keywords"
                )
            ],
            config_fields=[
                ConfigField(
                    key="analysis_type",
                    type="select",
                    label="Analysis Type",
                    description="Type of analysis to perform",
                    required=True,
                    default_value="all",
                    options=["sentiment", "entities", "keywords", "all"]
                ),
                ConfigField(
                    key="language",
                    type="select",
                    label="Language",
                    description="Text language",
                    required=False,
                    default_value="auto",
                    options=["auto", "en", "es", "fr", "de", "it"]
                )
            ],
            tags=["ai", "text", "analysis", "nlp"],
            version="1.0.0"
        )
        
        self._node_types["ai_model"] = ai_model_node
        self._node_types["text_analysis"] = text_analysis_node
    
    def _register_data_nodes(self):
        """Register data processing nodes"""
        
        # Data Transform Node
        data_transform_node = NodeType(
            id="data_transform",
            name="Data Transform",
            description="Transform, filter, and manipulate data using various operations",
            category="data_processing",
            icon="settings",
            color="#10B981",
            inputs=[
                NodeInput(
                    id="data",
                    label="Data",
                    type="any",
                    required=True,
                    description="Input data to transform"
                )
            ],
            outputs=[
                NodeOutput(
                    id="transformed_data",
                    label="Transformed Data",
                    type="any",
                    description="Transformed output data"
                )
            ],
            config_fields=[
                ConfigField(
                    key="operation",
                    type="select",
                    label="Operation",
                    description="Type of data transformation",
                    required=True,
                    default_value="filter",
                    options=["filter", "map", "reduce", "sort", "group", "join"]
                ),
                ConfigField(
                    key="expression",
                    type="string",
                    label="Expression",
                    description="Transformation expression or filter criteria",
                    required=True,
                    default_value=""
                ),
                ConfigField(
                    key="output_format",
                    type="select",
                    label="Output Format",
                    description="Format of the output data",
                    required=False,
                    default_value="json",
                    options=["json", "csv", "xml", "yaml"]
                )
            ],
            tags=["data", "transform", "filter"],
            version="1.0.0"
        )
        
        self._node_types["data_transform"] = data_transform_node
    
    def _register_trigger_nodes(self):
        """Register trigger nodes"""
        
        # Webhook Trigger
        webhook_trigger = NodeType(
            id="webhook_trigger",
            name="Webhook Trigger",
            description="Start workflow when HTTP webhook is called",
            category="triggers",
            icon="globe",
            color="#F59E0B",
            inputs=[],
            outputs=[
                NodeOutput(
                    id="payload",
                    label="Payload",
                    type="object",
                    description="Webhook payload data"
                ),
                NodeOutput(
                    id="headers",
                    label="Headers",
                    type="object",
                    description="HTTP headers"
                )
            ],
            config_fields=[
                ConfigField(
                    key="method",
                    type="select",
                    label="HTTP Method",
                    description="Allowed HTTP methods",
                    required=True,
                    default_value="POST",
                    options=["GET", "POST", "PUT", "DELETE", "PATCH"]
                ),
                ConfigField(
                    key="path",
                    type="string",
                    label="Webhook Path",
                    description="Custom path for the webhook (optional)",
                    required=False,
                    default_value=""
                ),
                ConfigField(
                    key="authentication",
                    type="select",
                    label="Authentication",
                    description="Authentication method for webhook",
                    required=False,
                    default_value="none",
                    options=["none", "api_key", "bearer_token", "basic_auth"]
                )
            ],
            tags=["trigger", "webhook", "http"],
            version="1.0.0"
        )
        
        # Schedule Trigger
        schedule_trigger = NodeType(
            id="schedule_trigger",
            name="Schedule Trigger",
            description="Start workflow on a schedule (cron-based)",
            category="triggers",
            icon="clock",
            color="#F59E0B",
            inputs=[],
            outputs=[
                NodeOutput(
                    id="timestamp",
                    label="Timestamp",
                    type="string",
                    description="Execution timestamp"
                ),
                NodeOutput(
                    id="schedule_info",
                    label="Schedule Info",
                    type="object",
                    description="Schedule metadata"
                )
            ],
            config_fields=[
                ConfigField(
                    key="schedule_type",
                    type="select",
                    label="Schedule Type",
                    description="Type of schedule",
                    required=True,
                    default_value="interval",
                    options=["interval", "cron", "once"]
                ),
                ConfigField(
                    key="interval_minutes",
                    type="number",
                    label="Interval (Minutes)",
                    description="Interval in minutes (for interval type)",
                    required=False,
                    default_value=60
                ),
                ConfigField(
                    key="cron_expression",
                    type="string",
                    label="Cron Expression",
                    description="Cron expression (for cron type)",
                    required=False,
                    default_value="0 0 * * *"
                ),
                ConfigField(
                    key="timezone",
                    type="string",
                    label="Timezone",
                    description="Timezone for schedule",
                    required=False,
                    default_value="UTC"
                )
            ],
            tags=["trigger", "schedule", "cron", "timer"],
            version="1.0.0"
        )
        
        self._node_types["webhook_trigger"] = webhook_trigger
        self._node_types["schedule_trigger"] = schedule_trigger
    
    def _register_integration_nodes(self):
        """Register integration nodes"""
        
        # HTTP Request Node
        http_request_node = NodeType(
            id="http_request",
            name="HTTP Request",
            description="Make HTTP requests to external APIs and services",
            category="integrations",
            icon="globe",
            color="#3B82F6",
            inputs=[
                NodeInput(
                    id="url",
                    label="URL",
                    type="string",
                    required=True,
                    description="Request URL"
                ),
                NodeInput(
                    id="body",
                    label="Body",
                    type="any",
                    required=False,
                    description="Request body"
                )
            ],
            outputs=[
                NodeOutput(
                    id="response",
                    label="Response",
                    type="object",
                    description="HTTP response"
                ),
                NodeOutput(
                    id="status_code",
                    label="Status Code",
                    type="number",
                    description="HTTP status code"
                )
            ],
            config_fields=[
                ConfigField(
                    key="method",
                    type="select",
                    label="HTTP Method",
                    description="HTTP request method",
                    required=True,
                    default_value="GET",
                    options=["GET", "POST", "PUT", "DELETE", "PATCH"]
                ),
                ConfigField(
                    key="headers",
                    type="json",
                    label="Headers",
                    description="HTTP headers (JSON format)",
                    required=False,
                    default_value={}
                ),
                ConfigField(
                    key="timeout",
                    type="number",
                    label="Timeout (seconds)",
                    description="Request timeout in seconds",
                    required=False,
                    default_value=30
                )
            ],
            tags=["integration", "http", "api", "request"],
            version="1.0.0"
        )
        
        self._node_types["http_request"] = http_request_node
    
    def _register_logic_nodes(self):
        """Register logic and control flow nodes"""
        
        # Condition Node
        condition_node = NodeType(
            id="condition",
            name="Condition",
            description="Route workflow based on conditions",
            category="logic",
            icon="git-branch",
            color="#EF4444",
            inputs=[
                NodeInput(
                    id="value",
                    label="Value",
                    type="any",
                    required=True,
                    description="Value to evaluate"
                )
            ],
            outputs=[
                NodeOutput(
                    id="true",
                    label="True",
                    type="any",
                    description="Path when condition is true"
                ),
                NodeOutput(
                    id="false",
                    label="False",
                    type="any",
                    description="Path when condition is false"
                )
            ],
            config_fields=[
                ConfigField(
                    key="operator",
                    type="select",
                    label="Operator",
                    description="Comparison operator",
                    required=True,
                    default_value="equals",
                    options=["equals", "not_equals", "greater_than", "less_than", "contains", "starts_with", "ends_with"]
                ),
                ConfigField(
                    key="compare_value",
                    type="string",
                    label="Compare Value",
                    description="Value to compare against",
                    required=True,
                    default_value=""
                )
            ],
            tags=["logic", "condition", "branch", "if"],
            version="1.0.0"
        )
        
        self._node_types["condition"] = condition_node
    
    def _register_web_scraping_nodes(self):
        """Register web scraping related nodes"""
        
        # URL Input Node
        url_input_node = NodeType(
            id="url_input",
            name="URL Input",
            description="Input a website URL for scraping",
            category="web_scraping",
            icon="link",
            color="#22C55E",
            inputs=[],  # No inputs - this is a starting node
            outputs=[
                NodeOutput(
                    id="url",
                    label="URL",
                    type="string",
                    description="The website URL to scrape"
                )
            ],
            config_fields=[
                ConfigField(
                    key="url",
                    type="url",
                    label="Website URL",
                    description="Enter the URL of the website to scrape",
                    required=True,
                    default_value="https://example.com"
                ),
                ConfigField(
                    key="validation",
                    type="select",
                    label="URL Validation",
                    description="Validation level for the URL",
                    required=False,
                    default_value="url",
                    options=["url", "strict", "permissive"]
                )
            ],
            tags=["input", "url", "web", "scraping"]
        )
        
        # Web Scraper Node
        web_scraper_node = NodeType(
            id="web_scraper",
            name="Web Scraper",
            description="Extract content from web pages",
            category="web_scraping",
            icon="globe",
            color="#22C55E",
            inputs=[
                NodeInput(
                    id="target_url",
                    label="Target URL",
                    type="string",
                    required=True,
                    description="URL of the website to scrape"
                )
            ],
            outputs=[
                NodeOutput(
                    id="content",
                    label="Scraped Content",
                    type="string",
                    description="Extracted text content from the webpage"
                ),
                NodeOutput(
                    id="metadata",
                    label="Page Metadata",
                    type="object",
                    description="Metadata about the scraped page (title, meta tags, etc.)"
                ),
                NodeOutput(
                    id="source_url",
                    label="Source URL",
                    type="string", 
                    description="The original URL that was scraped"
                )
            ],
            config_fields=[
                ConfigField(
                    key="scrape_type",
                    type="select",
                    label="Scraping Type",
                    description="What content to extract from the page",
                    required=True,
                    default_value="full_page",
                    options=["full_page", "text_only", "main_content", "specific_selector"]
                ),
                ConfigField(
                    key="remove_scripts",
                    type="boolean",
                    label="Remove Scripts",
                    description="Remove JavaScript from the scraped content",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    key="remove_styles",
                    type="boolean",
                    label="Remove Styles",
                    description="Remove CSS styles from the scraped content", 
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    key="extract_text_only",
                    type="boolean",
                    label="Text Only",
                    description="Extract only text content, removing HTML tags",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    key="max_content_length",
                    type="number",
                    label="Max Content Length",
                    description="Maximum number of characters to extract",
                    required=False,
                    default_value=10000
                ),
                ConfigField(
                    key="timeout",
                    type="number",
                    label="Timeout (seconds)",
                    description="Maximum time to wait for page load",
                    required=False,
                    default_value=30
                ),
                ConfigField(
                    key="user_agent",
                    type="string",
                    label="User Agent",
                    description="User agent string to use for requests",
                    required=False,
                    default_value="Mozilla/5.0 (compatible; WebScraper/1.0)"
                )
            ],
            tags=["scraping", "web", "content", "extraction"]
        )
        
        # Data Formatter Node
        data_formatter_node = NodeType(
            id="data_formatter",
            name="Data Formatter", 
            description="Format and structure output data",
            category="data_processing",
            icon="file-text",
            color="#10B981",
            inputs=[
                NodeInput(
                    id="summary_data",
                    label="Summary Data",
                    type="object",
                    required=True,
                    description="Data to format and structure"
                )
            ],
            outputs=[
                NodeOutput(
                    id="formatted_output",
                    label="Formatted Output",
                    type="object",
                    description="Structured and formatted data"
                )
            ],
            config_fields=[
                ConfigField(
                    key="output_format",
                    type="select", 
                    label="Output Format",
                    description="How to format the output data",
                    required=True,
                    default_value="structured",
                    options=["structured", "markdown", "html", "plain_text"]
                ),
                ConfigField(
                    key="include_metadata",
                    type="boolean",
                    label="Include Metadata",
                    description="Include metadata in the output",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    key="save_to_file",
                    type="boolean",
                    label="Save to File",
                    description="Save output to a file",
                    required=False,
                    default_value=False
                )
            ],
            tags=["formatting", "output", "structure", "data"]
        )
        
        # Register all web scraping nodes
        self._node_types["url_input"] = url_input_node
        self._node_types["web_scraper"] = web_scraper_node
        self._node_types["data_formatter"] = data_formatter_node

    def register_node_type(self, node_type: NodeType) -> None:
        """Register a custom node type"""
        self._node_types[node_type.id] = node_type
    
    def get_node_type(self, node_type_id: str) -> Optional[NodeType]:
        """Get a specific node type by ID"""
        return self._node_types.get(node_type_id)
    
    def get_all_node_types(self) -> List[NodeType]:
        """Get all registered node types"""
        return list(self._node_types.values())
    
    def get_node_types_by_category(self, category_id: str) -> List[NodeType]:
        """Get all node types in a specific category"""
        return [node_type for node_type in self._node_types.values() 
                if node_type.category == category_id]
    
    def get_category(self, category_id: str) -> Optional[NodeCategory]:
        """Get a specific category by ID"""
        return self._categories.get(category_id)
    
    def get_all_categories(self) -> List[NodeCategory]:
        """Get all registered categories"""
        return sorted(self._categories.values(), key=lambda c: c.order)
    
    def search_node_types(self, query: str) -> List[NodeType]:
        """Search node types by name, description, or tags"""
        query = query.lower()
        results = []
        
        for node_type in self._node_types.values():
            if (query in node_type.name.lower() or 
                query in node_type.description.lower() or 
                any(query in tag.lower() for tag in node_type.tags)):
                results.append(node_type)
        
        return results


# Global registry instance
node_registry = NodeTypeRegistry()
