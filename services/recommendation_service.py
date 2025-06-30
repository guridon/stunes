from functools import cache, lru_cache
from typing import List, Dict, Any
from src.core.database import get_database
from src.models.schemas import SongInfo
# from src.utils.cache import cached
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.db = get_database()
    
    @cache 
    def recommend_by_genre(self, song_id: str, limit: int = 5) -> List[SongInfo]:
        query = """
        MATCH (s:Song {song_id: $song_id})-[:HAS_GENRE]-(g:Genre)-[:HAS_GENRE]-(rec:Song)
        WHERE s.song_id <> rec.song_id
        WITH DISTINCT rec
        OPTIONAL MATCH (rec)-[:PERFORMED_BY]-(a:Artist)
        OPTIONAL MATCH (rec)-[:HAS_GENRE]-(rg:Genre)
        OPTIONAL MATCH (rec)-[:IN_ALBUM]-(al:Album)
        RETURN rec.song_id AS song_id,
               rec.title AS title,
               rec.issue_date AS issue_date,
               a.name AS artist_name,
               a.artist_id AS artist_id,
               rg.name AS genre_name,
               rg.genre_id AS genre_id,
               al.title AS album_title,
               al.album_id AS album_id
        ORDER BY RAND()
        LIMIT $limit
        """
        
        try:
            results = self.db.graph.query(query, params={"song_id": song_id, "limit": limit})
            return [SongInfo(**result) for result in results]
        except Exception as e:
            logger.error(f"Error in genre-based recommendation: {e}")
            return []
    
    @cache
    def recommend_by_artist(self, song_id: str, limit: int = 5) -> List[SongInfo]:
        query = """
        MATCH (s:Song {song_id: $song_id})-[:PERFORMED_BY]-(a:Artist)-[:PERFORMED_BY]-(rec:Song)
        WHERE s.song_id <> rec.song_id
        WITH DISTINCT rec, a
        OPTIONAL MATCH (rec)-[:HAS_GENRE]-(g:Genre)
        OPTIONAL MATCH (rec)-[:IN_ALBUM]-(al:Album)
        RETURN rec.song_id AS song_id,
               rec.title AS title,
               rec.issue_date AS issue_date,
               a.name AS artist_name,
               a.artist_id AS artist_id,
               g.name AS genre_name,
               g.genre_id AS genre_id,
               al.title AS album_title,
               al.album_id AS album_id
        ORDER BY rec.issue_date DESC
        LIMIT $limit
        """
        
        try:
            results = self.db.graph.query(query, params={"song_id": song_id, "limit": limit})
            return [SongInfo(**result) for result in results]
        except Exception as e:
            logger.error(f"Error in artist-based recommendation: {e}")
            return []
    
    def get_popular_songs(self, limit: int = 10) -> List[SongInfo]:
        query = """
        MATCH (s:Song)-[:INCLUDES]-(p:Playlist)
        WITH s, count(p) as playlist_count
        ORDER BY playlist_count DESC
        LIMIT $limit
        WITH DISTINCT s
        OPTIONAL MATCH (s)-[:PERFORMED_BY]-(a:Artist)
        OPTIONAL MATCH (s)-[:HAS_GENRE]-(g:Genre)
        OPTIONAL MATCH (s)-[:IN_ALBUM]-(al:Album)
        RETURN s.song_id AS song_id,
               s.title AS title,
               s.issue_date AS issue_date,
               a.name AS artist_name,
               a.artist_id AS artist_id,
               g.name AS genre_name,
               g.genre_id AS genre_id,
               al.title AS album_title,
               al.album_id AS album_id
        """
        
        try:
            results = self.db.graph.query(query, params={"limit": limit})
            return [SongInfo(**result) for result in results]
        except Exception as e:
            logger.error(f"Error getting popular songs: {e}")
            return []

recommendation_service = RecommendationService()
