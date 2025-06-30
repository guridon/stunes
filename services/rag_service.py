# src/services/rag_service.py - 검증된 search_service 활용
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from src.core.database import get_database
from src.core.config import settings
from src.services.search_service import search_service
from src.models.schemas import SongInfo
from typing import List, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.db = get_database()
        self.llm = ChatOpenAI(
            temperature=0, 
            model="gpt-4o",
            openai_api_key=settings.openai_api_key
        )
        
        self.cypher_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.db.graph,
            verbose=True,
            return_direct=False,
            return_intermediate_steps=True, 
            allow_dangerous_requests=True,
            top_k=settings.rag_top_k
        )
    def extract_title(self, results: str) -> List[str]:
        pattern = r"'([^']*)'"
        song_titles = re.findall(pattern, results)
        return song_titles

    def search_details(self, song_ids: List[str]) -> List[SongInfo]:
        songs=[]
        for id in song_ids:
            song_details = search_service.search_by_song_id(id)
            songs.extend(song_details)
        return songs
    
    def query(self, question: str) -> Tuple[str, List[SongInfo]]:
        final_question=f"{question}. 반드시 song_id를 함께 반환해주세요."
        try:
            rag_results=self.cypher_chain.invoke(
                {"query": final_question},
            )
            song_ids=[song.get("s.song_id") for song in rag_results["intermediate_steps"][1]["context"]]

            # song_titles = self.extract_title(rag_results["result"])
            songs = self.search_details(song_ids)
            return rag_results["result"], songs

        except Exception as e:
            logger.error(f"❌ Error in RAG query: {e}")
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}", []

rag_service = RAGService()