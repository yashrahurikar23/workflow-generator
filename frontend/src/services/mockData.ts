// Mock data service for testing frontend without backend
export const mockWorkflows = [
  {
    workflow_id: "workflow-1",
    name: "Email Marketing Campaign",
    description: "Automated email marketing workflow that sends personalized emails based on user behavior",
    steps: [
      {
        step_id: "step1",
        name: "Collect User Data",
        step_type: "data_transform",
        description: "Gather user behavior data from various sources",
        depends_on: [],
        config: { source: "analytics", fields: ["clicks", "views", "purchases"] }
      },
      {
        step_id: "step2", 
        name: "Segment Users",
        step_type: "condition",
        description: "Segment users based on behavior patterns",
        depends_on: ["step1"],
        config: { conditions: ["high_engagement", "recent_purchase"] }
      },
      {
        step_id: "step3",
        name: "Generate Email Content",
        step_type: "llm_process",
        description: "Use AI to generate personalized email content",
        depends_on: ["step2"],
        config: { model: "gpt-4", template: "marketing_email" }
      },
      {
        step_id: "step4",
        name: "Send Emails",
        step_type: "email",
        description: "Send personalized emails to segmented users",
        depends_on: ["step3"],
        config: { provider: "sendgrid", batch_size: 100 }
      }
    ],
    tags: ["marketing", "email", "automation", "ai"],
    parallel_execution: false,
    status: "active",
    created_at: "2025-08-20T10:00:00Z",
    execution_count: 15
  },
  {
    workflow_id: "workflow-2",
    name: "Data Processing Pipeline",
    description: "Complex data pipeline for ETL operations with parallel processing",
    steps: [
      {
        step_id: "extract1",
        name: "Extract from Database",
        step_type: "database",
        description: "Extract data from primary database",
        depends_on: [],
        config: { connection: "postgres_main", query: "SELECT * FROM users" }
      },
      {
        step_id: "extract2",
        name: "Extract from API",
        step_type: "api_call", 
        description: "Extract data from external API",
        depends_on: [],
        config: { url: "https://api.example.com/users", method: "GET" }
      },
      {
        step_id: "transform1",
        name: "Clean User Data",
        step_type: "data_transform",
        description: "Clean and normalize user data",
        depends_on: ["extract1"],
        config: { operations: ["remove_duplicates", "normalize_names"] }
      },
      {
        step_id: "transform2",
        name: "Enrich with API Data",
        step_type: "data_transform",
        description: "Enrich user data with API information",
        depends_on: ["extract2", "transform1"],
        config: { join_key: "user_id", merge_strategy: "left" }
      },
      {
        step_id: "load",
        name: "Load to Data Warehouse",
        step_type: "database",
        description: "Load processed data to warehouse",
        depends_on: ["transform2"],
        config: { connection: "warehouse", table: "processed_users" }
      }
    ],
    tags: ["data", "pipeline", "etl", "parallel"],
    parallel_execution: true,
    status: "active",
    created_at: "2025-08-21T14:30:00Z",
    execution_count: 8
  },
  {
    workflow_id: "workflow-3",
    name: "Customer Onboarding Flow",
    description: "Comprehensive workflow for onboarding new customers with manual approval steps",
    steps: [
      {
        step_id: "welcome",
        name: "Send Welcome Email",
        step_type: "email",
        description: "Send welcome email to new customer",
        depends_on: [],
        config: { template: "welcome", delay: "immediate" }
      },
      {
        step_id: "kyc_check",
        name: "KYC Verification",
        step_type: "api_call",
        description: "Perform Know Your Customer verification",
        depends_on: ["welcome"],
        config: { service: "identity_verify", timeout: 300 }
      },
      {
        step_id: "manual_review",
        name: "Manual Review",
        step_type: "manual",
        description: "Manual review of customer application",
        depends_on: ["kyc_check"],
        config: { assignee: "compliance_team", priority: "high" }
      },
      {
        step_id: "account_setup",
        name: "Set Up Account",
        step_type: "database",
        description: "Create customer account and initial setup",
        depends_on: ["manual_review"],
        config: { table: "customers", create_profile: true }
      },
      {
        step_id: "onboarding_complete",
        name: "Send Completion Email",
        step_type: "email",
        description: "Notify customer that onboarding is complete",
        depends_on: ["account_setup"],
        config: { template: "onboarding_complete" }
      }
    ],
    tags: ["onboarding", "customers", "manual", "approval"],
    parallel_execution: false,
    status: "draft",
    created_at: "2025-08-22T09:15:00Z", 
    execution_count: 3
  }
];

export const mockWorkflowsResponse = {
  workflows: mockWorkflows,
  total: mockWorkflows.length,
  page: 1,
  size: 10
};
