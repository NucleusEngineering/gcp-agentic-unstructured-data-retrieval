from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

VALID_LOCATIONS = {"us", "eu", "global"}

def validate_datastore(project_id: str, location: str, data_store_id: str) -> bool:
    """
    Verifies that a specific DataStore ID exists in the given project and location.

    Args:
        project_id: The Google Cloud project ID.
        location: The Discovery Engine location ('us', 'eu', or 'global').
        data_store_id: The ID of the datastore to verify.

    Returns:
        True if the datastore exists, otherwise raises a ValueError.
    """
    if location not in VALID_LOCATIONS:
        raise ValueError(f"Invalid LOCATION '{location}'. Must be one of {', '.join(VALID_LOCATIONS)}. Please correct your .env file.")

    logger.info(f"Validating DataStore '{data_store_id}' in project '{project_id}' at location '{location}'...")
    try:
        if location == "global":
            client_options = None
        else:
            api_endpoint = f"{location}-discoveryengine.googleapis.com"
            client_options = ClientOptions(api_endpoint=api_endpoint)

        client = discoveryengine.DataStoreServiceClient(client_options=client_options)  # type: ignore
        parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

        request = discoveryengine.ListDataStoresRequest(parent=parent)  # type: ignore
        response = client.list_data_stores(request)

        for datastore in response:
            # The ID is the last part of the fully qualified 'name'
            extracted_id = datastore.name.split('/')[-1]
            if extracted_id == data_store_id:
                logger.info(f"SUCCESS: Found DataStore '{datastore.display_name}' (ID: {extracted_id}).")
                return True

        raise ValueError(f"DataStore with ID '{data_store_id}' not found in location '{location}'. "
                         f"Please check your DATA_STORE_ID in the .env file or create the datastore in the Google Cloud Console.")

    except Exception as e:
        logger.error(f"An error occurred during datastore validation: {e}")
        raise
