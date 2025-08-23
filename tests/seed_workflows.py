#!/usr/bin/env python3
"""
Seed script to populate the database with sample workflows for testing and visualization
"""
import asyncio
import json
from datetime import datetime

import requests
from motor.motor_asyncio import AsyncIOMotorClient

BASE_URL = "http://localhost:8004/api/v1"

# Sample workflows with different complexities
SAMPLE_WORKFLOWS = [
    {
        "name": "Email Marketing Campaign",
        "description": "Automated email marketing workflow that sends personalized emails based on user behavior",
        "steps": [
            {
                "step_id": "fetch_users",
                "name": "Fetch Target Users",
                "step_type": "database",
                "description": "Get users who haven't opened emails in 30 days",
                "config": {
                    "query": "SELECT * FROM users WHERE last_email_opened < NOW() - INTERVAL 30 DAY",
                    "database": "marketing_db"
                },
                "depends_on": []
            },
            {
                "step_id": "segment_users",
                "name": "Segment Users",
                "step_type": "data_transform",
                "description": "Segment users based on their preferences and behavior",
                "config": {
                    "segmentation_rules": [
                        {"field": "age", "operator": ">", "value": 25, "segment": "adult"},
                        {"field": "purchase_history", "operator": ">", "value": 0, "segment": "customer"}
                    ]
                },
                "depends_on": ["fetch_users"]
            },
            {
                "step_id": "generate_content",
                "name": "Generate Personalized Content",
                "step_type": "llm_process",
                "description": "Use AI to generate personalized email content for each segment",
                "config": {
                    "prompt_template": "Create a personalized email for a {segment} user interested in {interests}",
                    "model": "gpt-4",
                    "max_tokens": 500
                },
                "depends_on": ["segment_users"]
            },
            {
                "step_id": "send_emails",
                "name": "Send Emails",
                "step_type": "email",
                "description": "Send personalized emails to users",
                "config": {
                    "email_service": "sendgrid",
                    "from_email": "noreply@company.com",
                    "subject_template": "We miss you, {first_name}!"
                },
                "depends_on": ["generate_content"]
            },
            {
                "step_id": "track_metrics",
                "name": "Track Email Metrics",
                "step_type": "api_call",
                "description": "Track email open rates and click-through rates",
                "config": {
                    "url": "https://api.analytics.com/track",
                    "method": "POST",
                    "headers": {"Authorization": "Bearer {api_key}"}
                },
                "depends_on": ["send_emails"]
            }
        ],
        "tags": ["marketing", "email", "automation", "ai"],
        "parallel_execution": False,
        "timeout_minutes": 60
    },
    {
        "name": "Data Processing Pipeline",
        "description": "Process and analyze large datasets with parallel processing and error handling",
        "steps": [
            {
                "step_id": "validate_input",
                "name": "Validate Input Data",
                "step_type": "data_transform",
                "description": "Validate incoming data format and quality",
                "config": {
                    "validation_rules": [
                        {"field": "timestamp", "type": "datetime", "required": True},
                        {"field": "user_id", "type": "string", "required": True},
                        {"field": "amount", "type": "number", "min": 0}
                    ]
                },
                "depends_on": []
            },
            {
                "step_id": "clean_data",
                "name": "Clean and Normalize Data",
                "step_type": "data_transform",
                "description": "Remove duplicates and normalize data formats",
                "config": {
                    "operations": [
                        {"type": "remove_duplicates", "fields": ["user_id", "timestamp"]},
                        {"type": "normalize_currency", "field": "amount"},
                        {"type": "standardize_dates", "field": "timestamp"}
                    ]
                },
                "depends_on": ["validate_input"]
            },
            {
                "step_id": "parallel_analysis_1",
                "name": "Calculate User Metrics",
                "step_type": "data_transform",
                "description": "Calculate user-specific metrics",
                "config": {
                    "metrics": ["total_spent", "avg_transaction", "frequency"]
                },
                "depends_on": ["clean_data"]
            },
            {
                "step_id": "parallel_analysis_2",
                "name": "Generate Time Series",
                "step_type": "data_transform",
                "description": "Create time-based analytics",
                "config": {
                    "time_buckets": ["hourly", "daily", "weekly"]
                },
                "depends_on": ["clean_data"]
            },
            {
                "step_id": "parallel_analysis_3",
                "name": "Detect Anomalies",
                "step_type": "llm_process",
                "description": "Use ML to detect unusual patterns",
                "config": {
                    "model": "anomaly_detector_v2",
                    "threshold": 0.95
                },
                "depends_on": ["clean_data"]
            },
            {
                "step_id": "merge_results",
                "name": "Merge Analysis Results",
                "step_type": "data_transform",
                "description": "Combine results from parallel analysis steps",
                "config": {
                    "merge_strategy": "outer_join",
                    "join_key": "user_id"
                },
                "depends_on": ["parallel_analysis_1", "parallel_analysis_2", "parallel_analysis_3"]
            },
            {
                "step_id": "generate_report",
                "name": "Generate Analysis Report",
                "step_type": "file_operation",
                "description": "Create a comprehensive analysis report",
                "config": {
                    "output_format": "pdf",
                    "template": "analytics_report_template.html",
                    "include_charts": True
                },
                "depends_on": ["merge_results"]
            },
            {
                "step_id": "notify_completion",
                "name": "Send Completion Notification",
                "step_type": "email",
                "description": "Notify stakeholders that analysis is complete",
                "config": {
                    "recipients": ["analyst@company.com", "manager@company.com"],
                    "subject": "Data Analysis Pipeline Completed",
                    "attach_report": True
                },
                "depends_on": ["generate_report"]
            }
        ],
        "tags": ["data", "analytics", "pipeline", "parallel"],
        "parallel_execution": True,
        "timeout_minutes": 120
    },
    {
        "name": "Customer Onboarding Flow",
        "description": "Automated customer onboarding with manual approval steps and follow-ups",
        "steps": [
            {
                "step_id": "receive_application",
                "name": "Receive Customer Application",
                "step_type": "api_call",
                "description": "Webhook endpoint to receive new customer applications",
                "config": {
                    "webhook_url": "/webhooks/customer-application",
                    "validation_schema": "customer_application.json"
                },
                "depends_on": []
            },
            {
                "step_id": "verify_identity",
                "name": "Verify Customer Identity",
                "step_type": "api_call",
                "description": "Use third-party service to verify customer identity",
                "config": {
                    "url": "https://api.identity-verification.com/verify",
                    "method": "POST",
                    "required_documents": ["passport", "driver_license"]
                },
                "depends_on": ["receive_application"]
            },
            {
                "step_id": "risk_assessment",
                "name": "Automated Risk Assessment",
                "step_type": "llm_process",
                "description": "AI-powered risk assessment based on application data",
                "config": {
                    "model": "risk_assessment_v3",
                    "factors": ["credit_score", "income", "employment_status"],
                    "risk_threshold": 0.7
                },
                "depends_on": ["verify_identity"]
            },
            {
                "step_id": "manual_review",
                "name": "Manual Review (High Risk)",
                "step_type": "manual",
                "description": "Manual review required for high-risk applications",
                "config": {
                    "assignee_role": "senior_underwriter",
                    "max_review_time_hours": 24,
                    "review_criteria": ["documentation_quality", "risk_factors"]
                },
                "condition": {
                    "field": "risk_score",
                    "operator": ">",
                    "value": 0.7
                },
                "depends_on": ["risk_assessment"]
            },
            {
                "step_id": "approve_application",
                "name": "Approve Application",
                "step_type": "condition",
                "description": "Approve or reject based on risk assessment and manual review",
                "config": {
                    "approval_logic": {
                        "auto_approve": {"risk_score": {"<": 0.3}},
                        "manual_approve": {"manual_review_status": "approved"},
                        "reject": {"risk_score": {">": 0.9}}
                    }
                },
                "depends_on": ["risk_assessment", "manual_review"]
            },
            {
                "step_id": "send_welcome_email",
                "name": "Send Welcome Email",
                "step_type": "email",
                "description": "Send welcome email with account details",
                "config": {
                    "template": "welcome_email.html",
                    "include_attachments": ["terms_of_service.pdf", "getting_started_guide.pdf"]
                },
                "condition": {
                    "field": "application_status",
                    "operator": "==",
                    "value": "approved"
                },
                "depends_on": ["approve_application"]
            },
            {
                "step_id": "setup_account",
                "name": "Setup Customer Account",
                "step_type": "api_call",
                "description": "Create customer account in the system",
                "config": {
                    "url": "https://api.internal.com/customers",
                    "method": "POST",
                    "account_type": "standard"
                },
                "condition": {
                    "field": "application_status",
                    "operator": "==",
                    "value": "approved"
                },
                "depends_on": ["approve_application"]
            },
            {
                "step_id": "schedule_followup",
                "name": "Schedule Follow-up",
                "step_type": "api_call",
                "description": "Schedule follow-up call with customer success team",
                "config": {
                    "url": "https://api.calendar.com/schedule",
                    "days_after_approval": 3,
                    "meeting_duration": 30
                },
                "depends_on": ["send_welcome_email", "setup_account"]
            }
        ],
        "tags": ["onboarding", "customers", "manual", "approval"],
        "parallel_execution": False,
        "timeout_minutes": 1440  # 24 hours
    }
]

