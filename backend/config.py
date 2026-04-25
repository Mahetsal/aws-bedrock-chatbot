"""
Configuration management for the Bedrock Chatbot.
Loads settings from environment variables with sensible defaults.
"""

import os


class Config:
    """Application configuration loaded from environment variables."""
    
    # AWS Settings
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID = os.getenv(
        "BEDROCK_MODEL_ID",
        "anthropic.claude-3-sonnet-20240229-v1:0"
    )
    DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "chatbot-sessions")
    
    # Model Parameters
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))
    
    # Session Settings
    SESSION_TTL = int(os.getenv("SESSION_TTL", "3600"))
    
    # System Prompt
    SYSTEM_PROMPT = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful, friendly AI assistant. Provide clear, "
        "concise answers. If you're unsure about something, say so "
        "rather than guessing."
    )
