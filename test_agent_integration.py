#!/usr/bin/env python3
"""
Test script for LlamaIndex Agent Integration
"""
import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.base_agent import WorkflowAgentOrchestrator
from app.agents.workflow_builder import WorkflowBuilderAgent
from app.agents.workflow_planner import WorkflowPlannerAgent


async def test_agent_integration():
    """Test the LlamaIndex agent integration"""
    
    print("🚀 Testing LlamaIndex Agent Integration")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = WorkflowAgentOrchestrator()
    
    # Create and register agents
    planner = WorkflowPlannerAgent()
    builder = WorkflowBuilderAgent()
    
    orchestrator.register_agent(planner)
    orchestrator.register_agent(builder)
    
    print("✅ Agents registered successfully")
    
    # Test workflow requests
    test_requests = [
        "Create a web scraping workflow that extracts content from a news website",
        "Build an email automation workflow that responds to customer inquiries",
        "I need a workflow to scrape product prices from an e-commerce site"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📋 Test {i}: {request}")
        print("-" * 60)
        
        try:
            # Mock workflow context
            context = {
                "current_workflow": {
                    "name": f"Test Workflow {i}",
                    "visual_data": {"nodes": [], "connections": []},
                    "messages": []
                }
            }
            
            # Process the request
            result = await orchestrator.process_workflow_request(request, context)
            
            if result["success"]:
                print("✅ Success!")
                print(f"📊 Generated workflow plan with {len(result.get('workflow_plan', {}).get('nodes', []))} nodes")
                print(f"🏗️ Built workflow with {len(result.get('generated_workflow', {}).get('visual_data', {}).get('nodes', []))} visual nodes")
                print(f"💬 AI Response: {result['ai_message']['content'][:200]}...")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Agent integration test completed!")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  No OPENAI_API_KEY found. Testing with mock LLM.")
        print("   Set OPENAI_API_KEY environment variable for real AI responses.")
        print()
    
    try:
        asyncio.run(test_agent_integration())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
