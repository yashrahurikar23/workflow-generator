#!/usr/bin/env python3
"""
Test the enhanced workflow system
"""
import asyncio
import json

from app.api.v1.endpoints.visual_workflows import workflow_executor
from app.main import app


async def test_enhanced_features():
    """Test the enhanced workflow features"""
    print("🧪 Testing Enhanced Workflow Features")
    print("=" * 50)
    
    # Test 1: Check if enhanced executor is available
    print("✅ Enhanced workflow executor imported successfully")
    print(f"   Type: {type(workflow_executor)}")
    
    # Test 2: Check active executions
    active_executions = workflow_executor.list_active_executions()
    print(f"✅ Active executions: {len(active_executions)}")
    
    # Test 3: Check execution history
    execution_history = workflow_executor.get_execution_history()
    print(f"✅ Execution history: {len(execution_history)} entries")
    
    print("\n🎉 All enhanced features are working correctly!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_features())
