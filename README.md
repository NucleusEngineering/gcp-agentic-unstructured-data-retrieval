# Extensible RAG Agent with Vertex AI Search

This repository provides a robust, production-ready foundation for a Retrieval-Augmented Generation (RAG) system built on Google Cloud. It uses the Google Agent Development Kit (ADK) to power a conversational agent that can reason over unstructured data, like PDFs, that has been indexed in Vertex AI Search.

The codebase is designed to be both a functional starting point and a launchpad for further extension. It currently handles PDF ingestion and provides a basic chat interface, with clear `TODO` markers and challenges for developers to enhance its capabilities.

---

## Project Documentation

This `README` provides a general overview and setup instructions. For more detailed information, please refer to the following documents:

-   **[INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md):** A step-by-step guide to provision the necessary Google Cloud resources (Vertex AI Search Data Store and Enterprise App) required to run this project.
-   **[AGENT_ARCHITECTURE.md](./AGENT_ARCHITECTURE.md):** A deep dive into the codebase, explaining how the agent is configured, how it uses tools, and how it interacts with the search client.
-   **[CHALLENGE.md](./CHALLENGE.md):** A comprehensive guide for developers looking to extend the project's functionality. It outlines specific challenges for improving data ingestion, enhancing search capabilities, and implementing advanced multi-agent systems.

---

## How It Works

The application operates in two main modes:

1.  **Ingestion (`--mode ingest`):**
    -   Scans a local directory (`data/raw`) for PDF files.
    -   Uploads the files to a Google Cloud Storage (GCS) bucket.
    -   Triggers an import job in **Vertex AI Search**, which automatically parses, chunks, and indexes the content of the documents.

2.  **Chat (`--mode chat`):**
    -   Starts an interactive command-line interface.
    -   The agent, powered by the ADK and a Gemini model, takes user questions.
    -   It uses a `search_knowledge_base` tool to query the indexed documents in Vertex AI Search.
    -   The search results are fed back to the agent as context, which it uses to generate an informed answer.

---

## Getting Started

### 1. Prerequisites
-   Python 3.10+
-   [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
-   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated (`gcloud auth application-default login`).

### 2. Installation & Configuration
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ben-Cliff/gcp-agentic-unstructured-data-retrieval.git
    cd gcp-agentic-unstructured-data-retrieval
    ```
2.  **Install dependencies:**
    ```bash
    poetry install
    ```
3.  **Configure environment variables:**
    -   Copy the example file: `cp .env.example .env`
    -   Edit the `.env` file and add your Google Cloud project details (`PROJECT_ID`, `LOCATION`, `DATA_STORE_ID`, etc.).

### 3. Provision Cloud Infrastructure
Before running the application, you must create the necessary Google Cloud resources. Follow the instructions in the **[INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md)** guide.

---

## Usage

### 1. Ingest Your Data
1.  Place your PDF files into the `data/raw` directory.
2.  Run the ingestion pipeline:
    ```bash
    poetry run python main.py --mode ingest
    ```

### 2. Chat with Your Data
Once the ingestion is complete, start the interactive chat session:
```bash
poetry run python main.py --mode chat
```

---

## Makefile Commands

This project includes a `Makefile` to streamline common tasks:

-   `make install`: Installs all project dependencies.
-   `make check`: Runs linting, static type checking, and other code quality checks.
-   `make create-datastore`: Runs the script to create the Vertex AI Search Data Store.
-   `make create-engine`: Runs the script to create the Enterprise Search App.