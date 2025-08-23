#!/usr/bin/env python3
"""
Setup script for Customer Support Email Automation workflow
"""
import asyncio
import os
import sys
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def setup_email_automation_workflow():
    """Setup the focused email automation workflow in MongoDB"""
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.workflow_generator
        
        print("🔄 Setting up Customer Support Email Automation workflow...")
        
        # Clear existing workflows
        delete_result = await db.workflows.delete_many({})
        print(f"✅ Cleared {delete_result.deleted_count} existing workflows")
        
        # Customer Support Email Automation Workflow
        email_automation_workflow = {
            'workflow_id': 'email-automation-v1',
            'name': 'Customer Support Email Automation',
            'description': 'Automated email processing with AI-powered classification, routing, and response generation',
            'workflow_type': 'visual',
            'status': 'active',
            'tags': ['email', 'customer-support', 'ai', 'automation'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'execution_count': 0,
            'last_executed_at': None,
            'visual_data': {
                'nodes': [
                    {
                        'node_id': 'email-trigger',
                        'node_type_id': 'email_trigger',
                        'name': 'Email Inbox Monitor',
                        'position': {'x': 100, 'y': 200},
                        'config': {
                            'check_interval': 30,
                            'email_source': 'mock',
                            'filters': {
                                'sender_domains': ['customer.com', 'support.com'],
                                'subject_keywords': ['support', 'help', 'issue', 'problem']
                            }
                        }
                    },
                    {
                        'node_id': 'ai-classifier',
                        'node_type_id': 'ai_model',
                        'name': 'Email Classifier',
                        'position': {'x': 400, 'y': 200},
                        'config': {
                            'provider': 'OpenAI',
                            'model': 'gpt-4',
                            'prompt': '''Analyze this customer email and classify it:
                            
Email: {email_content}

Classify the email and respond in JSON format:
{
  "category": "technical_issue|billing_question|feature_request|complaint|general_inquiry",
  "priority": "urgent|high|medium|low",
  "sentiment": "positive|neutral|negative",
  "requires_human": true|false,
  "estimated_response_time": "immediate|1_hour|4_hours|24_hours",
  "key_topics": ["topic1", "topic2"]
}''',
                            'temperature': 0.1,
                            'response_format': 'json'
                        }
                    },
                    {
                        'node_id': 'priority-router',
                        'node_type_id': 'condition',
                        'name': 'Priority Router',
                        'position': {'x': 700, 'y': 150},
                        'config': {
                            'condition_type': 'json_path',
                            'conditions': [
                                {
                                    'path': '$.priority',
                                    'operator': 'equals',
                                    'value': 'urgent',
                                    'route': 'urgent-handler'
                                },
                                {
                                    'path': '$.requires_human',
                                    'operator': 'equals',
                                    'value': True,
                                    'route': 'human-review'
                                }
                            ],
                            'default_route': 'auto-responder'
                        }
                    },
                    {
                        'node_id': 'urgent-handler',
                        'node_type_id': 'notification',
                        'name': 'Urgent Alert',
                        'position': {'x': 1000, 'y': 100},
                        'config': {
                            'notification_type': 'slack',
                            'channel': '#urgent-support',
                            'message_template': 'URGENT: New support ticket requires immediate attention\\nFrom: {sender}\\nSubject: {subject}\\nPriority: {priority}'
                        }
                    },
                    {
                        'node_id': 'human-review',
                        'node_type_id': 'approval',
                        'name': 'Human Review Queue',
                        'position': {'x': 1000, 'y': 200},
                        'config': {
                            'assignment_strategy': 'round_robin',
                            'escalation_timeout': 240,
                            'reviewers': ['support-team']
                        }
                    },
                    {
                        'node_id': 'auto-responder',
                        'node_type_id': 'ai_model',
                        'name': 'Response Generator',
                        'position': {'x': 1000, 'y': 300},
                        'config': {
                            'provider': 'OpenAI',
                            'model': 'gpt-4',
                            'prompt': '''Generate a helpful, professional response to this customer email:

Original Email: {email_content}
Email Classification: {classification}

Guidelines:
- Be professional and empathetic
- Address the specific issue mentioned
- Provide clear next steps if applicable
- Include relevant links or resources
- Match the tone appropriately

Generate only the response email content.''',
                            'temperature': 0.3
                        }
                    },
                    {
                        'node_id': 'email-sender',
                        'node_type_id': 'email_sender',
                        'name': 'Send Response',
                        'position': {'x': 1300, 'y': 250},
                        'config': {
                            'email_service': 'mock',
                            'from_address': 'support@company.com',
                            'auto_reply': True,
                            'track_opens': True,
                            'save_to_crm': True
                        }
                    },
                    {
                        'node_id': 'analytics-logger',
                        'node_type_id': 'data_logger',
                        'name': 'Analytics Tracker',
                        'position': {'x': 1300, 'y': 400},
                        'config': {
                            'log_destination': 'analytics_db',
                            'metrics': [
                                'response_time',
                                'classification_accuracy',
                                'customer_satisfaction',
                                'resolution_rate'
                            ]
                        }
                    }
                ],
                'connections': [
                    {
                        'connection_id': 'trigger-to-classifier',
                        'source_node_id': 'email-trigger',
                        'target_node_id': 'ai-classifier',
                        'source_output': 'email_data',
                        'target_input': 'email_content'
                    },
                    {
                        'connection_id': 'classifier-to-router',
                        'source_node_id': 'ai-classifier',
                        'target_node_id': 'priority-router',
                        'source_output': 'classification',
                        'target_input': 'data'
                    },
                    {
                        'connection_id': 'router-to-urgent',
                        'source_node_id': 'priority-router',
                        'target_node_id': 'urgent-handler',
                        'source_output': 'urgent-handler',
                        'target_input': 'alert_data'
                    },
                    {
                        'connection_id': 'router-to-human',
                        'source_node_id': 'priority-router',
                        'target_node_id': 'human-review',
                        'source_output': 'human-review',
                        'target_input': 'review_data'
                    },
                    {
                        'connection_id': 'router-to-auto',
                        'source_node_id': 'priority-router',
                        'target_node_id': 'auto-responder',
                        'source_output': 'auto-responder',
                        'target_input': 'email_content'
                    },
                    {
                        'connection_id': 'responder-to-sender',
                        'source_node_id': 'auto-responder',
                        'target_node_id': 'email-sender',
                        'source_output': 'response',
                        'target_input': 'email_content'
                    },
                    {
                        'connection_id': 'sender-to-analytics',
                        'source_node_id': 'email-sender',
                        'target_node_id': 'analytics-logger',
                        'source_output': 'delivery_status',
                        'target_input': 'log_data'
                    }
                ]
            },
            'execution_settings': {
                'max_concurrent_executions': 5,
                'retry_failed_steps': True,
                'max_retries': 3,
                'step_timeout': 300,
                'workflow_timeout': 1800
            }
        }
        
        # Insert the workflow
        result = await db.workflows.insert_one(email_automation_workflow)
        print(f"✅ Created email automation workflow: {result.inserted_id}")
        
        # Verify insertion
        workflow_count = await db.workflows.count_documents({})
        print(f"✅ Total workflows in database: {workflow_count}")
        
        # Print workflow summary
        workflow = await db.workflows.find_one({'workflow_id': 'email-automation-v1'})
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

async def setup_mock_email_data():
    """Setup mock email data for testing"""
    
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.workflow_generator
        
        # Clear existing mock emails
        await db.mock_emails.delete_many({})
        
        # Sample customer emails for testing
        mock_emails = [
            {
                'email_id': 'email-001',
                'sender': 'john.doe@customer.com',
                'recipient': 'support@company.com',
                'subject': 'Urgent: Payment processing issue',
                'content': '''Hello,
                
I'm having trouble processing my payment for order #12345. The system keeps giving me an error message saying "Payment failed" but my credit card is working fine on other sites.

This is quite urgent as I need the items by tomorrow for an important presentation. Can someone please help me resolve this immediately?

Best regards,
John Doe
Customer ID: C123456''',
                'timestamp': datetime.utcnow(),
                'status': 'unprocessed',
                'metadata': {
                    'order_id': '12345',
                    'customer_id': 'C123456',
                    'ip_address': '192.168.1.100',
                    'user_agent': 'Mozilla/5.0...'
                }
            },
            {
                'email_id': 'email-002',
                'sender': 'sarah.smith@example.com',
                'recipient': 'support@company.com',
                'subject': 'Question about premium features',
                'content': '''Hi there,
                
I've been using your basic plan for a few months and I'm really happy with the service. I'm considering upgrading to the premium plan but I have a few questions:

1. What's the difference in storage limits?
2. Are there any additional collaboration features?
3. Is there a discount for annual billing?

Thanks for your time!

Sarah Smith''',
                'timestamp': datetime.utcnow(),
                'status': 'unprocessed',
                'metadata': {
                    'current_plan': 'basic',
                    'account_type': 'individual'
                }
            },
            {
                'email_id': 'email-003',
                'sender': 'mike.wilson@business.com',
                'recipient': 'support@company.com',
                'subject': 'Feature request: API integration',
                'content': '''Hello Support Team,
                
Our development team has been using your platform for our clients and we love it. However, we would really benefit from having API access to integrate directly with our systems.

Specifically, we need:
- REST API for user management
- Webhook notifications for events
- Bulk data import/export capabilities

Is this something that's on your roadmap? Would love to discuss this further.

Best,
Mike Wilson
CTO, Business Solutions Inc.''',
                'timestamp': datetime.utcnow(),
                'status': 'unprocessed',
                'metadata': {
                    'company': 'Business Solutions Inc.',
                    'role': 'CTO',
                    'account_type': 'business'
                }
            }
        ]
        
        # Insert mock emails
        result = await db.mock_emails.insert_many(mock_emails)
        print(f"✅ Created {len(result.inserted_ids)} mock emails for testing")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up mock emails: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Customer Support Email Automation System")
    print("=" * 60)
    
    async def main():
        # Setup workflow
        workflow_success = await setup_email_automation_workflow()
        
        # Setup mock data
        mock_success = await setup_mock_email_data()
        
        if workflow_success and mock_success:
            print("\\n🎉 Setup completed successfully!")
            print("\\nNext steps:")
            print("1. Start the backend server: cd backend && uvicorn app.main:app --reload")
            print("2. Test the workflow: python test_email_automation.py")
            print("3. Start the frontend: cd frontend && npm run dev")
        else:
            print("\\n❌ Setup encountered errors. Please check the logs above.")
    
    asyncio.run(main())
