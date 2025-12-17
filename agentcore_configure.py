"""
AgentCore Configuration Script

This script configures and deploys the MCP server to AgentCore.
No code changes needed - just configure your environment variables.

Required setup:
1. Copy agentcore_config.env.example to agentcore_config.env and fill in your values
   (includes both AgentCore config AND MCP server environment variables)

The script will:
- Configure AgentCore with your Cognito/VPC settings
- Launch the MCP server with environment variables passed via env_vars parameter
"""

import os
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Runtime
from dotenv import load_dotenv

# Load AgentCore configuration from environment file
load_dotenv('agentcore_config.env')
# Also load MCP server environment variables from .env
load_dotenv('.env')

boto_session = Session()
region = boto_session.region_name

# Configuration from environment variables
tool_name = os.environ.get("TOOL_NAME", "bedrock_knowledgebase_agentcore_mcp")
role_arn = os.environ.get("ROLE_ARN")  # Optional
cognito_client_id = os.environ.get("COGNITO_CLIENT_ID")
cognito_discovery_url = os.environ.get("COGNITO_DISCOVERY_URL")

# VPC Configuration (optional)
vpc_subnets = os.environ.get("VPC_SUBNETS", "").split(",") if os.environ.get("VPC_SUBNETS") else None
vpc_security_groups = os.environ.get("VPC_SECURITY_GROUPS", "").split(",") if os.environ.get("VPC_SECURITY_GROUPS") else None

# Validate required configuration
if not cognito_client_id or not cognito_discovery_url:
    raise ValueError("COGNITO_CLIENT_ID and COGNITO_DISCOVERY_URL must be set in agentcore_config.env")

# Configure AgentCore Runtime
agentcore_runtime = Runtime()

auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_client_id],
        "discoveryUrl": cognito_discovery_url,
    }
}

print("Configuring AgentCore Runtime...")

# Build configuration parameters
config_params = {
    "entrypoint": "server.py",
    "auto_create_ecr": True,
    "requirements_file": "mcp_requirements.txt",
    "region": region,
    "authorizer_configuration": auth_config,
    "protocol": "MCP",
    "agent_name": tool_name,
}

# Add execution role if provided, otherwise use auto-create
if role_arn:
    config_params["execution_role"] = role_arn
    config_params["auto_create_execution_role"] = False
else:
    config_params["auto_create_execution_role"] = True

# Add VPC configuration if provided
if vpc_subnets and vpc_security_groups:
    config_params["vpc_enabled"] = True
    config_params["vpc_subnets"] = [s.strip() for s in vpc_subnets if s.strip()]
    config_params["vpc_security_groups"] = [sg.strip() for sg in vpc_security_groups if sg.strip()]

response = agentcore_runtime.configure(**config_params)
print("Configuration completed ✓")

# Launch
print("Launching MCP server to AgentCore Runtime...")
print("This may take several minutes...")

# Environment variables for the MCP server
# These will be passed to the deployed container
environment_variables = {
    "KNOWLEDGE_BASE_ID": os.environ.get("KNOWLEDGE_BASE_ID"),
    "AWS_REGION": region,
    "MAX_RESULTS": os.environ.get("MAX_RESULTS", "5"),
    "PRESIGNED_URL_EXPIRATION": os.environ.get("PRESIGNED_URL_EXPIRATION", "3600"),
    "KNOWLEDGE_BASE_DESCRIPTION": os.environ.get("KNOWLEDGE_BASE_DESCRIPTION", "A knowledge base for document retrieval"),
    "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
}

# Remove None values
environment_variables = {k: v for k, v in environment_variables.items() if v is not None}

# Validate required environment variables
required_vars = ["KNOWLEDGE_BASE_ID", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

launch_result = agentcore_runtime.launch(env_vars=environment_variables)

print("Launch completed ✓")
print(f"Agent ARN: {launch_result.agent_arn}")
print(f"Agent ID: {launch_result.agent_id}")