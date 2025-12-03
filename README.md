# nelly-hackathon-mvp

A Python-based skeleton for a RAG (Retrieval-Augmented Generation) system. It handles document ingestion (PDF parsing, chunking, JSON conversion), indexing into Vertex AI Search, and a Gemini-powered Agent for querying.

## Technology Stack

*   **Language:** Python 3.10+
*   **Cloud Provider:** Google Cloud Platform (Vertex AI, Vertex AI Search)
*   **Key Libraries:** `google-cloud-discoveryengine`, `vertexai`, `pypdf`, `python-dotenv`

## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd gcp-agentic-unstructured-data-retrieval
    ```

2.  **Install [Poetry](https://python-poetry.org/docs/#installation):**
    Follow the instructions on the official Poetry website to install it on your system.

3.  **Install dependencies:**
    ```bash
    poetry install
    ```

4.  **Configure environment variables:**
    *   Copy the example `.env.example` file to a new `.env` file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your Google Cloud project details:
        ```
        PROJECT_ID="your-gcp-project-id"
        LOCATION="us-central1"
        DATA_STORE_ID="your-vertex-search-datastore-id"
        ```

5.  **Authenticate with Google Cloud:**
    *   Ensure you have the [Google Cloud SDK](httpss://cloud.google.com/sdk/docs/install) installed.
    *   Log in with your application-default credentials:
        ```bash
        gcloud auth application-default login
        ```

## Usage

The application has two modes: `ingest` and `chat`.

### Ingest Mode

This mode processes PDF files from the `data/raw` directory and prepares them for indexing.

1.  Place your PDF files into the `data/raw` directory.
2.  Run the ingestion pipeline:
    ```bash
    poetry run python main.py --mode ingest
    ```
    This will create a `processed_data.json` file in the `data/processed` directory.

### Chat Mode

This mode starts an interactive chat session with the RAG agent, allowing you to ask questions about the documents you have ingested.

```bash
poetry run python main.py --mode chat
```

## Makefile Commands

This project uses a `Makefile` to streamline common development tasks.

*   **`make install`**:
    *   Installs all project dependencies using Poetry.

*   **`make check`**:
    *   Performs a series of checks to ensure code quality and consistency:
        *   Checks for lock file consistency.
        *   Lints the code using `ruff`.
        *   Performs static type checking with `mypy`.
        *   Checks for obsolete dependencies with `deptry`.

## Testing

Once the development setup is complete, you can test the application by following these steps:

1.  **Install Dependencies:**
    If you haven't already, install the required libraries using Poetry:
    ```bash
    make install
    ```
    or
    ```bash
    poetry install
    ```

2.  **Add PDF Files:**
    Place the PDF documents you want to process into the `data/raw/` directory.

3.  **Run the Ingestion Pipeline:**
    Use the `ingest` mode to parse, chunk, and process your PDFs.
    ```bash
    poetry run python main.py --mode ingest
    ```
    After the process completes, a `processed_data.json` file will be created in the `data/processed/` directory. This file is not yet uploaded to Vertex AI Search.

4.  **Start the Chatbot:**
    Run the `chat` mode to interact with the RAG agent. The agent will use the documents indexed in your Vertex AI Search datastore to answer questions.
    ```bash
    poetry run python main.py --mode chat
    ```
