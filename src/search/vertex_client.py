# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        self.data_store_id = os.getenv("DATA_STORE_ID")
        self.engine_id = os.getenv("ENGINE_ID")

        if not all([self.project_id, self.location, self.data_store_id]):
            logger.error("Missing one or more environment variables: PROJECT_ID, LOCATION, DATA_STORE_ID")
            raise ValueError("Missing required environment variables for VertexSearchClient.")

        # Set the API endpoint based on the location from .env
        self.api_endpoint = f"{self.location}-discoveryengine.googleapis.com"
        self.client_options = ClientOptions(api_endpoint=self.api_endpoint)

        logger.info(f"VertexSearchClient initializing with endpoint: {self.api_endpoint}")
        self.search_client = discoveryengine.SearchServiceClient(client_options=self.client_options)
        
        # Construct the serving_config path to target the data store directly
        # The serving config depends on whether an Engine is being used.
        if self.engine_id:
            # Use the Engine-based serving config. The 'serving_config_path' helper on the
            # SearchServiceClient only supports data stores, so we construct the engine-based path manually.
            self.serving_config = (
                f"projects/{self.project_id}/locations/{self.location}/collections/default_collection/"
                f"engines/{self.engine_id}/servingConfigs/default_config"
            )
        else:
            # Use the Data Store-based serving config.
            self.serving_config = self.search_client.serving_config_path(
                project=self.project_id,
                location=self.location,
                data_store=self.data_store_id,
                serving_config="default_config",
            )
        logger.info(f"Using serving config: {self.serving_config}")
        logger.info("VertexSearchClient initialized.")

    def search(self, query: str) -> str:
        """
        Executes a search query against the Vertex AI Search data store.
        """
        try:
            # =================================================================================================
            # HACKATHON CHALLENGE IMPLEMENTATION: HYBRID SEARCH
            #
            # Enhanced search combining keyword-based search with semantic search capabilities
            # using Vertex AI Search's query expansion and spell correction features.
            # =================================================================================================

            # Enhanced content search specification
            content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True,
                    max_snippet_count=3,  # Return more snippets for better context
                ),
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=2,  # Increased for better coverage
                    max_extractive_segment_count=3,  # More segments for comprehensive results
                ),
            )

            # HYBRID SEARCH: Query expansion for semantic matching
            # This enables the search to find semantically related content beyond exact keyword matches
            query_expansion_spec = discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
                pin_unexpanded_results=True  # Keep original keyword matches while adding semantic matches
            )

            # HYBRID SEARCH: Spell correction for handling typos and medical terminology variations
            # This helps with medical terms that might be misspelled or have multiple spellings
            spell_correction_spec = discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            )

            # Build the enhanced hybrid search request
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=10,  # Increased page size for more comprehensive results
                content_search_spec=content_search_spec,
                query_expansion_spec=query_expansion_spec,  # Enable semantic search
                spell_correction_spec=spell_correction_spec,  # Enable spell correction
            )

            logger.info(f"Executing hybrid search for query: '{query}' with semantic expansion and spell correction")
            response = self.search_client.search(request)

            context_snippets = []
            for result in response.results:
                if not result.document or not result.document.derived_struct_data:
                    continue

                data = result.document.derived_struct_data

                if data.get("extractive_segments"):
                    for segment in data["extractive_segments"]:
                        context_snippets.append(segment.get("content", ""))

                if data.get("extractive_answers"):
                    for answer in data["extractive_answers"]:
                        context_snippets.append(answer.get("content", ""))

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
