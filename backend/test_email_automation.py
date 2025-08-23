#!/usr/bin/env python3
"""
Test script to validate the Customer Support Email Automation workflow
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


async def test_email_automation():
    """Test the email automation workflow"""
    print("🚀 Testing Customer Support Email Automation")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.workflow_generator
        
        # Get the email automation workflow
        workflow_data = await db.workflows.find_one({"workflow_id": "email-automation-v1"})
        if not workflow_data:
            print("❌ Email automation workflow not found in database")
            return
        
        workflow = Workflow(**workflow_data)
        print(f"✅ Found workflow: {workflow.name}")
        print(f"   Nodes: {len(workflow.visual_data.nodes)}")
        print(f"   Connections: {len(workflow.visual_data.connections)}")
        
        # Create enhanced executor
        node_registry = NodeTypeRegistry()
        executor = EnhancedVisualWorkflowExecutor(node_registry)
        print("✅ Enhanced workflow executor created")
        
        # Test workflow execution
        print("\n🔄 Starting workflow execution...")
        execution_id = await executor.execute_workflow(workflow, {
            "test_mode": True,
            "email_source": "mock"
        })
        
        print(f"✅ Workflow execution started")
        print(f"   Execution ID: {execution_id}")
        
        # Monitor execution for a few seconds
        print("\n📊 Monitoring execution status...")
        for i in range(5):
            status = executor.get_execution_status(execution_id)
            if status:
                print(f"   Status: {status.get('status', 'unknown')}")
                print(f"   Progress: {status.get('progress_percentage', 0)}%")
                print(f"   Steps completed: {status.get('completed_steps', 0)}/{status.get('total_steps', 0)}")
            
            await asyncio.sleep(1)
        
        # Get execution logs
        logs = await executor.get_execution_logs(execution_id=execution_id, limit=10)
        print(f"\n📝 Recent logs ({len(logs)} entries):")
        for log in logs[:3]:  # Show first 3 logs
            print(f"   {log.get('timestamp', '')}: {log.get('message', '')}")
        
        print("\n🎉 Email automation workflow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_automation())
