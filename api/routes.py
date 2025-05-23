from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database.models import get_db, Conversation, Message
from ai_models.llm_manager import LLMManager
from vector_store.vector_manager import VectorStoreManager
from integrations.google_sheets import GoogleSheetsIntegration
from webhook.webhook_handler import WebhookHandler
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components
llm_manager = LLMManager()  # Now using only DeepSeek
vector_manager = VectorStoreManager()
sheets_integration = GoogleSheetsIntegration()
webhook_handler = WebhookHandler()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    confidence: float
    timestamp: str

class KnowledgeBaseUpdate(BaseModel):
    documents: List[Dict[str, Any]]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage, db: Session = Depends(get_db)):
    '''Handle chat messages'''
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        user_id = chat_message.user_id or "anonymous"
        
        # Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Get relevant context from vector store
        relevant_docs = vector_manager.similarity_search(chat_message.message, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # Get conversation history
        recent_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp.desc()).limit(10).all()
        
        conversation_history = []
        for msg in reversed(recent_messages):
            if msg.message_type == "user":
                conversation_history.append({"user": msg.content, "assistant": ""})
            elif msg.message_type == "assistant" and conversation_history:
                conversation_history[-1]["assistant"] = msg.content
        
        # Generate response
        response_data = llm_manager.generate_response(
            user_message=chat_message.message,
            context=context,
            conversation_history=conversation_history
        )
        
        # Save messages to database
        user_message_obj = Message(
            conversation_id=conversation.id,
            message_type="user",
            content=chat_message.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message_obj)
        
        assistant_message_obj = Message(
            conversation_id=conversation.id,
            message_type="assistant",
            content=response_data["response"],
            confidence_score=str(response_data.get("confidence", 0.8)),
            timestamp=datetime.utcnow()
        )
        db.add(assistant_message_obj)
        db.commit()
        
        # Log to Google Sheets
        try:
            sheets_integration.log_conversation({
                "session_id": session_id,
                "user_id": user_id,
                "user_message": chat_message.message,
                "bot_response": response_data["response"],
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": response_data.get("confidence", 0.8)
            })
        except Exception as e:
            logger.warning(f"Failed to log to Google Sheets: {e}")
        
        return ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            confidence=response_data.get("confidence", 0.8),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook")
async def webhook_endpoint(request: Request):
    '''Handle incoming webhooks'''
    try:
        result = await webhook_handler.handle_webhook(request)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/knowledge-base/update")
async def update_knowledge_base(kb_update: KnowledgeBaseUpdate, db: Session = Depends(get_db)):
    '''Update knowledge base'''
    try:
        # Update vector store
        vector_manager.update_knowledge_base(kb_update.documents)
        
        # Update Google Sheets
        sheets_integration.update_knowledge_base(kb_update.documents)
        
        return {"status": "success", "message": f"Updated {len(kb_update.documents)} documents"}
        
    except Exception as e:
        logger.error(f"Error updating knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to update knowledge base")

@router.get("/knowledge-base/sync")
async def sync_knowledge_base():
    '''Sync knowledge base from Google Sheets'''
    try:
        # Fetch data from Google Sheets
        kb_data = sheets_integration.get_knowledge_base_data()
        
        if kb_data:
            # Update vector store
            vector_manager.update_knowledge_base(kb_data)
            
            return {
                "status": "success", 
                "message": f"Synced {len(kb_data)} documents from Google Sheets"
            }
        else:
            return {"status": "warning", "message": "No data found in Google Sheets"}
            
    except Exception as e:
        logger.error(f"Error syncing knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync knowledge base")

@router.get("/conversations/{session_id}")
async def get_conversation(session_id: str, db: Session = Depends(get_db)):
    '''Get conversation history'''
    try:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp.asc()).all()
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "type": msg.message_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "confidence": msg.confidence_score
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")