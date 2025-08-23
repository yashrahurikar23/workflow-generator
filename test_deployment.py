#!/usr/bin/env python3
"""
Quick test script to check if the Render deployment is working
"""
import json
from datetime import datetime

import requests


def test_render_deployment():
    """Test if the Render deployment is live"""
    
    # Replace with your actual Render URL once deployed
    render_urls = [
        "https://workflow-backend.onrender.com",  # Expected URL pattern
        "https://workflow-backend-xyz.onrender.com",  # Alternative pattern
    ]
    
    print("🚀 Testing Render Deployment Status...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    for url in render_urls:
        print(f"\n📡 Testing: {url}")
        
        try:
            # Test health endpoint
            response = requests.get(f"{url}/health", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Health check: SUCCESS")
                print(f"   Response: {response.json()}")
                
                # Test API endpoints
                try:
                    workflows_response = requests.get(f"{url}/api/v1/workflows/", timeout=10)
                    if workflows_response.status_code == 200:
                        print(f"✅ Workflows API: SUCCESS")
                        workflows = workflows_response.json()
                        print(f"   Found {len(workflows.get('workflows', []))} workflows")
                    else:
                        print(f"⚠️  Workflows API: {workflows_response.status_code}")
                except Exception as e:
                    print(f"⚠️  Workflows API error: {e}")
                
                print(f"\n🎉 DEPLOYMENT IS LIVE!")
                print(f"🔗 Your API URL: {url}")
                print(f"📖 API Docs: {url}/docs")
                return url
                
            else:
                print(f"❌ Health check failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed: Service not reachable")
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout: Service might be sleeping (free tier)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 Instructions:")
    print(f"1. Check your Render dashboard for the actual URL")
    print(f"2. If using free tier, the service may take 30-60s to wake up")
    print(f"3. Update frontend API URLs once you have the correct endpoint")
    
    return None

def test_local_backend():
    """Test if local backend is running"""
    print("\n🏠 Testing Local Backend...")
    
    local_urls = [
        "http://localhost:8004",
        "http://localhost:8003", 
        "http://localhost:8000"
    ]
    
    for url in local_urls:
        try:
            response = requests.get(f"{url}/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ Local backend running at: {url}")
                return url
        except:
            continue
    
    print("❌ No local backend found")
    return None

def main():
    print("🔍 WORKFLOW GENERATOR - DEPLOYMENT TEST")
    print("=" * 50)
    
    # Test Render deployment
    render_url = test_render_deployment()
    
    # Test local backend
    local_url = test_local_backend()
    
    print("\n📝 SUMMARY")
    print("-" * 20)
    if render_url:
        print(f"✅ Render: {render_url}")
    else:
        print("❌ Render: Not accessible")
    
    if local_url:
        print(f"✅ Local: {local_url}")
    else:
        print("❌ Local: Not running")
    
    print("\n🔧 NEXT STEPS:")
    if render_url:
        print("1. ✅ Backend deployed successfully!")
        print("2. 🚀 Update frontend to use the Render URL")
        print("3. 🎯 Deploy frontend to Vercel/Netlify")
        print("4. 🧪 Test the complete workflow creation and execution")
    else:
        print("1. 📋 Check Render dashboard for deployment status")
        print("2. 🔍 Look for build logs and error messages")
        print("3. ⏳ Wait for deployment to complete (can take 5-10 minutes)")
        print("4. 🔄 Retry this test once deployment is ready")

if __name__ == "__main__":
    main()
