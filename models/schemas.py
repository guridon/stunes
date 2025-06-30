# src/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SongInfo(BaseModel):
    song_id: str
    title: str
    issue_date: Optional[str] = None
    artist_name: Optional[str] = None
    artist_id: Optional[str] = None
    genre_name: Optional[str] = None
    genre_id: Optional[str] = None
    album_title: Optional[str] = None
    album_id: Optional[str] = None
    subgenre_name: Optional[str] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    search_type: str = Field(..., pattern="^(title|artist|rag|recommendation)$")
    limit: int = Field(default=10, ge=1, le=50)
    user_id: Optional[str] = None

class SearchResponse(BaseModel):
    songs: List[SongInfo]
    rag_response: Optional[str] = None
    total_count: int
    search_type: str
    query: str
    execution_time: float

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$") 
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    songs: List[SongInfo] = []
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
