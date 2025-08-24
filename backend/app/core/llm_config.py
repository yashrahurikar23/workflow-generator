"""
LLM Configuration for LlamaIndex Agents
"""
import logging
import os
from typing import Optional

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class LLMSettings(BaseSettings):
    """LLM configuration settings"""
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.1
    
    # LLM provider selection
    llm_provider: str = "openai"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_llm_instance() -> LLM:
    """Get configured LLM instance for LlamaIndex agents"""
    settings = LLMSettings()
    
    try:
        if settings.llm_provider.lower() == "openai":
            if not settings.openai_api_key:
                # Try to get from environment if not in settings
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("No OpenAI API key found. Using mock LLM. Set OPENAI_API_KEY environment variable for real AI responses.")
                    return MockLLM()
                settings.openai_api_key = api_key
            
            return OpenAI(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=settings.openai_temperature
            )
        else:
            logger.warning(f"Unknown LLM provider: {settings.llm_provider}. Using mock LLM.")
            return MockLLM()
            
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}. Using mock LLM.")
        return MockLLM()

class MockLLM(LLM):
    """Mock LLM for development/testing when no API key is available"""
    
    @property
    def metadata(self):
        return {"model_name": "mock-llm"}
    
    def chat(self, messages, **kwargs):
        return self._generate_mock_response(messages)
    
    def complete(self, prompt, **kwargs):
        return self._generate_mock_response([{"content": prompt}])
    
    async def achat(self, messages, **kwargs):
        return self.chat(messages, **kwargs)
    
    async def acomplete(self, prompt, **kwargs):
        return self.complete(prompt, **kwargs)
    
    def _generate_mock_response(self, messages):
        """Generate a mock response for development"""
        latest_message = messages[-1] if messages else {"content": ""}
        content = latest_message.get("content", "")
        
        # Simple mock responses based on content
        if any(keyword in content.lower() for keyword in ["scrape", "website", "web"]):
            mock_content = """I'll help you create a web scraping workflow. Based on your request, I recommend:

1. **Web Scraper Node**: Extract content from target URLs
2. **AI Processor Node**: Analyze and clean the scraped content  
3. **File Storage Node**: Save the processed results
4. **Notification Node**: Alert when scraping is complete

This creates a complete automated web scraping pipeline. Would you like me to configure any specific scraping parameters?"""
        
        elif any(keyword in content.lower() for keyword in ["email", "automation"]):
            mock_content = """I'll help you create an email automation workflow. Here's what I suggest:

1. **Email Trigger Node**: Monitor incoming emails
2. **AI Processor Node**: Classify and analyze email content
3. **Condition Node**: Determine appropriate responses
4. **Notification Node**: Send automated replies

This workflow will automatically handle incoming emails based on your criteria. What type of email automation are you looking for?"""
        
        else:
            mock_content = f"""I understand you want to create a workflow for: "{content}"

I'm analyzing your requirements and will generate appropriate workflow nodes and connections. Since this is a mock response (no OpenAI API key configured), I would typically:

1. Analyze your specific requirements
2. Select appropriate node types
3. Create optimal connections between nodes
4. Generate proper configurations

To get real AI-powered responses, please set your OPENAI_API_KEY environment variable."""
        
        # Simple response object
        class MockResponse:
            def __init__(self, content):
                self.message = type('obj', (object,), {'content': content})()
            
            def __str__(self):
                return self.message.content
        
        return MockResponse(mock_content)