async def seed_workflows_via_api():
    """Seed workflows using the REST API"""
    print("🌱 Seeding workflows via API...")
    
    for i, workflow_data in enumerate(SAMPLE_WORKFLOWS, 1):
        print(f"\n{i}. Creating workflow: {workflow_data['name']}")
        
        try:
            response = requests.post(f"{BASE_URL}/workflows", json=workflow_data)
            
            if response.status_code == 201:
                workflow = response.json()
                print(f"   ✅ Created workflow: {workflow['workflow_id']}")
                print(f"   📝 Steps: {len(workflow['steps'])}")
                print(f"   🏷️  Tags: {', '.join(workflow['tags'])}")
            else:
                print(f"   ❌ Failed to create workflow: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error creating workflow: {str(e)}")
    
    print(f"\n🎉 Seeding completed! Created {len(SAMPLE_WORKFLOWS)} workflows.")

async def seed_workflows_direct():
    """Seed workflows directly to MongoDB (alternative method)"""
    print("🌱 Seeding workflows directly to MongoDB...")
    
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.workflow_generator
    collection = db.workflows
    
    for i, workflow_data in enumerate(SAMPLE_WORKFLOWS, 1):
        print(f"\n{i}. Creating workflow: {workflow_data['name']}")
        
        # Add required fields
        import uuid
        workflow_data.update({
            "workflow_id": str(uuid.uuid4()),
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": "seed_script"
        })
        
        try:
            result = await collection.insert_one(workflow_data)
            print(f"   ✅ Created workflow: {workflow_data['workflow_id']}")
            print(f"   📝 Steps: {len(workflow_data['steps'])}")
            print(f"   🏷️  Tags: {', '.join(workflow_data['tags'])}")
        except Exception as e:
            print(f"   ❌ Error creating workflow: {str(e)}")
    
    await client.close()
    print(f"\n🎉 Seeding completed! Created {len(SAMPLE_WORKFLOWS)} workflows.")

def test_api_connection():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/health")
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
                print(f"  - {workflow['name']} ({workflow['workflow_id']})")
                print(f"    Steps: {len(workflow['steps'])}, Tags: {', '.join(workflow['tags'])}")
        else:
            print(f"❌ Failed to list workflows: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing workflows: {str(e)}")

async def main():
    print("🚀 Workflow Seeding Script")
    print("=" * 50)
    
    # Test API connection first
    if test_api_connection():
        # List existing workflows
        list_existing_workflows()
        
        # Ask user for confirmation
        confirm = input("\n🤔 Do you want to seed sample workflows? (y/n): ").lower().strip()
        if confirm == 'y':
            await seed_workflows_via_api()
            
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
