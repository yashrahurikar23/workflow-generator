#!/usr/bin/env python3
"""
Test script to validate the Web Scraping workflow
"""
import asyncio
import os
import sys

# Since we're in the backend directory, adjust the path
sys.path.append(os.path.dirname(__file__))

from app.models.workflow_visual import Workflow, WorkflowNode
from app.services.enhanced_workflow_executor import \
    EnhancedVisualWorkflowExecutor
from app.services.node_registry import NodeTypeRegistry
from motor.motor_asyncio import AsyncIOMotorClient


async def test_web_scraping():
    """Test the web scraping workflow"""
    print("🚀 Testing Web Scraping Workflow")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.workflow_generator
        
        # Get the web scraping workflow
        workflow_data = await db.workflows.find_one({"workflow_id": "web-scraping-v1"})
        if not workflow_data:
            print("❌ Web scraping workflow not found in database")
            print("   Make sure to run: python ../setup_web_scraping.py")
            return
        
        workflow = Workflow(**workflow_data)
        print(f"✅ Found workflow: {workflow.name}")
        print(f"   Nodes: {len(workflow.visual_data.nodes)}")
        print(f"   Connections: {len(workflow.visual_data.connections)}")
        
        # Display workflow structure
        print("\\n📋 Workflow Structure:")
        for node in workflow.visual_data.nodes:
            print(f"   {node.node_id} ({node.node_type_id}) -> {node.name}")
        
        print("\\n🔗 Node Connections:")
        for conn in workflow.visual_data.connections:
            print(f"   {conn.source_node_id} -> {conn.target_node_id}")
        
        # Create enhanced executor
        node_registry = NodeTypeRegistry()
        executor = EnhancedVisualWorkflowExecutor(node_registry)
        print("\\n✅ Enhanced workflow executor created")
        
        # Test workflow execution with different URLs
        test_urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://jsonplaceholder.typicode.com/"
        ]
        
        for test_url in test_urls:
            print(f"\\n🔄 Testing with URL: {test_url}")
            print("-" * 40)
            
            # Start workflow execution
            execution_id = await executor.execute_workflow(workflow, {
                "test_mode": True,
                "url_input": test_url
            })
            
            print(f"✅ Workflow execution started")
            print(f"   Execution ID: {execution_id}")
            
            # Monitor execution
            print("\\n📊 Monitoring execution status...")
            for i in range(8):  # Monitor for up to 8 seconds
                status = executor.get_execution_status(execution_id)
                if status:
                    print(f"   Status: {status.get('status', 'unknown')}")
                    print(f"   Progress: {status.get('progress_percentage', 0)}%")
                    
                    # Show step progress
                    step_details = status.get('step_details', {})
                    for step_id, step_info in step_details.items():
                        step_status = step_info.get('status', 'unknown')
                        step_progress = step_info.get('progress', 0)
                        print(f"     {step_id}: {step_status} ({step_progress}%)")
                    
                    if status.get('status') == 'completed':
                        print("   ✅ Execution completed!")
                        break
                    elif status.get('status') == 'failed':
                        print("   ❌ Execution failed!")
                        break
                
                await asyncio.sleep(1)
            
            # Get execution results
            results = executor.get_execution_result(execution_id)
            if results:
                print("\\n📄 Execution Results:")
                print(f"   Final Status: {results.get('status', 'unknown')}")
                
                # Show results from each node
                node_results = results.get('node_results', {})
                for node_id, result in node_results.items():
                    print(f"\\n   Node: {node_id}")
                    if isinstance(result, dict):
                        if 'content' in result:
                            content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                            print(f"     Content: {content_preview}")
                        if 'metadata' in result:
                            metadata = result['metadata']
                            print(f"     Title: {metadata.get('title', 'N/A')}")
                            print(f"     Content Length: {metadata.get('content_length', 0)}")
                        if 'formatted_output' in result:
                            output = result['formatted_output']
                            print(f"     Summary: {output.get('summary', 'N/A')}")
                            print(f"     Topics: {output.get('key_topics', [])}")
            
            print("\\n" + "="*60)
        
        # Get execution logs
        print("\\n📝 Recent execution logs:")
        logs = await executor.get_execution_logs(limit=5)
        for log in logs[:3]:
            print(f"   {log.get('timestamp', '')}: {log.get('message', '')}")
        
        print("\\n🎉 Web scraping workflow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_node_registry():
    """Test that web scraping nodes are properly registered"""
    print("\\n🔧 Testing Node Registry...")
    
    registry = NodeTypeRegistry()
    
    # Test that web scraping nodes are registered
    web_scraping_nodes = ['url_input', 'web_scraper', 'data_formatter']
    
    for node_type_id in web_scraping_nodes:
        node_type = registry.get_node_type(node_type_id)
        if node_type:
            print(f"   ✅ {node_type_id}: {node_type.name}")
        else:
            print(f"   ❌ {node_type_id}: Not found")
    
    # Test web scraping category
    categories = registry.get_categories()
    web_category = next((cat for cat in categories if cat.id == 'web_scraping'), None)
    if web_category:
        print(f"   ✅ Web Scraping Category: {web_category.name}")
    else:
        print(f"   ❌ Web Scraping Category: Not found")

if __name__ == "__main__":
    async def main():
        await test_node_registry()
        await test_web_scraping()
    
    asyncio.run(main())
