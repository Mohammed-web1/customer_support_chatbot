import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib
import json

def generate_session_id() -> str:
    '''Generate unique session ID'''
    return str(uuid.uuid4())

def sanitize_text(text: str) -> str:
    '''Sanitize input text'''
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potential harmful characters
    text = re.sub(r'[<>{}]', '', text)
    
    return text

def extract_keywords(text: str) -> List[str]:
    '''Extract keywords from text'''
    # Simple keyword extraction
    words = re.findall(r'\b\w{3,}\b', text.lower())
    return list(set(words))

def calculate_confidence(similarity_scores: List[float]) -> float:
    '''Calculate confidence based on similarity scores'''
    if not similarity_scores:
        return 0.0
    
    avg_score = sum(similarity_scores) / len(similarity_scores)
    return min(avg_score * 1.2, 1.0)  # Boost and cap at 1.0

def hash_content(content: str) -> str:
    '''Generate hash for content'''
    return hashlib.md5(content.encode()).hexdigest()

def format_timestamp(dt: datetime = None) -> str:
    '''Format timestamp for API responses'''
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"

def validate_session_id(session_id: str) -> bool:
    '''Validate session ID format'''
    try:
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False

def clean_html(text: str) -> str:
    '''Remove HTML tags from text'''
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def truncate_text(text: str, max_length: int = 1000) -> str:
    '''Truncate text to maximum length'''
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."