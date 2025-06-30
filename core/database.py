from langchain_neo4j import Neo4jGraph
from functools import lru_cache
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._graph = None
    
    @property
    def graph(self) -> Neo4jGraph:
        if self._graph is None:
            try:
                self._graph = Neo4jGraph(
                    url=settings.neo4j_uri,
                    username=settings.neo4j_username,
                    password=settings.neo4j_password,
                )
                self._graph.refresh_schema()
                logger.info("Neo4j connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                raise
        return self._graph
    
    def health_check(self) -> bool:
        try:
            result = self.graph.query("RETURN 1 as test")
            return len(result) > 0
        except Exception:
            return False

@lru_cache()
def get_database() -> DatabaseManager:
    return DatabaseManager()
