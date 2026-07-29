# Search

This directory contains the modules responsible for interacting with the search and retrieval systems, such as Vertex AI Search. It encapsulates the client logic for executing search queries.

## Files

-   `vertex_client.py`: This file provides a dedicated `VertexSearchClient` class that acts as a high-level abstraction for the Vertex AI Search service.
    -   The `search` method is called by the agent's tools to perform queries against the indexed data.
    -   The `import_from_gcs` method is called by the ingestion pipeline to load new documents into the data store.