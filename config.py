import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # DeepSeek API Configuration
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
    GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
    
    # Webhook
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Embedding Model
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")