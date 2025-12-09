import os
from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
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
        self.engine_id = os.getenv("ENGINE_ID")

        if not all([self.project_id, self.location, self.engine_id]):
            logger.error("Missing one or more environment variables: PROJECT_ID, LOCATION, ENGINE_ID")
            raise ValueError("Missing required environment variables for VertexSearchClient.")

        # Set the API endpoint based on the location from .env
        self.api_endpoint = f"{self.location}-discoveryengine.googleapis.com"
        self.client_options = ClientOptions(api_endpoint=self.api_endpoint)

        logger.info(f"VertexSearchClient initializing with endpoint: {self.api_endpoint}")
        self.search_client = discoveryengine.SearchServiceClient(client_options=self.client_options)
        
        # Construct the serving_config path for the Enterprise Edition App (Engine)
        # We need to instantiate an EngineServiceClient to use its path helper
        self.serving_config = (
            f"projects/{self.project_id}"
            f"/locations/{self.location}"
            f"/collections/default_collection"
            f"/engines/{self.engine_id}"
            f"/servingConfigs/default_config"
        )
        logger.info(f"Using serving config: {self.serving_config}")
        logger.info("VertexSearchClient initialized.")

    def search(self, query: str) -> str:
        """
        Executes a search query against the Vertex AI Search data store.
        """
        try:
            content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True
                ),
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=1,
                    max_extractive_segment_count=1,
                ),
            )

            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=5,
                content_search_spec=content_search_spec,
            )
            response = self.search_client.search(request)

            context_snippets = []
            for result in response.results:
                if not result.document or not result.document.derived_struct_data:
                    continue

                data = result.document.derived_struct_data

                # Debug: Print available keys to see where the data is hiding
                logger.info(f"Document keys found: {list(data.keys())}")

                # 1. Collect Extractive Segments (Priority: High - contains full paragraphs)
                if data.get("extractive_segments"):
                    for segment in data["extractive_segments"]:
                        context_snippets.append(segment.get("content", ""))

                # 2. Collect Extractive Answers (Priority: Medium - specific facts)
                if data.get("extractive_answers"):
                    for answer in data["extractive_answers"]:
                        context_snippets.append(answer.get("content", ""))

                # 3. Fallback to Snippets only if no better context was found
                if not context_snippets and data.get("snippets"):
                    for snippet in data["snippets"]:
                        context_snippets.append(snippet.get("snippet", ""))

            # Filter out any potential empty strings from the results
            context_snippets = [s for s in context_snippets if s]

            consolidated_context = "\n\n".join(context_snippets)
            logger.info(f"Search query '{query}' returned {len(context_snippets)} context snippets.")
            return consolidated_context if consolidated_context else "No relevant documents found."

        except Exception as e:
            logger.error(f"Error during Vertex AI Search for query '{query}': {e}")
            return "Error retrieving documents from Vertex AI Search."

    def import_from_gcs(self, gcs_uri: str):
        """
        Imports documents from a GCS URI into the Vertex AI Search data store.
        """
        try:
            document_service_client = discoveryengine.DocumentServiceClient(client_options=self.client_options)
            parent = document_service_client.branch_path(
                project=self.project_id,
                location=self.location,
                data_store=self.data_store_id,
                branch="default_branch",
            )

            request = discoveryengine.ImportDocumentsRequest(
                parent=parent,
                gcs_source=discoveryengine.GcsSource(
                    input_uris=[gcs_uri],
                    data_schema="document"
                ),
                reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
            )

            operation = document_service_client.import_documents(request=request)
            logger.info(f"Waiting for document import from GCS to complete: {operation.operation.name}")
            response = operation.result()
            
            metadata = operation.metadata
            logger.info("Document import from GCS completed successfully.")
            logger.info(f"Success count: {metadata.success_count}")
            logger.info(f"Failure count: {metadata.failure_count}")
            if metadata.failure_count > 0:
                # Note: Error samples are in the response, not metadata
                for i, sample in enumerate(response.error_samples):
                    logger.error(f"Error sample {i+1}: {sample}")

        except Exception as e:
            logger.error(f"Error during GCS import to Vertex AI Search: {e}")
            raise
