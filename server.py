import os
from fastmcp import FastMCP
import boto3

mcp = FastMCP("bedrock-rag",host="0.0.0.0", stateless_http=True)

def get_bedrock_client():
    """Create Bedrock Agent Runtime client with credentials from env."""
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if aws_access_key and aws_secret_key:
        return boto3.client(
            "bedrock-agent-runtime",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
    # Fall back to default credential chain
    return boto3.client("bedrock-agent-runtime", region_name=aws_region)


def get_s3_client():
    """Create S3 client with credentials from env."""
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if aws_access_key and aws_secret_key:
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
    # Fall back to default credential chain
    return boto3.client("s3", region_name=aws_region)


def generate_presigned_url(s3_uri: str) -> str:
    """Generate a presigned URL for S3 object."""
    try:
        # Parse S3 URI (s3://bucket/key)
        if not s3_uri.startswith("s3://"):
            return s3_uri  # Return original if not S3 URI
        
        # Remove s3:// prefix and split bucket/key
        path = s3_uri[5:]  # Remove 's3://'
        bucket, key = path.split('/', 1)
        
        # Get expiration from env variable
        expiration = int(os.environ.get("PRESIGNED_URL_EXPIRATION", "3600"))
        
        s3_client = get_s3_client()
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return presigned_url
    except Exception as e:
        return f"Error generating presigned URL: {str(e)}"


def _get_tool_description() -> str:
    """Build tool description from env variable."""
    kb_description = os.environ.get(
        "KNOWLEDGE_BASE_DESCRIPTION",
        "a knowledge base",
    )
    return f"""Retrieve relevant documents from a Bedrock Knowledge Base

{kb_description}

Args:
    query: The question or search query to find relevant documents.

Returns:
    Retrieved documents with their content and metadata."""


@mcp.tool(description=_get_tool_description())
def retrieve(query: str) -> str:
    """Retrieve documents from a Bedrock Knowledge Base."""
    knowledge_base_id = os.environ.get("KNOWLEDGE_BASE_ID")
    if not knowledge_base_id:
        return "Error: KNOWLEDGE_BASE_ID environment variable is not set."

    client = get_bedrock_client()

    try:
        response = client.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={
                "text": query,
                "type": "TEXT"
            },
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": int(os.environ.get("MAX_RESULTS", "5"))
                }
            }
        )
        
        # Format the retrieved results
        results = []
        for i, result in enumerate(response.get("retrievalResults", []), 1):
            content = result.get("content", {}).get("text", "")
            score = result.get("score", 0)
            location = result.get("location", {})
            
            # Extract source information and generate presigned URL
            source_info = ""
            if location.get("type") == "S3":
                s3_uri = location.get('s3Location', {}).get('uri', 'Unknown')
                if s3_uri != 'Unknown':
                    presigned_url = generate_presigned_url(s3_uri)
                    # Extract filename from S3 URI for display
                    filename = s3_uri.split('/')[-1] if '/' in s3_uri else s3_uri
                    source_info = f"Source: [{filename}]({presigned_url})"
                else:
                    source_info = f"Source: {s3_uri}"
            
            results.append(f"[{i}] (Score: {score:.3f}) {source_info}\n{content}")
        
        if not results:
            return "No relevant documents found in the knowledge base."
        
        return "\n\n---\n\n".join(results)
        
    except Exception as e:
        return f"Error calling Bedrock retrieve: {str(e)}"


def main():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
