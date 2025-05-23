import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Any
from config import Config
import logging

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        # Use SentenceTransformer embeddings instead of OpenAI
        self.embeddings = SentenceTransformerEmbeddings(
            model_name=Config.EMBEDDING_MODEL
        )
        self.persist_directory = Config.CHROMA_PERSIST_DIRECTORY
        self.collection_name = "customer_support_kb"
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Initialize vector store
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store"""
        try:
            docs = []
            for doc in documents:
                # Split text into chunks
                chunks = self.text_splitter.split_text(doc['content'])
                
                for i, chunk in enumerate(chunks):
                    docs.append(Document(
                        page_content=chunk,
                        metadata={
                            'title': doc.get('title', ''),
                            'category': doc.get('category', ''),
                            'chunk_id': f"{doc.get('id', '')}_{i}",
                            'source': doc.get('source', 'knowledge_base')
                        }
                    ))
            
            # Add to vector store
            self.vector_store.add_documents(docs)
            logger.info(f"Added {len(docs)} document chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 5):
        """Search with similarity scores"""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with score: {e}")
            return []
    
    def update_knowledge_base(self, new_documents: List[Dict[str, Any]]):
        """Update the knowledge base with new documents"""
        try:
            # Clear existing collection
            self.client.delete_collection(self.collection_name)
            
            # Recreate vector store
            self.vector_store = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # Add new documents
            self.add_documents(new_documents)
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            raise