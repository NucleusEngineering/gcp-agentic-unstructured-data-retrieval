#!/bin/bash

# --- Configuration ---
# Source environment variables from .env file if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Validate that the required environment variables are set
if [ -z "${PROJECT_ID}" ] || [ -z "${LOCATION}" ] || [ -z "${DATA_STORE_ID}" ]; then
  echo "ERROR: One or more required environment variables are not set."
  echo "Please ensure PROJECT_ID, LOCATION, and DATA_STORE_ID are defined in your .env file."
  exit 1
fi

DISPLAY_NAME="Nelly Hackathon DataStore" # This can remain as a default
DEFAULT_COLLECTION="default_collection"

# --- 1. Authenticate with Google Cloud ---
echo "Ensuring gcloud is authenticated..."
if ! gcloud auth print-access-token > /dev/null 2>&1; then
  echo "You are not logged in. Please run 'gcloud auth application-default login'."
  gcloud auth application-default login
  if ! gcloud auth print-access-token > /dev/null 2>&1; then
    echo "Authentication failed. Exiting."
    exit 1
  fi
fi
echo "Authentication successful."

# --- 2. Construct the API Endpoint and URL for DataStore Creation ---
API_ENDPOINT="${LOCATION}-discoveryengine.googleapis.com"
CREATE_DS_URL="https://${API_ENDPOINT}/v1/projects/${PROJECT_ID}/locations/${LOCATION}/collections/${DEFAULT_COLLECTION}/dataStores?dataStoreId=${DATA_STORE_ID}"

# --- 3. Define the DataStore Payload ---
CREATE_DS_PAYLOAD='{
  "displayName": "'"${DISPLAY_NAME}"'",
  "industryVertical": "GENERIC",
  "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
  "contentConfig": "CONTENT_REQUIRED"
}'

# --- 4. Send the Request to Create the DataStore ---
echo ""
echo "--- Attempting to create Discovery Engine DataStore '${DATA_STORE_ID}' in '${LOCATION}' ---"
echo "Using Project ID: ${PROJECT_ID}"
echo "API URL: ${CREATE_DS_URL}"
echo "Payload: ${CREATE_DS_PAYLOAD}"
echo ""

CREATE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "${CREATE_DS_URL}" \
  -d "${CREATE_DS_PAYLOAD}")

# --- 5. Check the Response ---
if echo "${CREATE_RESPONSE}" | grep -q "error"; then
  echo "ERROR: Failed to create DataStore."
  echo "${CREATE_RESPONSE}"
  if echo "${CREATE_RESPONSE}" | grep -q "already exists"; then
    echo "The DataStore '${DATA_STORE_ID}' in '${LOCATION}' already exists."
  fi
else
  echo "Successfully initiated DataStore creation."
  echo "${CREATE_RESPONSE}"
fi
