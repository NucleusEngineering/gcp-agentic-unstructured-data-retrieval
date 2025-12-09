from src.search.vertex_client import VertexSearchClient
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

search_client = VertexSearchClient()

def search_knowledge_base(query: str) -> str:
    """
    Searches the Nelly Hackathon knowledge base to find information and answer user questions.

    Args:
        query: A detailed search query crafted from the user's question.
    """
    logger.info(f"Tool call: search_knowledge_base with query: {query}")
    return search_client.search(query)
