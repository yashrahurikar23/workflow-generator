"""
Mock Email Service for Testing Customer Support Email Automation
Uses GPT-4 to generate realistic customer emails for testing
"""
import asyncio
import json
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class EmailPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EmailCategory(str, Enum):
    TECHNICAL_ISSUE = "technical_issue"
    BILLING_QUESTION = "billing_question"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    GENERAL_INQUIRY = "general_inquiry"

@dataclass
class MockEmail:
    """Mock email data structure"""
    email_id: str
    sender: str
    recipient: str
    subject: str
    content: str
    timestamp: datetime
    priority: EmailPriority
    category: EmailCategory
    sentiment: str  # positive, neutral, negative
    metadata: Dict[str, Any]

class MockEmailGenerator:
    """Generate realistic customer emails using GPT-4 patterns"""
    
    def __init__(self):
        self.email_templates = self._load_email_templates()
        self.customer_names = [
            "John Smith", "Sarah Johnson", "Mike Wilson", "Emily Brown", 
            "David Lee", "Lisa Davis", "Tom Anderson", "Maria Garcia",
            "James Miller", "Jennifer Taylor", "Robert Kim", "Amy Chen"
        ]
        self.companies = [
            "TechCorp", "BusinessSolutions", "StartupInc", "Enterprise Ltd",
            "InnovateNow", "GlobalTech", "SmartSystems", "FutureTech"
        ]
        self.domains = [
            "gmail.com", "hotmail.com", "company.com", "business.org",
            "startup.io", "enterprise.net", "tech.co", "example.com"
        ]
    
    def _load_email_templates(self) -> Dict[EmailCategory, List[Dict[str, Any]]]:
        """Load email templates for different categories"""
        return {
            EmailCategory.TECHNICAL_ISSUE: [
                {
                    "subject_patterns": [
                        "Unable to login to my account",
                        "Error message when trying to {action}",
                        "App keeps crashing on {device}",
                        "Feature not working as expected",
                        "System timeout issues"
                    ],
                    "content_patterns": [
                        "I'm having trouble accessing my account. When I try to login, I get an error message saying '{error}'. This started happening {timeframe}. Can you please help?",
                        "The {feature} feature isn't working properly. Every time I try to {action}, the system {issue}. This is affecting my work significantly.",
                        "I'm experiencing technical difficulties with {component}. The error occurs when {scenario}. My account details are {details}."
                    ],
                    "priority": [EmailPriority.HIGH, EmailPriority.MEDIUM, EmailPriority.URGENT],
                    "sentiment": ["negative", "neutral"],
                    "urgency_keywords": ["urgent", "critical", "asap", "immediately", "broken"]
                }
            ],
            EmailCategory.BILLING_QUESTION: [
                {
                    "subject_patterns": [
                        "Question about my billing statement",
                        "Incorrect charge on my account",
                        "Need invoice for order #{order_id}",
                        "Payment method update",
                        "Refund request for {service}"
                    ],
                    "content_patterns": [
                        "I have a question about my recent billing statement. I noticed a charge for ${amount} on {date} that I don't recognize. Could you please clarify what this is for?",
                        "I need to update my payment method for my subscription. My current card is expiring and I want to ensure there's no interruption in service.",
                        "I would like to request a refund for {service} as {reason}. The transaction ID is {transaction_id}."
                    ],
                    "priority": [EmailPriority.MEDIUM, EmailPriority.LOW],
                    "sentiment": ["neutral", "negative"],
                    "urgency_keywords": ["overdue", "payment", "charge", "refund"]
                }
            ],
            EmailCategory.FEATURE_REQUEST: [
                {
                    "subject_patterns": [
                        "Feature request: {feature}",
                        "Suggestion for improvement",
                        "Would love to see {feature} added",
                        "Enhancement request",
                        "Product feedback and suggestions"
                    ],
                    "content_patterns": [
                        "I've been using your platform for {timeframe} and really enjoy it. I would love to see {feature} added because {reason}. This would really help with {use_case}.",
                        "I have a suggestion that could improve the user experience. Currently, {current_situation}, but it would be great if {proposed_solution}.",
                        "Our team would benefit greatly from having {feature}. We currently use {workaround} but a native solution would be much more efficient."
                    ],
                    "priority": [EmailPriority.LOW, EmailPriority.MEDIUM],
                    "sentiment": ["positive", "neutral"],
                    "urgency_keywords": ["would love", "suggestion", "improvement", "enhancement"]
                }
            ],
            EmailCategory.COMPLAINT: [
                {
                    "subject_patterns": [
                        "Extremely disappointed with {service}",
                        "Poor customer service experience",
                        "Service quality issues",
                        "Complaint about {issue}",
                        "This is unacceptable"
                    ],
                    "content_patterns": [
                        "I am extremely disappointed with the service quality. {specific_issue} has been ongoing for {timeframe} and despite multiple attempts to get help, nothing has been resolved.",
                        "I had a very poor experience with your customer service team. {incident_description}. This is not what I expect from a company of your reputation.",
                        "The recent changes to {service} have made it nearly unusable. {specific_problems}. I'm considering switching to a competitor if this isn't fixed soon."
                    ],
                    "priority": [EmailPriority.HIGH, EmailPriority.URGENT],
                    "sentiment": ["negative"],
                    "urgency_keywords": ["disappointed", "unacceptable", "terrible", "frustrated", "angry"]
                }
            ],
            EmailCategory.GENERAL_INQUIRY: [
                {
                    "subject_patterns": [
                        "Question about {topic}",
                        "General inquiry",
                        "Need information about {service}",
                        "How do I {action}?",
                        "Getting started with {feature}"
                    ],
                    "content_patterns": [
                        "Hello, I'm new to your platform and have a few questions about {topic}. Specifically, I'd like to know {questions}. Thanks for your help!",
                        "I'm interested in learning more about {service}. Could you provide information about {specific_aspects}? I'm particularly interested in {details}.",
                        "Hi, I need some guidance on {topic}. I've tried {attempted_solutions} but I'm still not sure about {confusion}. Any help would be appreciated."
                    ],
                    "priority": [EmailPriority.LOW, EmailPriority.MEDIUM],
                    "sentiment": ["positive", "neutral"],
                    "urgency_keywords": ["question", "inquiry", "information", "help", "guidance"]
                }
            ]
        }
    
    def generate_email(self, category: Optional[EmailCategory] = None, priority: Optional[EmailPriority] = None) -> MockEmail:
        """Generate a realistic customer email"""
        
        # Select category if not provided
        if category is None:
            category = random.choice(list(EmailCategory))
        
        # Get template for category
        template_data = self.email_templates[category][0]
        
        # Generate sender info
        customer_name = random.choice(self.customer_names)
        first_name = customer_name.split()[0].lower()
        last_name = customer_name.split()[1].lower()
        domain = random.choice(self.domains)
        sender_email = f"{first_name}.{last_name}@{domain}"
        
        # Generate subject
        subject_pattern = random.choice(template_data["subject_patterns"])
        subject = self._fill_template(subject_pattern, category)
        
        # Generate content
        content_pattern = random.choice(template_data["content_patterns"])
        content = self._fill_template(content_pattern, category)
        
        # Add signature
        content += f"\\n\\nBest regards,\\n{customer_name}"
        if random.choice([True, False]):
            company = random.choice(self.companies)
            content += f"\\n{company}"
        
        # Determine priority
        if priority is None:
            priority = random.choice(template_data["priority"])
        
        # Determine sentiment
        sentiment = random.choice(template_data["sentiment"])
        
        # Check for urgency keywords to adjust priority
        urgency_keywords = template_data.get("urgency_keywords", [])
        content_lower = content.lower()
        subject_lower = subject.lower()
        
        if any(keyword in content_lower or keyword in subject_lower for keyword in urgency_keywords):
            if priority in [EmailPriority.LOW, EmailPriority.MEDIUM]:
                priority = EmailPriority.HIGH
        
        # Generate metadata
        metadata = {
            "customer_name": customer_name,
            "account_type": random.choice(["free", "premium", "enterprise"]),
            "customer_since": (datetime.now() - timedelta(days=random.randint(30, 1000))).isoformat(),
            "previous_tickets": random.randint(0, 10),
            "satisfaction_score": round(random.uniform(1, 5), 1),
            "preferred_language": "en",
            "timezone": random.choice(["UTC", "EST", "PST", "GMT"]),
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
            "generated_at": datetime.utcnow().isoformat(),
            "template_category": category.value
        }
        
        return MockEmail(
            email_id=f"email-{uuid.uuid4().hex[:8]}",
            sender=sender_email,
            recipient="support@company.com",
            subject=subject,
            content=content,
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(0, 120)),
            priority=priority,
            category=category,
            sentiment=sentiment,
            metadata=metadata
        )
    
    def _fill_template(self, template: str, category: EmailCategory) -> str:
        """Fill template with realistic data"""
        replacements = {
            # Technical terms
            "{action}": random.choice(["upload files", "download report", "save changes", "process payment", "export data"]),
            "{error}": random.choice(["Authentication failed", "Server timeout", "Invalid input", "Access denied", "Connection lost"]),
            "{device}": random.choice(["iPhone", "Android phone", "Windows laptop", "Mac", "iPad"]),
            "{feature}": random.choice(["dashboard", "reporting tool", "mobile app", "API integration", "export function"]),
            "{timeframe}": random.choice(["yesterday", "this morning", "last week", "since the update", "for 3 days"]),
            "{component}": random.choice(["login page", "dashboard", "report generator", "file uploader", "payment system"]),
            "{scenario}": random.choice(["I click save", "the page loads", "I try to export", "uploading files", "processing payment"]),
            "{issue}": random.choice(["crashes", "freezes", "shows an error", "becomes unresponsive", "logs me out"]),
            "{details}": f"user ID: {random.randint(10000, 99999)}",
            
            # Billing terms
            "{amount}": f"{random.randint(10, 500):.2f}",
            "{date}": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%B %d"),
            "{service}": random.choice(["Premium Plan", "Pro Subscription", "Enterprise License", "Add-on Feature"]),
            "{reason}": random.choice(["I'm not satisfied with the service", "it doesn't meet my needs", "I found a better alternative"]),
            "{transaction_id}": f"TXN-{uuid.uuid4().hex[:8].upper()}",
            "{order_id}": f"{random.randint(100000, 999999)}",
            
            # General terms
            "{topic}": random.choice(["pricing", "features", "integration", "setup", "migration", "best practices"]),
            "{questions}": random.choice([
                "how to get started and what features are available",
                "pricing options and what's included in each plan",
                "how to integrate with our existing systems",
                "what support options are available"
            ]),
            "{specific_aspects}": random.choice([
                "pricing and feature comparison",
                "implementation timeline and requirements",
                "training and support options",
                "security and compliance features"
            ]),
            "{attempted_solutions}": random.choice([
                "reading the documentation",
                "searching the help center",
                "watching tutorial videos",
                "asking colleagues"
            ]),
            "{confusion}": random.choice([
                "the setup process",
                "how to configure the settings",
                "which plan is right for me",
                "how to import my data"
            ]),
            
            # Complaint terms
            "{specific_issue}": random.choice([
                "The system keeps going down",
                "Customer support is unresponsive",
                "Features that were promised are missing",
                "Performance has significantly degraded"
            ]),
            "{incident_description}": random.choice([
                "The representative was rude and unhelpful",
                "I was transferred multiple times without resolution",
                "My issue was marked as resolved but nothing was fixed",
                "I waited on hold for over an hour"
            ]),
            "{specific_problems}": random.choice([
                "The interface is confusing and hard to navigate",
                "Important features have been removed or hidden",
                "Performance is much slower than before",
                "The new workflow doesn't make sense"
            ]),
            
            # Feature request terms
            "{use_case}": random.choice([
                "our daily workflow",
                "team collaboration",
                "client reporting",
                "data analysis",
                "project management"
            ]),
            "{current_situation}": random.choice([
                "we have to manually export and import data",
                "the process requires multiple steps",
                "we can't customize the layout",
                "there's no way to automate this task"
            ]),
            "{proposed_solution}": random.choice([
                "there was an automated workflow feature",
                "we could customize the dashboard",
                "bulk operations were supported",
                "there was better integration with third-party tools"
            ]),
            "{workaround}": random.choice([
                "a combination of Excel and manual processes",
                "third-party tools for integration",
                "custom scripts we've developed",
                "multiple different platforms"
            ])
        }
        
        result = template
        for placeholder, replacement in replacements.items():
            result = result.replace(placeholder, replacement)
        
        return result
    
    def generate_batch(self, count: int = 10, category_distribution: Optional[Dict[EmailCategory, float]] = None) -> List[MockEmail]:
        """Generate a batch of emails with specified distribution"""
        
        if category_distribution is None:
            # Default distribution
            category_distribution = {
                EmailCategory.TECHNICAL_ISSUE: 0.4,
                EmailCategory.BILLING_QUESTION: 0.2,
                EmailCategory.GENERAL_INQUIRY: 0.2,
                EmailCategory.FEATURE_REQUEST: 0.1,
                EmailCategory.COMPLAINT: 0.1
            }
        
        emails = []
        for category, ratio in category_distribution.items():
            category_count = int(count * ratio)
            for _ in range(category_count):
                emails.append(self.generate_email(category=category))
        
        # Fill remaining slots if any
        while len(emails) < count:
            emails.append(self.generate_email())
        
        # Shuffle to randomize order
        random.shuffle(emails)
        
        return emails

