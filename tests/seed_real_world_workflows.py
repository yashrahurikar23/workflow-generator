#!/usr/bin/env python3
"""
Enhanced seed script with three real-world useful workflows
"""
import asyncio
import json
import uuid
from datetime import datetime

import requests
from motor.motor_asyncio import AsyncIOMotorClient

BASE_URL = "http://localhost:8004/api/v1"

# Three Real-World Useful Workflows
REAL_WORLD_WORKFLOWS = [
    {
        "name": "Customer Support Automation Pipeline",
        "description": "Automatically process customer support emails, categorize them, route to appropriate agents, and generate initial responses",
        "workflow_type": "visual",
        "tags": ["customer-support", "automation", "email", "ai"],
        "visual_data": {
            "nodes": [
                {
                    "node_id": "email_trigger",
                    "node_type_id": "webhook_trigger",
                    "name": "Email Trigger",
                    "description": "Monitors support inbox for new emails",
                    "position": {"x": 100, "y": 100},
                    "config": {
                        "method": "POST",
                        "path": "/support-email",
                        "authentication": "api_key"
                    }
                },
                {
                    "node_id": "text_analysis",
                    "node_type_id": "text_analysis",
                    "name": "Analyze Email Content",
                    "description": "Extract sentiment, urgency, and category from email",
                    "position": {"x": 300, "y": 100},
                    "config": {
                        "analysis_type": "all",
                        "language": "auto"
                    }
                },
                {
                    "node_id": "ai_classification",
                    "node_type_id": "ai_model",
                    "name": "AI Classification",
                    "description": "Categorize the issue using AI",
                    "position": {"x": 500, "y": 100},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "temperature": 0.3,
                        "max_tokens": 200,
                        "system_prompt": "Classify this customer support email into one of these categories: billing, technical, general. Also determine urgency level: high, medium, low."
                    }
                },
                {
                    "node_id": "priority_router",
                    "node_type_id": "condition",
                    "name": "Priority Router",
                    "description": "Route based on urgency level",
                    "position": {"x": 700, "y": 100},
                    "config": {
                        "operator": "equals",
                        "compare_value": "high"
                    }
                },
                {
                    "node_id": "auto_response",
                    "node_type_id": "ai_model",
                    "name": "Generate Auto Response",
                    "description": "Generate acknowledgment email",
                    "position": {"x": 900, "y": 200},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 300,
                        "system_prompt": "Generate a professional acknowledgment email for this customer support request. Be empathetic and helpful."
                    }
                },
                {
                    "node_id": "slack_notification",
                    "node_type_id": "http_request",
                    "name": "Slack Notification",
                    "description": "Notify team in Slack",
                    "position": {"x": 900, "y": 50},
                    "config": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 10
                    }
                },
                {
                    "node_id": "crm_update",
                    "node_type_id": "http_request",
                    "name": "Update CRM",
                    "description": "Create/update customer record",
                    "position": {"x": 1100, "y": 100},
                    "config": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 15
                    }
                }
            ],
            "connections": [
                {
                    "id": "conn1",
                    "source_node_id": "email_trigger",
                    "source_handle": "payload",
                    "target_node_id": "text_analysis",
                    "target_handle": "text"
                },
                {
                    "id": "conn2",
                    "source_node_id": "text_analysis",
                    "source_handle": "sentiment",
                    "target_node_id": "ai_classification",
                    "target_handle": "context"
                },
                {
                    "id": "conn3",
                    "source_node_id": "ai_classification",
                    "source_handle": "response",
                    "target_node_id": "priority_router",
                    "target_handle": "value"
                },
                {
                    "id": "conn4",
                    "source_node_id": "priority_router",
                    "source_handle": "true",
                    "target_node_id": "slack_notification",
                    "target_handle": "body"
                },
                {
                    "id": "conn5",
                    "source_node_id": "priority_router",
                    "source_handle": "false",
                    "target_node_id": "auto_response",
                    "target_handle": "prompt"
                },
                {
                    "id": "conn6",
                    "source_node_id": "auto_response",
                    "source_handle": "response",
                    "target_node_id": "crm_update",
                    "target_handle": "body"
                },
                {
                    "id": "conn7",
                    "source_node_id": "slack_notification",
                    "source_handle": "response",
                    "target_node_id": "crm_update",
                    "target_handle": "body"
                }
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "settings": {"auto_save": True}
        },
        "parallel_execution": True,
        "timeout_minutes": 30,
        "is_template": False
    },
    {
        "name": "Content Creation & Publishing Workflow",
        "description": "Streamline content creation from research to publication across multiple platforms",
        "workflow_type": "visual",
        "tags": ["content", "publishing", "social-media", "automation", "seo"],
        "visual_data": {
            "nodes": [
                {
                    "node_id": "schedule_trigger",
                    "node_type_id": "schedule_trigger",
                    "name": "Content Schedule",
                    "description": "Daily content creation trigger",
                    "position": {"x": 100, "y": 200},
                    "config": {
                        "schedule_type": "cron",
                        "cron_expression": "0 9 * * *",
                        "timezone": "UTC"
                    }
                },
                {
                    "node_id": "topic_research",
                    "node_type_id": "ai_model",
                    "name": "Topic Research",
                    "description": "Generate content topics and research",
                    "position": {"x": 300, "y": 200},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "temperature": 0.8,
                        "max_tokens": 500,
                        "system_prompt": "Generate trending content topics for a tech blog. Provide 3 topic ideas with brief research points for each."
                    }
                },
                {
                    "node_id": "content_planner",
                    "node_type_id": "ai_model",
                    "name": "Content Planning",
                    "description": "Create content outline and structure",
                    "position": {"x": 500, "y": 200},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "temperature": 0.6,
                        "max_tokens": 800,
                        "system_prompt": "Create a detailed content outline with introduction, main points, and conclusion for the given topic."
                    }
                },
                {
                    "node_id": "content_writer",
                    "node_type_id": "ai_model",
                    "name": "AI Content Writer",
                    "description": "Generate draft content",
                    "position": {"x": 700, "y": 200},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "system_prompt": "Write a comprehensive blog post based on the provided outline. Make it engaging, informative, and SEO-friendly."
                    }
                },
                {
                    "node_id": "seo_optimizer",
                    "node_type_id": "text_analysis",
                    "name": "SEO Optimization",
                    "description": "Optimize content for search engines",
                    "position": {"x": 900, "y": 150},
                    "config": {
                        "analysis_type": "keywords",
                        "language": "en"
                    }
                },
                {
                    "node_id": "social_formatter",
                    "node_type_id": "data_transform",
                    "name": "Social Media Formatter",
                    "description": "Format content for different platforms",
                    "position": {"x": 900, "y": 250},
                    "config": {
                        "operation": "map",
                        "expression": "format_for_social_media",
                        "output_format": "json"
                    }
                },
                {
                    "node_id": "publish_blog",
                    "node_type_id": "http_request",
                    "name": "Publish to Blog",
                    "description": "Publish to WordPress/CMS",
                    "position": {"x": 1100, "y": 150},
                    "config": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 30
                    }
                },
                {
                    "node_id": "social_scheduler",
                    "node_type_id": "http_request",
                    "name": "Schedule Social Posts",
                    "description": "Schedule posts across platforms",
                    "position": {"x": 1100, "y": 250},
                    "config": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 20
                    }
                }
            ],
            "connections": [
                {
                    "id": "conn1",
                    "source_node_id": "schedule_trigger",
                    "source_handle": "timestamp",
                    "target_node_id": "topic_research",
                    "target_handle": "prompt"
                },
                {
                    "id": "conn2",
                    "source_node_id": "topic_research",
                    "source_handle": "response",
                    "target_node_id": "content_planner",
                    "target_handle": "prompt"
                },
                {
                    "id": "conn3",
                    "source_node_id": "content_planner",
                    "source_handle": "response",
                    "target_node_id": "content_writer",
                    "target_handle": "prompt"
                },
                {
                    "id": "conn4",
                    "source_node_id": "content_writer",
                    "source_handle": "response",
                    "target_node_id": "seo_optimizer",
                    "target_handle": "text"
                },
                {
                    "id": "conn5",
                    "source_node_id": "content_writer",
                    "source_handle": "response",
                    "target_node_id": "social_formatter",
                    "target_handle": "data"
                },
                {
                    "id": "conn6",
                    "source_node_id": "seo_optimizer",
                    "source_handle": "keywords",
                    "target_node_id": "publish_blog",
                    "target_handle": "body"
                },
                {
                    "id": "conn7",
                    "source_node_id": "social_formatter",
                    "source_handle": "transformed_data",
                    "target_node_id": "social_scheduler",
                    "target_handle": "body"
                }
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "settings": {"auto_save": True}
        },
        "parallel_execution": True,
        "timeout_minutes": 45,
        "is_template": True
    },
    {
        "name": "E-commerce Order Processing & Fulfillment",
        "description": "Automate the entire order lifecycle from payment to delivery tracking",
        "workflow_type": "visual",
        "tags": ["ecommerce", "order-processing", "fulfillment", "automation"],
        "visual_data": {
            "nodes": [
                {
                    "node_id": "order_webhook",
                    "node_type_id": "webhook_trigger",
                    "name": "New Order Webhook",
                    "description": "Receives new order notifications",
                    "position": {"x": 100, "y": 300},
                    "config": {
                        "method": "POST",
                        "path": "/new-order",
                        "authentication": "bearer_token"
                    }
                },
                {
                    "node_id": "payment_verification",
                    "node_type_id": "http_request",
                    "name": "Payment Verification",
                    "description": "Verify payment status",
                    "position": {"x": 300, "y": 300},
                    "config": {
                        "method": "GET",
                        "headers": {"Authorization": "Bearer token"},
                        "timeout": 10
                    }
                },
                {
                    "node_id": "inventory_check",
                    "node_type_id": "http_request",
                    "name": "Inventory Check",
                    "description": "Verify product availability",
                    "position": {"x": 500, "y": 300},
                    "config": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 15
                    }
                },
                {
                    "node_id": "fraud_detection",
                    "node_type_id": "ai_model",
                    "name": "Fraud Detection",
                    "description": "AI-powered fraud analysis",
                    "position": {"x": 500, "y": 200},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "temperature": 0.1,
                        "max_tokens": 100,
                        "system_prompt": "Analyze this order data for potential fraud indicators. Consider unusual patterns, shipping vs billing address, order value, etc."
                    }
                },
                {
                    "node_id": "order_router",
                    "node_type_id": "condition",
                    "name": "Order Routing",
                    "description": "Route to appropriate warehouse",
                    "position": {"x": 700, "y": 300},
                    "config": {
                        "operator": "equals",
                        "compare_value": "approved"
                    }
                },
                {
                    "node_id": "shipping_calculator",
                    "node_type_id": "ai_model",
                    "name": "Shipping Calculator",
                    "description": "Calculate optimal shipping method",
                    "position": {"x": 900, "y": 300},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.3,
                        "max_tokens": 200,
                        "system_prompt": "Calculate the best shipping method considering cost, speed, and customer preferences."
                    }
                },
                {
                    "node_id": "label_generation",
                    "node_type_id": "http_request",
                    "name": "Generate Shipping Label",
                    "description": "Create shipping labels automatically",
                    "position": {"x": 1100, "y": 250},
                    "config": {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 20
                    }
                },
                {
                    "node_id": "inventory_update",
                    "node_type_id": "http_request",
                    "name": "Update Inventory",
                    "description": "Update stock levels",
                    "position": {"x": 1100, "y": 350},
                    "config": {
                        "method": "PUT",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 10
                    }
                },
                {
                    "node_id": "customer_notification",
                    "node_type_id": "ai_model",
                    "name": "Customer Notification",
                    "description": "Send order confirmation & tracking",
                    "position": {"x": 1300, "y": 300},
                    "config": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.5,
                        "max_tokens": 400,
                        "system_prompt": "Generate a friendly order confirmation email with tracking information and delivery estimate."
                    }
                }
            ],
            "connections": [
                {
                    "id": "conn1",
                    "source_node_id": "order_webhook",
                    "source_handle": "payload",
                    "target_node_id": "payment_verification",
                    "target_handle": "url"
                },
                {
                    "id": "conn2",
                    "source_node_id": "order_webhook",
                    "source_handle": "payload",
                    "target_node_id": "fraud_detection",
                    "target_handle": "prompt"
                },
                {
                    "id": "conn3",
                    "source_node_id": "payment_verification",
                    "source_handle": "response",
                    "target_node_id": "inventory_check",
                    "target_handle": "body"
                },
                {
                    "id": "conn4",
                    "source_node_id": "inventory_check",
                    "source_handle": "response",
                    "target_node_id": "order_router",
                    "target_handle": "value"
                },
                {
                    "id": "conn5",
                    "source_node_id": "fraud_detection",
                    "source_handle": "response",
                    "target_node_id": "order_router",
                    "target_handle": "value"
                },
                {
                    "id": "conn6",
                    "source_node_id": "order_router",
                    "source_handle": "true",
                    "target_node_id": "shipping_calculator",
                    "target_handle": "prompt"
                },
                {
                    "id": "conn7",
                    "source_node_id": "shipping_calculator",
                    "source_handle": "response",
                    "target_node_id": "label_generation",
                    "target_handle": "body"
                },
                {
                    "id": "conn8",
                    "source_node_id": "shipping_calculator",
                    "source_handle": "response",
                    "target_node_id": "inventory_update",
                    "target_handle": "body"
                },
                {
                    "id": "conn9",
                    "source_node_id": "label_generation",
                    "source_handle": "response",
                    "target_node_id": "customer_notification",
                    "target_handle": "context"
                },
                {
                    "id": "conn10",
                    "source_node_id": "inventory_update",
                    "source_handle": "response",
                    "target_node_id": "customer_notification",
                    "target_handle": "context"
                }
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "settings": {"auto_save": True}
        },
        "parallel_execution": True,
        "timeout_minutes": 60,
        "is_template": True
    }
]

