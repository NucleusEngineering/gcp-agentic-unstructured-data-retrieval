import sys
import os
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import NotFound
from google.cloud import discoveryengine_v1 as discoveryengine

from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
ENGINE_ID = os.getenv("ENGINE_ID")
APP_NAME = os.getenv("APP_NAME", "GenAI-RAG")

if not all([PROJECT_ID, LOCATION, DATA_STORE_ID, ENGINE_ID]):
    raise ValueError(
        "Missing one or more required environment variables: "
        "PROJECT_ID, LOCATION, DATA_STORE_ID, ENGINE_ID"
    )

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
        display_name=f"{os.getenv('APP_NAME', 'GenAI-RAG')} Hackathon Enterprise Search",
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

    # Check if the engine already exists
    try:
        engine_path = client.engine_path(
            project=PROJECT_ID,
            location=LOCATION,
            collection="default_collection",
            engine=ENGINE_ID,
        )
        client.get_engine(name=engine_path)
        print(f"✅ Engine '{ENGINE_ID}' already exists. Continuing.")
        return
    except NotFound:
        print(f"Engine '{ENGINE_ID}' not found. Proceeding with creation...")
    except Exception as e:
        print(f"❌ An unexpected error occurred while checking for the engine: {e}")
        sys.exit(1)

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
        sys.exit(1)

if __name__ == "__main__":
    create_engine()
