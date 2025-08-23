#!/usr/bin/env python3
"""
Test runner for chat and thread API tests
"""
import os
import subprocess
import sys
from pathlib import Path


def run_test_suite():
    """Run the complete test suite for chat and thread APIs"""
    
    print("🧪 CHAT & THREAD API TEST SUITE")
    print("=" * 50)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Test configurations
    test_configs = [
        {
            "name": "Unit Tests - Chat Models",
            "command": ["python", "-m", "pytest", "tests/test_chat_models.py", "-v"],
            "description": "Testing chat data models and validation"
        },
        {
            "name": "Unit Tests - Chat CRUD",
            "command": ["python", "-m", "pytest", "tests/test_chat_crud.py", "-v"],
            "description": "Testing chat database operations"
        },
        {
            "name": "Integration Tests - Chat API",
            "command": ["python", "-m", "pytest", "tests/test_chat_api_integration.py", "-v"],
            "description": "Testing chat API endpoints"
        },
        {
            "name": "End-to-End Tests - Chat System",
            "command": ["python", "-m", "pytest", "tests/test_chat_e2e.py", "-v", "-s"],
            "description": "Testing complete chat system workflows"
        }
    ]
    
    results = {}
    
    for config in test_configs:
        print(f"\n🔍 {config['name']}")
        print(f"📄 {config['description']}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                config["command"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout per test suite
            )
            
            if result.returncode == 0:
                print(f"✅ {config['name']}: PASSED")
                results[config['name']] = "PASSED"
            else:
                print(f"❌ {config['name']}: FAILED")
                print(f"Error output: {result.stderr}")
                results[config['name']] = "FAILED"
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {config['name']}: TIMEOUT")
            results[config['name']] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {config['name']}: ERROR - {e}")
            results[config['name']] = "ERROR"
    
    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    passed = sum(1 for r in results.values() if r == "PASSED")
    total = len(results)
    
    for test_name, result in results.items():
        status_emoji = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "TIMEOUT": "⏰",
            "ERROR": "💥"
        }.get(result, "❓")
        
        print(f"{status_emoji} {test_name}: {result}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} test suite(s) failed!")
        return 1


def check_backend_status():
    """Check if backend is running before running tests"""
    print("🔍 Checking backend status...")
    
    try:
        import requests
        response = requests.get("http://localhost:8004/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"⚠️  Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        print("\n💡 To start the backend:")
        print("cd backend && uvicorn main:app --host 0.0.0.0 --port 8004")
        return False


def install_test_dependencies():
    """Install required test dependencies"""
    print("📦 Installing test dependencies...")
    
    dependencies = [
        "pytest",
        "pytest-asyncio", 
        "httpx",
        "pytest-mock"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
            return False
    
    print("✅ Test dependencies installed")
    return True


if __name__ == "__main__":
    print("🚀 STARTING CHAT API TEST SUITE")
    print("=" * 50)
    
    # Install dependencies
    if not install_test_dependencies():
        sys.exit(1)
    
    # Check backend status
    backend_running = check_backend_status()
    
    if not backend_running:
        print("\n⚠️  Backend not running. Some integration tests may fail.")
        print("Continuing with unit tests...")
    
    # Run tests
    exit_code = run_test_suite()
    
    if not backend_running:
        print("\n💡 TIP: Start the backend server for full test coverage:")
        print("cd backend && uvicorn main:app --host 0.0.0.0 --port 8004")
    
    sys.exit(exit_code)