async def seed_real_world_workflows():
    """Seed the three real-world workflows via API"""
    print("🌱 Seeding Real-World Workflows...")
    
    for i, workflow_data in enumerate(REAL_WORLD_WORKFLOWS, 1):
        print(f"\n{i}. Creating workflow: {workflow_data['name']}")
        
        try:
            response = requests.post(f"{BASE_URL}/visual/visual-workflows", json=workflow_data)
            
            if response.status_code == 200:
                workflow = response.json()
                print(f"   ✅ Created visual workflow: {workflow['workflow_id']}")
                print(f"   📊 Nodes: {len(workflow['visual_data']['nodes'])}")
                print(f"   🔗 Connections: {len(workflow['visual_data']['connections'])}")
                print(f"   🏷️  Tags: {', '.join(workflow['tags'])}")
            else:
                print(f"   ❌ Failed to create workflow: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error creating workflow: {str(e)}")
    
    print(f"\n🎉 Real-world workflow seeding completed!")

async def seed_workflows_direct():
    """Seed workflows directly to MongoDB (for visual workflows)"""
    print("🌱 Seeding Real-World Workflows directly to MongoDB...")
    
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.workflow_generator
    collection = db.workflows
    
    for i, workflow_data in enumerate(REAL_WORLD_WORKFLOWS, 1):
        print(f"\n{i}. Creating workflow: {workflow_data['name']}")
        
        # Add required fields
        workflow_data.update({
            "workflow_id": str(uuid.uuid4()),
            "status": "active",
            "execution_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": "seed_script"
        })
        
        try:
            result = await collection.insert_one(workflow_data)
            print(f"   ✅ Created visual workflow: {workflow_data['workflow_id']}")
            print(f"   📊 Nodes: {len(workflow_data['visual_data']['nodes'])}")
            print(f"   🔗 Connections: {len(workflow_data['visual_data']['connections'])}")
            print(f"   🏷️  Tags: {', '.join(workflow_data['tags'])}")
        except Exception as e:
            print(f"   ❌ Error creating workflow: {str(e)}")
    
    await client.close()
    print(f"\n🎉 Real-world workflow seeding completed!")

