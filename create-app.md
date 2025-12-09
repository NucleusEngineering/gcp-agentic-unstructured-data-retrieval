# Infrastructure Task: Create Enterprise Search Engine

## Context & Rationale

### The Problem: "Standard" Tier Limitations
Our RAG Agent is currently connected directly to a **Standard Edition** Data Store. While the agent can "find" the document, it cannot "read" the specific content required to answer user questions.

* **Current Behavior:** The agent returns generic refusals ("I do not have information about technical details") because the API only provides a 1-2 sentence summary (snippet) of the document.
* **The "Librarian" Metaphor:** The current setup is like a librarian who only reads the book's title and back cover. They know the book exists, but they cannot open it to answer specific questions about Chapter 3.
* **Technical Root Cause:** Standard Edition does not support **`extractive_segments`**. This feature is required to extract actual paragraphs and text chunks from unstructured files (PDFs) to feed into the LLM context window.

### The Solution: Enterprise Edition App
To fix this, we must wrap our existing Data Store in an **Enterprise Edition App (Engine)**.

* **Unlocks RAG:** Enables `extractive_segments` and `extractive_answers`.
* **Fixes API Errors:** Resolves the `400 Bad Request` error we encountered when our Python code tried to request text chunks from the Standard engine.
* **No Re-indexing Needed:** We do not need to re-upload the PDF. We simply link the new "Brain" (Enterprise Engine) to the existing "Memory" (Data Store).

## Technical Specifications
* **Goal:** Create a Vertex AI Search Engine (App).
* **Region:** `eu` (Must match the Data Store location).
* **Edition:** `ENTERPRISE` (Required for RAG/LLM features).
* **Existing Data Store ID:** `nelly-vertex-search-datastore`
* **New Engine ID:** `nelly-search-app`

## Implementation Script

Create a file named `scripts/create_enterprise_engine.py` with the following content. This script uses the `google-cloud-discoveryengine` library to provision the resource programmatically.

```python
import os
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

# --- Configuration ---
# You can modify these or load them from os.environ
PROJECT_ID = "tony-allen"
LOCATION = "eu"  # Important: Must match your Data Store location
DATA_STORE_ID = "nelly-vertex-search-datastore"
ENGINE_ID = "nelly-search-app"

def create_engine():
    print(f"🚀 Initializing Engine Creation for: {ENGINE_ID} in {LOCATION}...")

    # 1. Configure Client with Regional Endpoint
    # EU resources require the specific eu-discoveryengine endpoint
    api_endpoint = f"{LOCATION}-discoveryengine.googleapis.com" if LOCATION != "global" else None
    client_options = ClientOptions(api_endpoint=api_endpoint) if api_endpoint else None
    
    client = discoveryengine.EngineServiceClient(client_options=client_options)

    # 2. Define the Enterprise Engine
    # We explicitly enable ENTERPRISE tier and LLM add-ons for RAG
    engine = discoveryengine.Engine(
        display_name="Nelly Hackathon Enterprise Search",
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        data_store_ids=[DATA_STORE_ID],
        search_engine_config=discoveryengine.Engine.SearchEngineConfig(
            search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
            search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
        ),
    )

    # 3. Construct the Parent Resource Path
    # Format: projects/{project}/locations/{location}/collections/{collection}
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"

    # 4. Execute Creation Request
    request = discoveryengine.CreateEngineRequest(
        parent=parent,
        engine=engine,
        engine_id=ENGINE_ID,
    )

    try:
        operation = client.create_engine(request=request)
        print("⏳ Operation submitted. Waiting for completion (this takes 1-2 mins)...")
        response = operation.result()
        print("✅ Enterprise Engine Created Successfully!")
        print(f"   Name: {response.name}")
        print(f"   ID: {ENGINE_ID}")
    except Exception as e:
        print(f"❌ Error creating engine: {e}")

if __name__ == "__main__":
    create_engine()



## Execution Instructions

1.  **Run the script:**
    ```bash
    poetry run python scripts/create_enterprise_engine.py
    ```

2.  **Update Application Config (Critical Step):**
    Once the script finishes successfully, the application code must be updated to point to the new **Engine** resource instead of the raw Data Store.

    * **File:** `src/search/vertex_client.py`
    * **Action:** Update the `serving_config` path construction.
    * **Old Path (Standard):** `.../dataStores/nelly-vertex-search-datastore/...`
    * **New Path (Enterprise):** `.../collections/default_collection/engines/nelly-search-app/...`