#!/usr/bin/env python3
"""
Setup script for Web Scraping workflow
Simple workflow: URL Input -> Web Scraping -> AI Summarization -> Output
"""
import asyncio
import os
import sys
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def setup_web_scraping_workflow():
    """Setup the web scraping workflow in MongoDB"""
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.workflow_generator
        
        print("🔄 Setting up Web Scraping workflow...")
        
        # Clear existing workflows
        delete_result = await db.workflows.delete_many({})
        print(f"✅ Cleared {delete_result.deleted_count} existing workflows")
        
        # Web Scraping Workflow
        web_scraping_workflow = {
            'workflow_id': 'web-scraping-v1',
            'name': 'Web Content Scraper & Summarizer',
            'description': 'Simple workflow to scrape website content and generate AI-powered summaries',
            'workflow_type': 'visual',
            'status': 'active',
            'tags': ['web-scraping', 'ai', 'summarization', 'content'],
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'execution_count': 0,
            'last_executed_at': None,
            'visual_data': {
                'nodes': [
                    {
                        'node_id': 'url-input',
                        'node_type_id': 'url_input',
                        'name': 'Website URL Input',
                        'position': {'x': 100, 'y': 200},
                        'config': {
                            'url': 'https://example.com',
                            'validation': 'url',
                            'placeholder': 'Enter website URL to scrape...'
                        }
                    },
                    {
                        'node_id': 'web-scraper',
                        'node_type_id': 'web_scraper',
                        'name': 'Content Scraper',
                        'position': {'x': 400, 'y': 200},
                        'config': {
                            'scrape_type': 'full_page',
                            'remove_scripts': True,
                            'remove_styles': True,
                            'extract_text_only': True,
                            'max_content_length': 10000,
                            'timeout': 30,
                            'user_agent': 'Mozilla/5.0 (compatible; WebScraper/1.0)'
                        }
                    },
                    {
                        'node_id': 'ai-summarizer',
                        'node_type_id': 'ai_model',
                        'name': 'Content Summarizer',
                        'position': {'x': 700, 'y': 200},
                        'config': {
                            'provider': 'OpenAI',
                            'model': 'gpt-4',
                            'prompt': '''Analyze and summarize the following web content:

Content: {scraped_content}
URL: {source_url}

Please provide:
1. A concise summary (2-3 sentences)
2. Key topics/themes identified
3. Main takeaways or insights
4. Content type (article, blog, product page, etc.)

Format your response as JSON:
{
  "summary": "Brief summary here",
  "key_topics": ["topic1", "topic2", "topic3"],
  "main_takeaways": ["takeaway1", "takeaway2"],
  "content_type": "article/blog/product/news/etc",
  "word_count": estimated_word_count,
  "reading_time": "X minutes"
}''',
                            'temperature': 0.3,
                            'response_format': 'json'
                        }
                    },
                    {
                        'node_id': 'output-formatter',
                        'node_type_id': 'data_formatter',
                        'name': 'Results Formatter',
                        'position': {'x': 1000, 'y': 200},
                        'config': {
                            'output_format': 'structured',
                            'include_metadata': True,
                            'save_to_file': False,
                            'display_format': 'json'
                        }
                    }
                ],
                'connections': [
                    {
                        'connection_id': 'input-to-scraper',
                        'source_node_id': 'url-input',
                        'target_node_id': 'web-scraper',
                        'source_output': 'url',
                        'target_input': 'target_url'
                    },
                    {
                        'connection_id': 'scraper-to-ai',
                        'source_node_id': 'web-scraper',
                        'target_node_id': 'ai-summarizer',
                        'source_output': 'content',
                        'target_input': 'scraped_content'
                    },
                    {
                        'connection_id': 'ai-to-output',
                        'source_node_id': 'ai-summarizer',
                        'target_node_id': 'output-formatter',
                        'source_output': 'response',
                        'target_input': 'summary_data'
                    }
                ]
            },
            'execution_settings': {
                'max_concurrent_executions': 3,
                'retry_failed_steps': True,
                'max_retries': 2,
                'step_timeout': 60,
                'workflow_timeout': 300
            }
        }
        
        # Insert the workflow
        result = await db.workflows.insert_one(web_scraping_workflow)
        print(f"✅ Created web scraping workflow: {result.inserted_id}")
        
        # Verify insertion
        workflow_count = await db.workflows.count_documents({})
        print(f"✅ Total workflows in database: {workflow_count}")
        
        # Print workflow summary
        workflow = await db.workflows.find_one({'workflow_id': 'web-scraping-v1'})
        if workflow:
            print("\\n📋 Workflow Summary:")
            print(f"   Name: {workflow['name']}")
            print(f"   ID: {workflow['workflow_id']}")
            print(f"   Nodes: {len(workflow['visual_data']['nodes'])}")
            print(f"   Connections: {len(workflow['visual_data']['connections'])}")
            print(f"   Status: {workflow['status']}")
        
        # Close connection
        client.close()
        print("\\n✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        return False

async def setup_test_urls():
    """Setup test URLs for scraping"""
    
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.workflow_generator
        
        # Clear existing test URLs
        await db.test_urls.delete_many({})
        
        # Sample URLs for testing
        test_urls = [
            {
                'url_id': 'test-001',
                'url': 'https://example.com',
                'description': 'Example.com - Simple test page',
                'expected_content_type': 'webpage',
                'status': 'pending'
            },
            {
                'url_id': 'test-002', 
                'url': 'https://httpbin.org/html',
                'description': 'HTTPBin HTML test page',
                'expected_content_type': 'test_page',
                'status': 'pending'
            },
            {
                'url_id': 'test-003',
                'url': 'https://jsonplaceholder.typicode.com/',
                'description': 'JSONPlaceholder API documentation',
                'expected_content_type': 'documentation',
                'status': 'pending'
            }
        ]
        
        # Insert test URLs
        result = await db.test_urls.insert_many(test_urls)
        print(f"✅ Created {len(result.inserted_ids)} test URLs")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up test URLs: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Web Scraping Workflow System")
    print("=" * 60)
    
    async def main():
        # Setup workflow
        workflow_success = await setup_web_scraping_workflow()
        
        # Setup test data
        test_success = await setup_test_urls()
        
        if workflow_success and test_success:
            print("\\n🎉 Setup completed successfully!")
            print("\\nNext steps:")
            print("1. Start the backend server: cd backend && uvicorn app.main:app --reload")
            print("2. Test the workflow: cd backend && python test_web_scraping.py")
            print("3. Start the frontend: cd frontend && npm run dev")
            print("\\nWorkflow Flow:")
            print("URL Input → Web Scraper → AI Summarizer → Formatted Output")
        else:
            print("\\n❌ Setup encountered errors. Please check the logs above.")
    
    asyncio.run(main())
