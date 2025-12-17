# Bedrock Knowledge Base MCP Server

A FastMCP server that provides seamless access to AWS Bedrock Knowledge Base through the Model Context Protocol (MCP). This server enables AI assistants to query your knowledge base and retrieve relevant documents with direct access links.

## 🚀 Key Features

### 📚 Bedrock Knowledge Base Integration
- **Semantic Search**: Query your Bedrock Knowledge Base using natural language
- **Relevance Scoring**: Get documents ranked by relevance with confidence scores
- **Configurable Results**: Control the number of returned documents (default: 5)
- **Rich Metadata**: Access document metadata including source location and content type

### 🔗 S3 Presigned URL Generation
- **Direct Document Access**: Automatically generates presigned URLs for S3-stored documents
- **Secure Access**: Time-limited URLs (configurable expiration, default: 1 hour)
- **Click-to-Download**: Users can directly access original documents via generated links
- **Multiple Formats**: Supports various document formats (PDF, DOCX, TXT, etc.)

### 🛠 Deployment Flexibility
- **Local Development**: Run locally for testing and development
- **AgentCore Deployment**: Deploy to AWS AgentCore for production use
- **MCP Protocol**: Compatible with any MCP client (Kiro IDE, Claude Desktop, etc.)
- **Environment-based Configuration**: Easy configuration via environment variables

### 🎯 LLM Context Optimization
- **Dynamic Tool Descriptions**: Customize tool descriptions based on your knowledge base content
- **Smart Invocation**: LLMs know when to use the tool based on configurable descriptions
- **Structured Output**: Formatted results with source attribution and relevance scores

## Setup

### 1. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials and Knowledge Base configuration:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
MAX_RESULTS=5
PRESIGNED_URL_EXPIRATION=3600
KNOWLEDGE_BASE_DESCRIPTION=Description of your knowledge base for LLM context
```

### 2. Install Dependencies

Using UV (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
uv run python server.py
```

## AgentCore Deployment

### 1. Configure Environment Variables

You need to set up two environment files:

**AgentCore Configuration:**
```bash
cp agentcore_config.env.example agentcore_config.env
```

Edit `agentcore_config.env` with your AgentCore settings:
```env
# Cognito Configuration
COGNITO_CLIENT_ID=your_cognito_client_id
COGNITO_DISCOVERY_URL=https://cognito-idp.REGION.amazonaws.com/USER_POOL_ID/.well-known/openid-configuration
TOOL_NAME=your_tool_name
# Optional: VPC and IAM role configuration
```

**MCP Server Configuration:**
```bash
cp .env.example .env
```

Edit `.env` with your MCP server settings:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
KNOWLEDGE_BASE_DESCRIPTION=Description of your knowledge base
```

### 2. Deploy to AgentCore

```bash
uv run python agentcore_configure.py
```

## MCP Integration

### Kiro IDE Configuration

Add to your MCP configuration (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "bedrock-kb": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/this/project", "python", "server.py"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "KNOWLEDGE_BASE_ID": "your_kb_id"
      }
    }
  }
}
```

### Available Tools

#### `retrieve(query: str)`
Query the Bedrock Knowledge Base and retrieve relevant documents.

**Input:**
- `query`: Natural language question or search terms

**Output:**
- Ranked list of relevant documents with:
  - Relevance scores (0.0 to 1.0)
  - Document content excerpts
  - Clickable presigned URLs to original S3 documents
  - Source file names and metadata

**Example Output:**
```
[1] (Score: 0.856) Source: [company-policy.pdf](https://presigned-url-here)
This document outlines the company's remote work policy...

---

[2] (Score: 0.742) Source: [technical-guide.docx](https://another-presigned-url-here)
Technical implementation guidelines for the new system...
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | Required |
| `AWS_REGION` | AWS Region | `us-east-1` |
| `KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | Required |
| `MAX_RESULTS` | Maximum number of results to return | `5` |
| `PRESIGNED_URL_EXPIRATION` | Presigned URL expiration in seconds | `3600` |
| `KNOWLEDGE_BASE_DESCRIPTION` | Description for LLM context | Generic description |

## 🔧 How It Works

1. **Query Processing**: The MCP server receives natural language queries from AI assistants
2. **Knowledge Base Search**: Uses AWS Bedrock's `retrieve` API to perform semantic search
3. **Document Retrieval**: Fetches relevant documents with metadata and relevance scores
4. **URL Generation**: Automatically generates presigned URLs for S3-stored documents
5. **Response Formatting**: Returns structured results with clickable links and source attribution

## 📋 Prerequisites

- AWS Account with Bedrock Knowledge Base configured
- S3 bucket containing your documents (indexed by the Knowledge Base)
- AWS credentials with appropriate permissions:
  - `bedrock:Retrieve` on your Knowledge Base
  - `s3:GetObject` on your document bucket

## 🔒 Security Notes

- Never commit `.env` or `agentcore_config.env` files to version control
- Use IAM roles with minimal required permissions
- Regularly rotate AWS credentials
- Set appropriate presigned URL expiration times
- Consider using VPC endpoints for enhanced security in production

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License