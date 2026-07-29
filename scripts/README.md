# Scripts Directory

This directory contains all the operational scripts for the project, from infrastructure setup to data generation and evaluation.

---

## Script Descriptions

### Infrastructure Setup

#### `create_datastore.sh`

-   **Purpose**: Creates a new **Data Store** in Google Cloud Vertex AI Search. A Data Store is the foundational container that holds your raw documents before they are indexed.
-   **How it's used**: This script is typically run once during the initial project setup. It reads configuration variables like your `PROJECT_ID`, `LOCATION`, and desired `DATA_STORE_ID` from the `.env` file and uses the `curl` command to make a REST API call to Google Cloud to create the resource.
-   **Usage**:
    ```bash
    bash scripts/create_datastore.sh
    ```

#### `create_enterprise_engine.py`

-   **Purpose**: Creates a new **Enterprise Engine** and links it to the Data Store created by the previous script. The Engine is the "brain" that provides the advanced search and RAG capabilities (like summarization and question answering) on top of your data. This script specifically enables the `SEARCH_ADD_ON_LLM` feature, which is required for generative AI functionalities.
-   **How it's used**: This is also run once during initial setup, after the Data Store has been created. It uses the Python client library for Vertex AI Search.
-   **Usage**:
    ```bash
    poetry run python scripts/create_enterprise_engine.py
    ```

### Data Generation & Evaluation

#### `generate_data.py`

-   **Purpose**: Generates synthetic medical records in PDF format and saves them to the `data/raw/` directory. This allows you to create a large volume of realistic-looking test data.
-   **How it's used**: This script uses the `Faker` library to create random patient names and the `reportlab` library to generate PDF files. It's useful for stress-testing the data ingestion and search pipeline.
-   **Usage**:
    ```bash
    poetry run python scripts/generate_data.py
    ```

#### `generate_golden_dataset.py`

-   **Purpose**: Creates the "golden" or "ground truth" dataset used for evaluating the agent's performance. It reads the raw PDFs, uses Gemini to create high-quality question-and-answer pairs from each document, and saves them to `data/processed/golden_dataset.jsonl`.
-   **How it's used**: Run this script after you have your raw data in place. The output is the benchmark against which the agent's answers are measured.
-   **Usage**:
    ```bash
    poetry run python scripts/generate_golden_dataset.py
    ```

#### `run_evaluation.py`

-   **Purpose**: This is the primary script for evaluating the RAG agent's performance. It runs the agent against each question in the `golden_dataset.jsonl`, then uses the Vertex AI Evaluation Service to score the agent's responses on metrics like "groundedness" and "instruction_following".
-   **How it's used**: Run this script whenever you want to measure the impact of changes to your agent (e.g., prompt changes, model changes). The detailed results are saved to `data/processed/eval_results.json`.
-   **Usage**:
    ```bash
    poetry run python scripts/run_evaluation.py
    ```