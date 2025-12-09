# Infrastructure Setup Guide

This guide provides the necessary scripts and instructions to provision the required Google Cloud infrastructure for this application. The setup is a two-step process:

1.  **Create a Vertex AI Search Data Store:** This is the "memory" where your unstructured documents (PDFs) will be stored and indexed.
2.  **Create an Enterprise Search App (Engine):** This is the "brain" that sits on top of the Data Store and provides the advanced RAG capabilities (`extractive_segments`) needed by the agent.

---

## Step 1: Create the Vertex AI Search Data Store

This script creates the foundational Data Store where your documents will live.

### Instructions

1.  **Ensure your `.env` file is configured** with your `PROJECT_ID`, `LOCATION`, and a unique `DATA_STORE_ID`.
2.  **Authenticate with gcloud:** If you haven't already, run `gcloud auth application-default login`.
3.  **Run the script from the project root:**

    ```bash
    bash scripts/create_datastore.sh
    ```

The script will use the variables from your `.env` file to create the Data Store in the correct project and location.

---

## Step 2: Create the Enterprise Search App (Engine)

This script wraps the Data Store you created in Step 1 with an Enterprise-tier App, unlocking the necessary features for the RAG agent to extract meaningful context from your documents.

### Instructions

1.  **Verify the configuration** at the top of the `scripts/create_enterprise_engine.py` file to ensure the `PROJECT_ID`, `LOCATION`, and `DATA_STORE_ID` match the resources from Step 1.
2.  **Run the script from the project root:**

    ```bash
    poetry run python scripts/create_enterprise_engine.py
    ```

This process can take 1-2 minutes to complete.

### Critical Final Step: Update Application Code

After the Enterprise App is created, you must update the application's code to point to it.

*   **File:** `src/search/vertex_client.py`
*   **Action:** In the `__init__` method, find the line that defines `self.serving_config` and update it to point to the new **Engine** resource.

    *   **Old Path (Standard):**
        ```python
        self.serving_config = self.search_client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default_config",
        )
        ```

    *   **New Path (Enterprise):**
        ```python
        self.serving_config = self.search_client.serving_config_path(
            project=self.project_id,
            location=self.location,
            collection="default_collection",
            engine=os.getenv("ENGINE_ID"), # Assumes you add ENGINE_ID to your .env
            serving_config="default_config",
        )
        ```
