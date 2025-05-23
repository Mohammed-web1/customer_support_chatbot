from fastapi import HTTPException, Request
import hashlib
import hmac
import json
from typing import Dict, Any
from config import Config
import logging

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        self.secret = Config.WEBHOOK_SECRET
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.secret:
            logger.warning("Webhook secret not configured")
            return True  # Skip verification if no secret
        
        try:
            expected_signature = hmac.new(
                self.secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    async def handle_webhook(self, request: Request) -> Dict[str, Any]:
        """Handle incoming webhook"""
        try:
            # Get payload
            payload = await request.body()
            
            # Get signature from headers
            signature = request.headers.get('X-Signature-256', '')
            
            # Verify signature
            if not self.verify_signature(payload, signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Parse JSON payload
            try:
                data = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
            
            # Process webhook data
            return await self.process_webhook_data(data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def process_webhook_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook data based on type"""
        webhook_type = data.get('type', 'unknown')
        
        if webhook_type == 'message':
            return await self.handle_message_webhook(data)
        elif webhook_type == 'knowledge_base_update':
            return await self.handle_kb_update_webhook(data)
        else:
            logger.warning(f"Unknown webhook type: {webhook_type}")
            return {"status": "ignored", "message": f"Unknown webhook type: {webhook_type}"}
    
    async def handle_message_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message webhook"""
        # This would typically trigger a chat response
        return {
            "status": "processed",
            "message": "Message webhook received",
            "data": data
        }
    
    async def handle_kb_update_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge base update webhook"""
        # This would typically trigger a knowledge base refresh
        return {
            "status": "processed",
            "message": "Knowledge base update webhook received",
            "data": data
        }