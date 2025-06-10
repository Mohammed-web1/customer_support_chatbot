from langchain.schema import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any, Optional
import requests
from config import Config
import logging
import json

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        self.setup_deepseek()
        self.setup_prompts()
        
    def setup_deepseek(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL
        self.model = Config.DEEPSEEK_MODEL
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")
    
    def setup_prompts(self):
        self.system_prompt_template = '''
You are an AI customer support assistant. Your role is to help customers with their inquiries in a friendly, professional, and helpful manner.

Guidelines:
1. Always be polite and professional
2. Provide accurate information based on the knowledge base
3. If you don't know something, admit it and offer to escalate
4. Keep responses concise but comprehensive
5. Ask clarifying questions when needed

Knowledge Base Context:
{context}

Previous Conversation:
{history}
'''
    
    def generate_response(
        self, 
        user_message: str, 
        context: str = "", 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate response using DeepSeek API"""
        try:
            return self._generate_deepseek_response(user_message, context, conversation_history)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _generate_deepseek_response(
        self, 
        user_message: str, 
        context: str, 
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate response using DeepSeek API"""
        try:
           
            history_text = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  
                    history_text += f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}\n"
            
        
            system_message = self.system_prompt_template.format(
                context=context,
                history=history_text
            )
            
           
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            }
            
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    response_content = result["choices"][0]["message"]["content"]
                    
                    return {
                        "response": response_content,
                        "confidence": 0.8,  
                        "tokens_used": result.get("usage", {}),
                        "model": self.model
                    }
                else:
                    raise Exception("No valid response from DeepSeek API")
            else:
                error_msg = f"DeepSeek API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text}"
                
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API request timeout")
            raise Exception("Request timeout - please try again")
        except requests.exceptions.ConnectionError:
            logger.error("DeepSeek API connection error")
            raise Exception("Connection error - please check your internet connection")
        except Exception as e:
            logger.error(f"DeepSeek response generation error: {e}")
            raise
    
    def validate_api_key(self) -> bool:
        """Validate DeepSeek API key"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False
