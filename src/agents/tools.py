from src.search.vertex_client import VertexSearchClient
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

def retrieve_documents(query: str) -> str:
    """
    Retrieves relevant documents using the VertexSearchClient.

    Args:
        query (str): The search query.

    Returns:
        str: Consolidated context from retrieved documents.
    """
    logger.info(f"Tool call: retrieve_documents with query: {query}")
    vertex_search_client = VertexSearchClient()
    return vertex_search_client.search(query)
