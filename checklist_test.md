# Project Recreation Checklist

This checklist outlines the steps to set up the project from scratch in a new Google Cloud project.

## 1. Local Machine Setup

- [ ] **Clone the repository:**
  ```bash
  git clone https://github.com/Ben-Cliff/gcp-agentic-unstructured-data-retrieval.git
  cd gcp-agentic-unstructured-data-retrieval
  ```
- [ ] **Install Python dependencies:**
  ```bash
  poetry install
  ```
- [ ] **Authenticate with Google Cloud:**
  ```bash
  gcloud auth application-default login
  ```

## 2. Configure Environment

- [ ] **Create `.env` file:**
  ```bash
  cp .env.example .env
  ```
- [ ] **Update `.env` with new project details:**

  > **⚠️ Important:**
  > 1.  Ensure your `PROJECT_ID` is correct and that the project exists.
  > 2.  Your `GCS_BUCKET_NAME` must be **globally unique**. A good practice is to append your project ID to the name (e.g., `my-app-bucket-your-project-id`).
  > 3.  **Do not** use quotes (single or double) around the values in your `.env` file.

  - `PROJECT_ID`: `unstructured-data-hack-test`
  - `LOCATION`: (e.g., `eu` or `us`)
  - `APP_NAME`: A unique name for this deployment (e.g., `my-test-app`)
  - `DATA_STORE_ID`: A unique ID for the data store (e.g., `unstructured-data-hack-test-ds`)
  - `ENGINE_ID`: A unique ID for the search engine (e.g., `unstructured-data-hack-test-engine`)
  - `GCS_BUCKET_NAME`: A globally unique name for your GCS bucket (e.g., `unstructured-data-hack-test-bucket`)
  - `VERTEX_AI_REGION`: The same value as `LOCATION`.

  > **Note:** Below is an example of a complete, working configuration for reference.
  > ```env
  > PROJECT_ID="tony-allen"
  > LOCATION="eu"
  > DATA_STORE_ID="nelly-vertex-search-datastore"
  > ENGINE_ID="nelly-search-app"
  > VERTEX_AI_REGION="europe-west1"
  > GCS_BUCKET_NAME="tony-allen-nelly-hackathon-datastore"
  > APP_NAME="Nelly"
  > ```

## 3. Provision Google Cloud Infrastructure

- [ ] **Run the infrastructure setup script:**
  ```bash
  make infra
  ```
  *This command will create the GCS Bucket, Vertex AI Search Data Store, and the Enterprise Search App (Engine).*

## 4. Data Ingestion

- [ ] **Generate or add data:**
  - **Option A (Generate):** Run the script to create mock data.
    ```bash
    poetry run python scripts/generate_data.py
    ```
  - **Option B (Add your own):** Place your PDF files in the `data/raw` directory.
- [ ] **Run the ingestion pipeline:**
  ```bash
  poetry run python main.py --mode ingest
  ```

## 5. Test the Application

- [ ] **Start the chat interface:**
  ```bash
  poetry run python main.py --mode chat
  ```
- [ ] **Ask a question:** Interact with the chatbot to verify it can retrieve information from the documents you ingested.
