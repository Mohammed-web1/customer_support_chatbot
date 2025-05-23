# customer-support-chatbot
# AI Customer Support Chatbot

A comprehensive AI-powered customer support chatbot with advanced features including vector search, webhook integration, and Google Sheets synchronization.

## Features

- 🤖 **AI-Powered Responses** - Using OpenAI GPT or DeepSeek API
- 🔍 **Vector Search** - ChromaDB for intelligent knowledge retrieval
- 📊 **Google Sheets Integration** - Sync knowledge base and log conversations
- 🔗 **Webhook Support** - Real-time integrations with external systems
- 💾 **Persistent Storage** - SQLite database for conversation history
- 🚀 **FastAPI Backend** - High-performance async API
- 🐳 **Docker Support** - Easy deployment with Docker Compose

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-customer-support-chatbot

# Run setup script
python scripts/setup.py

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Update your `.env` file with actual values:

```env
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_SHEETS_ID=your-google-sheet-id
WEBHOOK_SECRET=your-webhook-secret
```

### 3. Google Sheets Setup

1. Create a Google Service Account
2. Download the credentials JSON file
3. Replace `credentials.json` with your credentials
4. Share your Google Sheet with the service account email

### 4. Run the Application

```bash
# Development
python main.py

# Production with Docker
docker-compose up -d
```

## File Structure

```
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker image definition
├── config.py             # Configuration management
│
├── api/
│   └── routes.py         # API endpoints
│
├── database/
│   └── models.py         # SQLAlchemy models and database setup
│
├── ai_models/
│   └── llm_manager.py    # LLM integration (OpenAI/DeepSeek)
│
├── vector_store/
│   └── vector_manager.py # ChromaDB vector store management
│
├── integrations/
│   └── google_sheets.py  # Google Sheets integration
│
├── webhook/
│   └── webhook_handler.py # Webhook processing
│
├── utils/
│   └── helpers.py        # Utility functions
│
├── scripts/
│   └── setup.py          # Setup and initialization script
│
└── tests/
    └── test_api.py       # API tests
```

## API Endpoints

### Chat Endpoint
```bash
POST /api/v1/chat
{
  "message": "I need help with my account",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

### Webhook Endpoint
```bash
POST /api/v1/webhook
# Handles incoming webhooks with signature verification
```

### Knowledge Base Management
```bash
# Update knowledge base
POST /api/v1/knowledge-base/update

# Sync from Google Sheets
GET /api/v1/knowledge-base/sync
```

### Conversation History
```bash
GET /api/v1/conversations/{session_id}
```

## Google Sheets Integration

### Knowledge Base Sheet Structure
| Column | Description |
|--------|-------------|
| id | Unique identifier |
| title | Document title |
| content | Full content |
| category | Category/topic |
| tags | Comma-separated tags |

### Conversation Log Sheet Structure
| Column | Description |
|--------|-------------|
| session_id | Chat session ID |
| user_id | User identifier |
| message | User message |
| response | Bot response |
| timestamp | Message timestamp |
| confidence | Response confidence score |

## Webhook Integration

The system supports webhooks for real-time integrations:

```json
{
  "type": "message",
  "data": {
    "user_id": "user123",
    "message": "Hello",
    "timestamp": "2025-05-23T10:00:00Z"
  }
}
```

## Vector Search

The system uses ChromaDB for semantic search:
- Automatic text chunking and embedding
- Similarity search for relevant context
- Support for metadata filtering

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key | Yes* |
| DEEPSEEK_API_KEY | DeepSeek API key | Yes* |
| GOOGLE_SHEETS_ID | Google Sheet ID | Yes |
| WEBHOOK_SECRET | Webhook signature secret | No |
| DATABASE_URL | Database connection string | No |

*Either OpenAI or DeepSeek key is required

## Testing

```bash
# Run tests
pytest tests/

# Test specific endpoint
pytest tests/test_api.py::test_chat_endpoint
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Monitoring and Logging

- Comprehensive logging throughout the application
- Health check endpoint: `/health`
- API documentation: `/docs`

## Security Features

- Webhook signature verification
- Input sanitization
- CORS configuration
- Environment variable protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs in the `logs/` directory
- Open an issue on GitHub
