"""
AWS Bedrock Configuration
LLM and Embeddings setup for the multi-agent system
"""

import boto3
from langchain_aws import ChatBedrock, BedrockEmbeddings

# Initialize AWS session
session = boto3.Session()

# Configure LLM (Language Model)
llm = ChatBedrock(
    model_id="us.amazon.nova-micro-v1:0",
    client=session.client("bedrock-runtime"),
    temperature=0.2,
)

# Configure Embeddings
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    client=session.client("bedrock-runtime")
)

