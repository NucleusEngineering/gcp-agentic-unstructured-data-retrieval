Here is the revised **Infrastructure Setup Guide**, formatted for clarity and consistency with the previous document.

-----

# Infrastructure Setup Guide

This guide provides the necessary scripts and instructions to provision the Google Cloud infrastructure. The setup follows a two-step hierarchical process:

1.  **Create a Vertex AI Search Data Store:** Storage and indexing for unstructured docs (PDFs).
2.  **Create an Enterprise Search App (Engine):** The serving layer that provides advanced RAG capabilities (like `extractive_segments`).

-----

## Step 1: Create the Vertex AI Search Data Store

This script creates the foundational Data Store where your documents will live.

### Instructions

1.  **Configure Environment:** Ensure your `.env` file contains your `PROJECT_ID`, `LOCATION`, and a unique `DATA_STORE_ID`.
2.  **Authenticate:** Run `gcloud auth application-default login` if you haven't already.
3.  **Run Script:** Execute the following from the project root:

<!-- end list -->

```bash
bash scripts/create_datastore.sh
```

> **Note:** The script will automatically use variables from your `.env` file to target the correct project and location.

-----

## Step 2: Create the Enterprise Search App (Engine)

This script wraps the Data Store from Step 1 in an Enterprise-tier App, unlocking the specific features required for the RAG agent.

### Instructions

1.  **Verify Configuration:** Check the top of `scripts/create_enterprise_engine.py` to ensure `PROJECT_ID`, `LOCATION`, and `DATA_STORE_ID` match the resources created in Step 1.
2.  **Run Script:** Execute the Python script via poetry:

<!-- end list -->

```bash
poetry run python scripts/create_enterprise_engine.py
```

  * *Time Estimate: This process typically takes 1-2 minutes.*

-----

## Application Code

Once the Enterprise App is live, you must manually point your application code to the new Engine resource.

**Target File:** `src/search/vertex_client.py`

```python
self.serving_config = self.search_client.serving_config_path(
    project=self.project_id,
    location=self.location,
    collection="default_collection",
    engine=os.getenv("ENGINE_ID"), # Ensure ENGINE_ID is added to your .env
    serving_config="default_config",
)
```

-----
