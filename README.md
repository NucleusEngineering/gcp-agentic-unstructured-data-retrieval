# Extensible RAG Agent with Vertex AI Search

This repository provides a starting point for a Retrieval-Augmented Generation (RAG) system built on Google Cloud. It uses the Google Agent Development Kit (ADK) to create a conversational agent that can reason over unstructured data, like PDFs, indexed in Vertex AI Search.

The codebase is intended as a functional example that can be extended. It currently handles PDF ingestion and provides a basic chat interface, with `TODO` markers and challenges included to guide developers in enhancing its capabilities.

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

## Prerequisites

Before you begin, ensure you have the following tools installed on your system:
-   **Python 3.10+**
-   **[Poetry](https://python-poetry.org/docs/#installation)** for dependency management.
-   **[Google Cloud SDK](https://cloud.google.com/sdk/docs/install)** to manage your Google Cloud resources from the command line.

## Getting Started

This section provides a streamlined guide to get the project running. For a more detailed breakdown of the infrastructure and architecture, please refer to the specific documentation mentioned above.

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ben-Cliff/gcp-agentic-unstructured-data-retrieval.git
cd gcp-agentic-unstructured-data-retrieval
```

### Step 2: Install Dependencies
This project uses Poetry for dependency management.
```bash
poetry install
```

### Step 3: Configure Your Environment
Copy the example environment file and fill in the details for your Google Cloud project.
```bash
cp .env.example .env
```
Now, edit the `.env` file with your specific project information. Refer to the comments in the file for guidance.

### Step 4: Provision Cloud Infrastructure
This is the most important step. The included `Makefile` automates the entire setup of your Google Cloud resources.
```bash
make infra
```

> **A Note on Authentication:**
> The first time you run `make infra`, it will likely detect that you are not logged into Google Cloud and prompt you to authenticate. This process (`gcloud auth application-default login`) will open a web browser for you to sign in.
>
> **Occasionally, the script may fail immediately after you log in.** This is normal. Simply **run `make infra` a second time,** and the script will pick up your new credentials and continue where it left off.

---

## Usage

### 1. Ingest Your Data
1.  **Generate sample data:**
    Run the make command to generate synthetic medical records for testing.
    ```bash
    make generate-data
    ```
    > Alternatively, you can place your own PDF files into the `data/raw` directory.

2.  **Run the ingestion pipeline:**
    This command uploads the files to GCS and indexes them in Vertex AI Search.
    ```bash
    poetry run python main.py --mode ingest
    ```
    > **Note:** The indexing process in Vertex AI Search runs in the background and may take a few minutes to complete. Your data will be available for chat once this process is finished.

### 2. Chat with Your Data
Once the ingestion is complete, start the interactive chat session:
```bash
poetry run python main.py --mode chat
```

---

## Makefile Commands

This project includes a `Makefile` to streamline common tasks:

-   `make install`: Installs all project dependencies using Poetry.
-   `make check`: Runs linting and static type checking to ensure code quality.
-   `make create-datastore`: Executes the script to provision the Vertex AI Search Data Store.
-   `make create-engine`: Executes the script to create the Enterprise Search App, which wraps the Data Store.
-   `make infra`: A convenience command that runs both `create-datastore` and `create-engine` in sequence.