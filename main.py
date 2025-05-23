from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from database.models import create_tables
import logging
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Customer Support Chatbot",
    description="Advanced AI chatbot with vector search, webhooks, and Google Sheets integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    '''Initialize database and components'''
    try:
        create_tables()
        logger.info("Database tables created successfully")
        
        # Initialize vector store with sample data if empty
        from vector_store.vector_manager import VectorStoreManager
        from integrations.google_sheets import GoogleSheetsIntegration
        
        vector_manager = VectorStoreManager()
        sheets_integration = GoogleSheetsIntegration()
        
        # Try to sync knowledge base from Google Sheets
        try:
            kb_data = sheets_integration.get_knowledge_base_data()
            if kb_data:
                vector_manager.add_documents(kb_data)
                logger.info(f"Loaded {len(kb_data)} documents from Google Sheets")
        except Exception as e:
            logger.warning(f"Could not load from Google Sheets: {e}")
            
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.get("/")
async def root():
    return {
        "message": "AI Customer Support Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-05-23T10:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )