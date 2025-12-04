import os
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1 as discoveryengine
from src.shared.logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()

class VertexSearchClient:
    """
    Handles search queries to Vertex AI Search.
    """
    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID")
        self.location = os.getenv("LOCATION")
        self.data_store_id = os.getenv("DATA_STORE_ID")

        if not all([self.project_id, self.location, self.data_store_id]):
            logger.error("Missing one or more environment variables: PROJECT_ID, LOCATION, DATA_STORE_ID")
            raise ValueError("Missing required environment variables for VertexSearchClient.")

        self.client = discoveryengine.SearchServiceClient()
        self.serving_config = self.client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default"
        )
        logger.info("VertexSearchClient initialized.")

    def search(self, query: str) -> str:
        """
        Executes a search query against the Vertex AI Search data store.

        Args:
            query (str): The search query string.

        Returns:
            str: A consolidated string of "Context" to feed the LLM.
        """
        try:
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=5  # Limit to 5 results for brevity
            )
            response = self.client.search(request)

            context_snippets = []
            for result in response.results:
                if result.document and result.document.derived_struct_data:
                    # Extract snippet from the document if available
                    snippet = result.document.derived_struct_data.get("snippet", "")
                    if snippet:
                        context_snippets.append(snippet)
                    else:
                        # Fallback to content if no specific snippet
                        content = result.document.derived_struct_data.get("content", "")
                        if content:
                            context_snippets.append(content)

            consolidated_context = "\n\n".join(context_snippets)
            logger.info(f"Search query '{query}' returned {len(context_snippets)} context snippets.")
            return consolidated_context if consolidated_context else "No relevant documents found."

        except Exception as e:
            logger.error(f"Error during Vertex AI Search for query '{query}': {e}")
            return "Error retrieving documents from Vertex AI Search."
