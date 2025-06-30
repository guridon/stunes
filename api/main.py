from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.models.schemas import *
from src.services.search_service import search_service
from src.services.rag_service import rag_service
from src.core.database import get_database
import time
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered Music Search and Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/health")
async def health_check():
    db = get_database()
    db_healthy = db.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": time.time()
    }

@app.post("/api/search", response_model=SearchResponse)
async def search_songs(request: SearchRequest):
    start_time = time.time()
    try:
        if request.search_type == "rag":
            # response_text, songs = rag_service.query(request.query)
            try:
                response_text, songs = rag_service.query(request.query)
            except Exception as e:
                logger.error(f"RAG query failed: {e}")
                response_text = "Error in RAG processing"  # 기본값 할당
            return SearchResponse(
                songs=songs,
                rag_response=response_text,
                total_count=len(songs),
                search_type=request.search_type,
                query=request.query,
                execution_time=time.time() - start_time
            )
        else:
            songs = search_service.search(request)
            return SearchResponse(
                songs=songs,
                rag_response=None,
                total_count=len(songs),
                search_type=request.search_type,
                query=request.query,
                execution_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/chat", response_model=ChatResponse)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
