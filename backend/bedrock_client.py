"""
Amazon Bedrock client wrapper.
Provides a clean interface for invoking foundation models
with support for multiple model families (Claude, Titan, etc.).
"""

import json
import boto3
from typing import Optional


class BedrockClient:
    """Wrapper for Amazon Bedrock Runtime API."""
    
    def __init__(self, model_id: str, region: str = "us-east-1"):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region
        )
    
    def invoke(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Invoke the Bedrock model with conversation messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0.0 - 1.0).
            system_prompt: Optional system-level instruction.
        
        Returns:
            The model's text response.
        """
        if "anthropic" in self.model_id:
            return self._invoke_claude(messages, max_tokens, temperature, system_prompt)
        elif "titan" in self.model_id:
            return self._invoke_titan(messages, max_tokens, temperature, system_prompt)
        else:
            return self._invoke_claude(messages, max_tokens, temperature, system_prompt)
    
    def _invoke_claude(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Invoke Anthropic Claude model via Bedrock."""
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ],
        }
        
        if system_prompt:
            request_body["system"] = system_prompt
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body),
        )
        
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
    
    def _invoke_titan(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Invoke Amazon Titan model via Bedrock."""
        # Build prompt from messages
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg['content']}")
        
        prompt_parts.append("Assistant:")
        input_text = "\n\n".join(prompt_parts)
        
        request_body = {
            "inputText": input_text,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": 0.9,
            },
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body),
        )
        
        response_body = json.loads(response["body"].read())
        return response_body["results"][0]["outputText"].strip()
    
    def list_available_models(self) -> list[str]:
        """List available foundation models in the account."""
        bedrock_client = boto3.client("bedrock", region_name="us-east-1")
        response = bedrock_client.list_foundation_models()
        
        return [
            {
                "id": model["modelId"],
                "name": model.get("modelName", "Unknown"),
                "provider": model.get("providerName", "Unknown"),
            }
            for model in response.get("modelSummaries", [])
        ]
