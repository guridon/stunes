from functools import cache, lru_cache
from typing import List, Dict, Any
from src.core.database import get_database
from src.models.schemas import SongInfo, SearchRequest
# from src.utils.cache import cached
import logging
import time

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.db = get_database()
    @cache 
    def search_by_title(self, query: str, limit: int = 10) -> List[SongInfo]:
        search_query = """
        MATCH (s:Song)
        WHERE toLower(s.title) CONTAINS toLower($query)
        WITH DISTINCT s
        OPTIONAL MATCH (s)-[:PERFORMED_BY]-(a:Artist)
        OPTIONAL MATCH (s)-[:HAS_GENRE]-(g:Genre)
        OPTIONAL MATCH (s)-[:IN_ALBUM]-(al:Album)
        OPTIONAL MATCH (g)-[:CONTAINS]-(sg:SubGenre)
        WITH s, 
             head(collect(DISTINCT a)) as artist,
             head(collect(DISTINCT g)) as genre,
             head(collect(DISTINCT al)) as album,
             head(collect(DISTINCT sg)) as subgenre
        RETURN s.song_id AS song_id,
               s.title AS title,
               s.issue_date AS issue_date,
               artist.name AS artist_name,
               artist.artist_id AS artist_id,
               genre.name AS genre_name,
               genre.genre_id AS genre_id,
               album.title AS album_title,
               album.album_id AS album_id,
               subgenre.name AS subgenre_name
        ORDER BY s.title
        LIMIT $limit
        """
        try:
            start_time = time.time()
            results = self.db.graph.query(search_query, params={"query": query, "limit": limit})
            execution_time = time.time() - start_time
            
            logger.info(f"Title search for '{query}' returned {len(results)} results in {execution_time:.2f}s")
            
            return [SongInfo(**result) for result in results]
        except Exception as e:
            logger.error(f"Error in title search: {e}")
            return []
        
    @cache
    def search_by_song_id(self, song_id: str) -> List[SongInfo]:
        search_query = """
        MATCH (s:Song {song_id: $song_id})
        OPTIONAL MATCH (s)-[:PERFORMED_BY]-(a:Artist)
        OPTIONAL MATCH (s)-[:HAS_GENRE]-(g:Genre)
        OPTIONAL MATCH (s)-[:IN_ALBUM]-(al:Album)
        OPTIONAL MATCH (g)-[:CONTAINS]-(sg:SubGenre)
        WITH s, 
             head(collect(DISTINCT a)) as artist,
             head(collect(DISTINCT g)) as genre,
             head(collect(DISTINCT al)) as album,
             head(collect(DISTINCT sg)) as subgenre
        RETURN s.song_id AS song_id,
               s.title AS title,
               s.issue_date AS issue_date,
               artist.name AS artist_name,
               artist.artist_id AS artist_id,
               genre.name AS genre_name,
               genre.genre_id AS genre_id,
               album.title AS album_title,
               album.album_id AS album_id,
               subgenre.name AS subgenre_name
        """
        try:
            start_time = time.time()
            results = self.db.graph.query(search_query, params={"song_id": song_id})
            execution_time = time.time() - start_time
            
            logger.info(f"ID search for '{song_id}' returned {len(results)} results in {execution_time:.4f}s")
            
            return [SongInfo(**result) for result in results]
        except Exception as e:
            logger.error(f"Error in ID search: {e}")
            return []
    
    @cache
    def search_by_artist(self, query: str, limit: int = 10) -> List[SongInfo]:
        """아티스트명으로 검색"""
        search_query = """
        MATCH (a:Artist)
        WHERE toLower(a.name) CONTAINS toLower($query)
        WITH DISTINCT a
        OPTIONAL MATCH (a)-[:PERFORMED_BY]-(s:Song)
        OPTIONAL MATCH (s)-[:HAS_GENRE]-(g:Genre)
        OPTIONAL MATCH (s)-[:IN_ALBUM]-(al:Album)
        OPTIONAL MATCH (g)-[:CONTAINS]-(sg:SubGenre)
        WITH s, a,
             head(collect(DISTINCT g)) as genre,
             head(collect(DISTINCT al)) as album,
             head(collect(DISTINCT sg)) as subgenre
        WHERE s IS NOT NULL
        RETURN s.song_id AS song_id,
               s.title AS title,
               s.issue_date AS issue_date,
               a.name AS artist_name,
               a.artist_id AS artist_id,
               genre.name AS genre_name,
               genre.genre_id AS genre_id,
               album.title AS album_title,
               album.album_id AS album_id,
               subgenre.name AS subgenre_name
        ORDER BY s.title
        LIMIT $limit
        """
        try:
            start_time = time.time()
            results = self.db.graph.query(search_query, params={"query": query, "limit": limit})
            execution_time = time.time() - start_time
            
            logger.info(f"Artist search for '{query}' returned {len(results)} results in {execution_time:.2f}s")
            
            return [SongInfo(**result) for result in results]
        except Exception as e:
            logger.error(f"Error in artist search: {e}")
            return []

    def search(self, request: SearchRequest) -> List[SongInfo]:
        if request.search_type == "title":
            return self.search_by_title(request.query, request.limit)
        elif request.search_type == "artist":
            return self.search_by_artist(request.query, request.limit)
        else:
            raise ValueError(f"Unsupported search type: {request.search_type}")

search_service = SearchService()