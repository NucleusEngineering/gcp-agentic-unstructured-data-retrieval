# Extensible RAG Agent with Vertex AI Search

This repository provides a starting point for a Retrieval-Augmented Generation (RAG) system built on Google Cloud. It uses the Google Agent Development Kit (ADK) to create a conversational agent that can reason over unstructured data, like PDFs, indexed in Vertex AI Search.

The codebase is intended as a functional example that can be extended. It currently handles PDF ingestion and provides a basic chat interface, with `TODO` markers and challenges included to guide developers in enhancing its capabilities.

---

## How It Works

The application operates in two primary modes:

1.  **Ingestion (`--mode ingest`):** This mode processes unstructured documents from a local directory. By default, it looks for PDF files, extracts their text content, and splits the text into smaller segments called chunks. The default chunking strategy is a naive, fixed-size sliding window that breaks text every 1000 characters with a 100-character overlap. This simple method is provided as a starting point, and a key challenge is to replace it with a more context-aware approach (see `CHALLENGE.md`). These chunks are then uploaded to a Vertex AI Search data store.

2.  **Chat (`--mode chat`):** This mode launches an interactive command-line interface where you can ask questions. The agent takes your query, searches the indexed documents in Vertex AI Search for relevant chunks, and uses a large language model (LLM) to generate a response based on the retrieved information.

---

## Key Commands

Here is a summary of the most important commands for setting up and running the project.

### Makefile Commands
-   `make install`: Installs all project dependencies using Poetry.
-   `make infra`: A convenience command that runs all infrastructure setup steps in sequence (permissions, datastore, engine, GCS bucket).
-   `make check`: Checks poetry lock file consistency.

### Application Commands
-   `poetry run python main.py --mode ingest`: Runs the ingestion pipeline to process raw documents and load them into Vertex AI Search.
-   `poetry run python main.py --mode chat`: Starts the interactive chat session with the RAG agent.
-   `poetry run python scripts/run_evaluation.py`: Runs the evaluation script to measure the agent's performance against a golden dataset.

---

## Optional & Repurposable Commands

The following scripts are not required for the basic workflow but can be altered or repurposed for custom use cases.

-   `make generate-data`: Generates synthetic medical records for testing. You can modify `scripts/generate_data.py` to create different types of data.
-   `poetry run python scripts/generate_golden_dataset.py`: Creates a structured evaluation dataset from the raw data. You can adapt this script to build custom datasets for measuring performance on specific tasks.

---
## Project Documentation

For detailed information, please refer to the following documents:

-   **[SETUP.md](./SETUP.md):** A comprehensive guide to install, configure, and run the project.
-   **[CHALLENGE.md](./CHALLENGE.md):** A guide for developers looking to extend the project's functionality, with specific challenges for 
-   **[INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md):** A step-by-step guide to provision the necessary Google Cloud resources.
