import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_root_endpoint():
    '''Test root endpoint'''
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Customer Support Chatbot API" in response.json()["message"]

def test_health_check():
    '''Test health check endpoint'''
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    '''Test chat endpoint'''
    chat_data = {
        "message": "Hello, I need help with my account",
        "session_id": "test-session-123"
    }
    
    response = client.post("/api/v1/chat", json=chat_data)
    assert response.status_code == 200
    
    response_data = response.json()
    assert "response" in response_data
    assert "session_id" in response_data
    assert "confidence" in response_data

def test_knowledge_base_update():
    '''Test knowledge base update endpoint'''
    kb_data = {
        "documents": [
            {
                "id": "1",
                "title": "Test Document",
                "content": "This is a test document for the knowledge base",
                "category": "test"
            }
        ]
    }
    
    response = client.post("/api/v1/knowledge-base/update", json=kb_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_conversation_retrieval():
    '''Test conversation retrieval'''
    # First, create a conversation
    chat_data = {
        "message": "Test message",
        "session_id": "test-conversation-456"
    }
    
    chat_response = client.post("/api/v1/chat", json=chat_data)
    assert chat_response.status_code == 200
    
    # Then retrieve it
    response = client.get("/api/v1/conversations/test-conversation-456")
    assert response.status_code == 200
    
    conversation_data = response.json()
    assert "session_id" in conversation_data
    assert "messages" in conversation_data