class MockEmailService:
    """Service to manage mock emails for testing"""
    
    def __init__(self):
        self.generator = MockEmailGenerator()
        self.inbox: List[MockEmail] = []
        self.processed_emails: List[str] = []
        self.is_running = False
    
    async def start_email_simulation(self, interval_minutes: int = 5, batch_size: int = 3):
        """Start generating emails at regular intervals"""
        self.is_running = True
        
        while self.is_running:
            # Generate new batch of emails
            new_emails = self.generator.generate_batch(batch_size)
            self.inbox.extend(new_emails)
            
            print(f"📧 Generated {len(new_emails)} new emails. Inbox: {len(self.inbox)} emails")
            
            # Wait for next interval
            await asyncio.sleep(interval_minutes * 60)
    
    def stop_email_simulation(self):
        """Stop email generation"""
        self.is_running = False
    
    def get_unprocessed_emails(self) -> List[MockEmail]:
        """Get all unprocessed emails"""
        return [email for email in self.inbox if email.email_id not in self.processed_emails]
    
    def get_emails_by_priority(self, priority: EmailPriority) -> List[MockEmail]:
        """Get emails by priority"""
        return [email for email in self.inbox if email.priority == priority and email.email_id not in self.processed_emails]
    
    def get_emails_by_category(self, category: EmailCategory) -> List[MockEmail]:
        """Get emails by category"""
        return [email for email in self.inbox if email.category == category and email.email_id not in self.processed_emails]
    
    def mark_as_processed(self, email_id: str):
        """Mark email as processed"""
        if email_id not in self.processed_emails:
            self.processed_emails.append(email_id)
    
    def get_next_email(self) -> Optional[MockEmail]:
        """Get next unprocessed email"""
        unprocessed = self.get_unprocessed_emails()
        if unprocessed:
            # Sort by priority and timestamp
            priority_order = {
                EmailPriority.URGENT: 0,
                EmailPriority.HIGH: 1,
                EmailPriority.MEDIUM: 2,
                EmailPriority.LOW: 3
            }
            
            sorted_emails = sorted(
                unprocessed,
                key=lambda e: (priority_order[e.priority], e.timestamp)
            )
            
            return sorted_emails[0]
        
        return None
    
    def generate_test_email(self, category: EmailCategory = None, priority: EmailPriority = None) -> MockEmail:
        """Generate a single test email"""
        email = self.generator.generate_email(category, priority)
        self.inbox.append(email)
        return email
    
    def get_inbox_summary(self) -> Dict[str, Any]:
        """Get inbox summary statistics"""
        unprocessed = self.get_unprocessed_emails()
        
        category_counts = {}
        priority_counts = {}
        sentiment_counts = {}
        
        for email in unprocessed:
            # Count by category
            category_counts[email.category.value] = category_counts.get(email.category.value, 0) + 1
            
            # Count by priority
            priority_counts[email.priority.value] = priority_counts.get(email.priority.value, 0) + 1
            
            # Count by sentiment
            sentiment_counts[email.sentiment] = sentiment_counts.get(email.sentiment, 0) + 1
        
        return {
            "total_emails": len(self.inbox),
            "unprocessed_emails": len(unprocessed),
            "processed_emails": len(self.processed_emails),
            "category_breakdown": category_counts,
            "priority_breakdown": priority_counts,
            "sentiment_breakdown": sentiment_counts,
            "oldest_unprocessed": min([e.timestamp for e in unprocessed]).isoformat() if unprocessed else None,
            "newest_unprocessed": max([e.timestamp for e in unprocessed]).isoformat() if unprocessed else None
        }
    
    def clear_inbox(self):
        """Clear all emails from inbox"""
        self.inbox.clear()
        self.processed_emails.clear()

# Global mock email service instance
mock_email_service = MockEmailService()

def get_mock_email_service() -> MockEmailService:
    """Get the global mock email service instance"""
    return mock_email_service

# Example usage and testing
if __name__ == "__main__":
    async def test_mock_email_service():
        service = get_mock_email_service()
        
        print("🧪 Testing Mock Email Service")
        print("=" * 50)
        
        # Generate test emails for each category
        for category in EmailCategory:
            email = service.generate_test_email(category=category)
            print(f"\\n📧 {category.value.upper()}:")
            print(f"   From: {email.sender}")
            print(f"   Subject: {email.subject}")
            print(f"   Priority: {email.priority.value}")
            print(f"   Sentiment: {email.sentiment}")
            print(f"   Content Preview: {email.content[:100]}...")
        
        # Test inbox summary
        print("\\n📊 Inbox Summary:")
        summary = service.get_inbox_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Test email processing
        print("\\n🔄 Processing Emails:")
        while True:
            next_email = service.get_next_email()
            if not next_email:
                break
            
            print(f"   Processing: {next_email.subject} (Priority: {next_email.priority.value})")
            service.mark_as_processed(next_email.email_id)
        
        print("\\n✅ All emails processed!")
    
    asyncio.run(test_mock_email_service())
