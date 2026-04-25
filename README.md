# AWS Bedrock Chatbot

A serverless AI chatbot built with **Amazon Bedrock**, **AWS Lambda**, and **Python**. This project demonstrates how to build a production-ready conversational AI application using AWS cloud-native services.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange?logo=amazon-aws)
![License](https://img.shields.io/badge/License-MIT-green)

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Frontend   │────▶│  API Gateway │────▶│   AWS Lambda      │
│  (HTML/JS)   │◀────│   (REST)     │◀────│   (Python 3.11)   │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │  Amazon Bedrock    │
                                          │  (Claude/Titan)    │
                                          └─────────┬─────────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │   DynamoDB         │
                                          │ (Chat History)     │
                                          └───────────────────┘
```

## Features

- **Multi-model support** — Switch between Claude, Titan, and other Bedrock models
- **Conversation memory** — Chat history stored in DynamoDB with session management
- **Streaming responses** — Real-time token streaming for responsive UX
- **Rate limiting** — Built-in request throttling to manage API costs
- **Clean web UI** — Minimal, responsive frontend with dark mode
- **Infrastructure as Code** — CloudFormation template for one-click deployment

## Project Structure

```
aws-bedrock-chatbot/
├── backend/
│   ├── lambda_function.py      # Main Lambda handler
│   ├── bedrock_client.py       # Bedrock API wrapper
│   ├── dynamodb_handler.py     # Chat history persistence
│   ├── config.py               # Configuration management
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── index.html              # Chat interface
│   ├── style.css               # Styling
│   └── app.js                  # Frontend logic
├── infrastructure/
│   └── template.yaml           # CloudFormation template
├── tests/
│   ├── test_bedrock_client.py  # Unit tests
│   └── test_lambda.py          # Integration tests
├── .gitignore
├── LICENSE
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- AWS CLI configured with appropriate permissions
- AWS account with Bedrock model access enabled

### Local Development

```bash
# Clone the repository
git clone https://github.com/saleh-alkhrisat/aws-bedrock-chatbot.git
cd aws-bedrock-chatbot

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
export DYNAMODB_TABLE=chatbot-sessions

# Run locally
python backend/lambda_function.py
```

### Deploy to AWS

```bash
# Deploy infrastructure
aws cloudformation deploy \
    --template-file infrastructure/template.yaml \
    --stack-name bedrock-chatbot \
    --capabilities CAPABILITY_IAM

# Package and deploy Lambda
cd backend && zip -r function.zip . && \
aws lambda update-function-code \
    --function-name bedrock-chatbot \
    --zip-file fileb://function.zip
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `BEDROCK_MODEL_ID` | Bedrock model identifier | `anthropic.claude-3-sonnet` |
| `DYNAMODB_TABLE` | DynamoDB table name | `chatbot-sessions` |
| `MAX_TOKENS` | Max response tokens | `1024` |
| `TEMPERATURE` | Model temperature | `0.7` |
| `SESSION_TTL` | Session expiry (seconds) | `3600` |

## License

MIT License — see [LICENSE](LICENSE) for details.
