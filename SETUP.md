# Project Setup Guide

This document provides a comprehensive guide to set up and run the project.

## 1. Prerequisites

Before you begin, ensure you have the following tools installed:
-   **Python 3.10+**
-   **[Poetry](https://python-poetry.org/docs/#installation)** for dependency management.
-   **[Google Cloud SDK](https://cloud.google.com/sdk/docs/install)** to manage your Google Cloud resources.

## 2. Initial Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Ben-Cliff/gcp-agentic-unstructured-data-retrieval.git
    cd gcp-agentic-unstructured-data-retrieval
    ```
2.  **Install Dependencies**:
    ```bash
    poetry install
    ```
3.  **Activate the Poetry shell**:
    ```bash
    poetry shell
    ```

## 3. Google Cloud Infrastructure Setup

This project requires specific Google Cloud resources.

1.  **Configure Environment Variables**:
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit the newly created `.env` file and fill in your `PROJECT_ID`, `LOCATION`, `DATA_STORE_ID`, `ENGINE_ID`, `VERTEX_AI_REGION`, and `GEMINI_API_KEY`.

2.  **Authenticate Google Cloud CLI**:
    *   Log in to your Google Cloud account:
        ```bash
        gcloud auth application-default login
        ```
    *   Set the active Google Cloud project:
        ```bash
        gcloud config set project <your-gcp-project-id>
        ```

3.  **Provision Infrastructure**:
    *   This command automates the entire setup of your Google Cloud resources.
    *   Run from the project root:
        ```bash
        make infra
        ```
    *   **Note on Authentication**: The first time you run this, it may fail immediately after you log in. This is normal. Simply run `make infra` a second time, and the script will use your new credentials to continue.

## 4. Data Processing & Usage

The application has two main modes: `ingest` and `chat`.

1.  **Ingest Data**:
    *   This mode scans `data/raw` for PDFs, uploads them to GCS, and triggers an import job in Vertex AI Search.
    *   **Note**: The `data/raw` directory already contains sample data. If you wish to generate more, see the Appendix.
    *   Run the ingestion pipeline. This process will take some time.
        ```bash
        poetry run python main.py --mode ingest
        ```
    *   You can monitor its progress in the Google Cloud Console:
        *   **Vertex AI Search**: [http://pantheon.corp.google.com/gen-app-builder/data-stores?authuser=2&project=<your-gcp-project-id>](http://pantheon.corp.google.com/gen-app-builder/data-stores?authuser=2&project=<your-gcp-project-id>)
        *   **Google Cloud Storage**: [https://console.cloud.google.com/storage/browser/<your-gcs-bucket-name>?project=<your-gcp-project-id>](https://console.cloud.google.com/storage/browser/<your-gcs-bucket-name>?project=<your-gcp-project-id>)

2.  **Chat with Your Data**:
    *   This mode starts an interactive CLI where the agent uses the indexed documents to answer questions.
    *   Run from the project root:
        ```bash
        poetry run python main.py --mode chat
        ```
    *   **Note**: You will notice the agent is not very helpful at first. This is your first clue.
    *   **Example Questions**:
        *   "how many patients have Dr. Rodriguez seen?"
        *   "How is Albert Johnson doing?"
        *   "Tell me about Albert Johnson"

## 5. Evaluating the Agent

Since the agent's initial performance is suboptimal, the next step is to evaluate it.

*   **Run the evaluation script:**
    ```bash
    poetry run python scripts/run_evaluation.py
    ```
*   **Note**: This script needs to be created as part of the hackathon challenge. It will use a "golden dataset" to measure the agent's responses. For instructions on how to create your own, see the Appendix.

## 6. The Hackathon Begins!

The setup is complete. Your mission is to improve the system by:

*   **Tackling the `TODO`s** in the codebase.
*   **Improving the agent** through evaluation.
*   **Processing new data types**.
*   **Building smarter, multi-agent systems**.

Refer to `CHALLENGE.md` for detailed instructions. Good luck!

---
## Appendix: Optional Steps

### Generating Synthetic Data
If you want to supplement or replace the existing sample data, you can generate new synthetic medical records.
```bash
make generate-data
```

### Generating a Golden Dataset
The evaluation script uses a pre-made golden dataset. If you want to create your own for customized testing:
1.  **Generate raw data** (if needed):
    ```bash
    poetry run python scripts/generate_data.py
    ```
2.  **Create the golden dataset**:
    ```bash
    poetry run python scripts/generate_golden_dataset.py
    ```

---
## Makefile Commands Reference
-   `make install`: Installs all project dependencies.
-   `make check`: Runs linting and static type checking.
-   `make generate-data`: Generates synthetic medical records for testing.
-   `make infra`: A convenience command that runs all infrastructure setup steps.