def test_api_connection():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"http://localhost:8004/health")
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        return False

def list_existing_workflows():
    """List existing workflows in the system"""
    print("\n📋 Listing existing workflows...")
    
    try:
        response = requests.get(f"{BASE_URL}/workflows")
        if response.status_code == 200:
            workflows = response.json()
            print(f"Found {len(workflows)} existing workflows:")
            
            for workflow in workflows:
                workflow_type = workflow.get('workflow_type', 'legacy')
                node_count = 0
                if workflow_type == 'visual' and 'visual_data' in workflow:
                    node_count = len(workflow['visual_data'].get('nodes', []))
                
                print(f"  - {workflow['name']} ({workflow['workflow_id']})")
                print(f"    Type: {workflow_type}, Nodes: {node_count}, Tags: {', '.join(workflow.get('tags', []))}")
        else:
            print(f"❌ Failed to list workflows: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing workflows: {str(e)}")

async def main():
    print("🚀 Real-World Workflow Seeding Script")
    print("=" * 50)
    
    # Test API connection first
    if test_api_connection():
        # List existing workflows
        list_existing_workflows()
        
        # Ask user for confirmation
        confirm = input("\n🤔 Do you want to seed the 3 real-world workflows? (y/n): ").lower().strip()
        if confirm == 'y':
            await seed_real_world_workflows()
            
            # List workflows after seeding
            print("\n" + "=" * 50)
            list_existing_workflows()
        else:
            print("❌ Seeding cancelled by user")
    else:
        print("\n🔄 Trying direct MongoDB connection...")
        try:
            await seed_workflows_direct()
        except Exception as e:
            print(f"❌ Direct MongoDB seeding failed: {str(e)}")
            print("\n💡 Make sure MongoDB is running and the API server is started")

if __name__ == "__main__":
    asyncio.run(main())
