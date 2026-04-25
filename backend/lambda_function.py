"""
AWS Lambda handler for Bedrock Chatbot.
Handles API Gateway requests, manages chat sessions,
and communicates with Amazon Bedrock for AI responses.
"""

import json
import uuid
import logging
from datetime import datetime

from bedrock_client import BedrockClient
from dynamodb_handler import ChatHistoryManager
from config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
bedrock = BedrockClient(
    model_id=Config.BEDROCK_MODEL_ID,
    region=Config.AWS_REGION
)
chat_history = ChatHistoryManager(
    table_name=Config.DYNAMODB_TABLE,
    region=Config.AWS_REGION
)


def build_response(status_code: int, body: dict) -> dict:
    """Build a standardized API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body),
    }


def handle_chat(event: dict) -> dict:
    """Process a chat message and return AI response."""
    body = json.loads(event.get("body", "{}"))
    
    user_message = body.get("message", "").strip()
    session_id = body.get("session_id", str(uuid.uuid4()))
    
    if not user_message:
        return build_response(400, {"error": "Message cannot be empty"})
    
    # Retrieve conversation history for context
    history = chat_history.get_history(session_id, limit=Config.HISTORY_LIMIT)
    
    # Build messages array with history
    messages = []
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Get response from Bedrock
        response_text = bedrock.invoke(
            messages=messages,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            system_prompt=Config.SYSTEM_PROMPT
        )
        
        # Save both messages to history
        chat_history.save_message(session_id, "user", user_message)
        chat_history.save_message(session_id, "assistant", response_text)
        
        return build_response(200, {
            "response": response_text,
            "session_id": session_id,
            "model": Config.BEDROCK_MODEL_ID,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Bedrock invocation error: {str(e)}")
        return build_response(500, {
            "error": "Failed to generate response",
            "details": str(e)
        })


def handle_history(event: dict) -> dict:
    """Retrieve chat history for a session."""
    params = event.get("queryStringParameters", {}) or {}
    session_id = params.get("session_id")
    
    if not session_id:
        return build_response(400, {"error": "session_id is required"})
    
    history = chat_history.get_history(session_id)
    return build_response(200, {
        "session_id": session_id,
        "messages": history
    })


def handle_new_session(event: dict) -> dict:
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    return build_response(200, {
        "session_id": session_id,
        "message": "New session created"
    })


def lambda_handler(event, context):
    """Main Lambda entry point."""
    logger.info(f"Received event: {json.dumps(event)}")
    
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    
    # Handle CORS preflight
    if http_method == "OPTIONS":
        return build_response(200, {"message": "OK"})
    
    # Route requests
    if path == "/chat" and http_method == "POST":
        return handle_chat(event)
    elif path == "/history" and http_method == "GET":
        return handle_history(event)
    elif path == "/session" and http_method == "POST":
        return handle_new_session(event)
    else:
        return build_response(404, {"error": "Route not found"})


# Local development server
if __name__ == "__main__":
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class LocalHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            event = {
                "httpMethod": "POST",
                "path": self.path,
                "body": body,
            }
            
            response = lambda_handler(event, None)
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response["body"].encode())
        
        def do_GET(self):
            event = {
                "httpMethod": "GET",
                "path": self.path,
                "queryStringParameters": {},
            }
            response = lambda_handler(event, None)
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response["body"].encode())
        
        def do_OPTIONS(self):
            event = {"httpMethod": "OPTIONS", "path": self.path}
            response = lambda_handler(event, None)
            self.send_response(200)
            self.end_headers()
    
    print("Starting local server on http://localhost:8000")
    server = HTTPServer(("localhost", 8000), LocalHandler)
    server.serve_forever()
