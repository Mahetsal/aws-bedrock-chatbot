"""
DynamoDB handler for chat session management.
Stores and retrieves conversation history with TTL-based expiration.
"""

import boto3
import time
from datetime import datetime
from typing import Optional
from boto3.dynamodb.conditions import Key


class ChatHistoryManager:
    """Manages chat history storage in DynamoDB."""
    
    def __init__(self, table_name: str, region: str = "us-east-1", ttl: int = 3600):
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)
        self.ttl = ttl
    
    def save_message(self, session_id: str, role: str, content: str) -> None:
        """
        Save a message to the chat history.
        
        Args:
            session_id: Unique session identifier.
            role: Message role ('user' or 'assistant').
            content: Message text content.
        """
        timestamp = datetime.utcnow().isoformat()
        ttl_value = int(time.time()) + self.ttl
        
        self.table.put_item(
            Item={
                "session_id": session_id,
                "timestamp": timestamp,
                "role": role,
                "content": content,
                "ttl": ttl_value,
            }
        )
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> list[dict]:
        """
        Retrieve chat history for a session.
        
        Args:
            session_id: Session to retrieve history for.
            limit: Maximum number of messages to return.
        
        Returns:
            List of message dicts sorted by timestamp.
        """
        query_params = {
            "KeyConditionExpression": Key("session_id").eq(session_id),
            "ScanIndexForward": True,  # Ascending order by timestamp
        }
        
        if limit:
            query_params["Limit"] = limit
        
        response = self.table.query(**query_params)
        
        return [
            {
                "role": item["role"],
                "content": item["content"],
                "timestamp": item["timestamp"],
            }
            for item in response.get("Items", [])
        ]
    
    def clear_session(self, session_id: str) -> int:
        """
        Delete all messages in a session.
        
        Returns:
            Number of messages deleted.
        """
        messages = self.get_history(session_id)
        
        with self.table.batch_writer() as batch:
            for msg in messages:
                batch.delete_item(
                    Key={
                        "session_id": session_id,
                        "timestamp": msg["timestamp"],
                    }
                )
        
        return len(messages)
    
    def get_active_sessions(self) -> list[str]:
        """Return list of active session IDs."""
        response = self.table.scan(
            ProjectionExpression="session_id",
            Select="SPECIFIC_ATTRIBUTES",
        )
        
        session_ids = set()
        for item in response.get("Items", []):
            session_ids.add(item["session_id"])
        
        return list(session_ids)
