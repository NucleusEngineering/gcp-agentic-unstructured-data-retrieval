This `implementation_plan.md` is designed to be read by an AI coding assistant (like Gemini Code Assist) or used as a step-by-step manual for a developer to scaffold the project.

[cite_start]It adheres to the structure defined in the **Hackathon Starter Kit** [cite: 11, 12] and your summary.

-----

# implementation\_plan.md

## Project Overview

**Project Name:** `nelly-hackathon-mvp`
**Description:** A Python-based skeleton for a RAG (Retrieval-Augmented Generation) system. It handles document ingestion (PDF parsing, chunking, JSON conversion), indexing into Vertex AI Search, and a Gemini-powered Agent for querying.

## Technology Stack

  * **Language:** Python 3.10+
  * **Cloud Provider:** Google Cloud Platform (Vertex AI, Vertex AI Search)
  * **Key Libraries:** `google-cloud-discoveryengine`, `vertexai`, `pypdf`, `python-dotenv`
  * **Style:** MVP, Modular, Type-hinted, Logged.

-----

## Phase 1: Environment & Configuration

### 1.1 Project Structure

Create the following directory structure:

```text
nelly-hackathon-mvp/
├── data/
│   ├── raw/                  # Place PDF files here
│   └── processed/            # Output JSON files land here
├── src/
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py         # Centralized logging configuration
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── parser.py         # Extracts text from PDFs
│   │   ├── chunker.py        # Splits text into context-aware segments
│   │   └── pipeline.py       # Orchestrates Parsing -> Chunking -> JSON
│   ├── search/
│   │   ├── __init__.py
│   │   └── vertex_client.py  # Handles search queries to Vertex AI
│   └── agent/
│       ├── __init__.py
│       └── bot.py            # Gemini Agent logic with Search Tool
├── .env.example              # Template for environment variables
├── .gitignore                # Standard Python gitignore
├── main.py                   # CLI Entry point (Ingest vs Chat)
├── README.md                 # Setup instructions
└── requirements.txt          # Dependencies
```

### 1.2 Configuration Files

**Create `.env.example`**:

```text
PROJECT_ID="your-gcp-project-id"
LOCATION="us-central1" (or "eu-west1")
DATA_STORE_ID="your-vertex-search-datastore-id"
```

**Create `requirements.txt`**:

```text
google-cloud-discoveryengine>=0.11.0
google-cloud-aiplatform>=1.38.0
pypdf>=3.17.0
python-dotenv>=1.0.0
```

**Create `src/utils/logger.py`**:

  * Implement a `setup_logger(name)` function.
  * Use standard Python `logging` library.
  * Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
  * Output to Console (StreamHandler).

-----

## Phase 2: The Ingestion Engine (Steps 1, 2, 3)

### 2.1 Document Parsing (`src/ingestion/parser.py`)

  * **Function:** `parse_pdf(file_path: str) -> str`
  * **Logic:**
      * Use `pypdf.PdfReader`.
      * Iterate through pages and extract text.
      * **Innovation Point:** Add a TODO comment for developers to implement OCR for scanned docs later.
  * **Return:** A single string containing the full document text (or a list of page objects if preferred, but keep it simple for MVP).

### 2.2 Text Chunking (`src/ingestion/chunker.py`)

  * **Function:** `chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]`
  * **Logic:**
      * Implement a simple sliding window approach.
      * **Innovation Point:** Add a docstring noting this is where "Semantic Chunking" logic should be injected.

### 2.3 Conversion & Orchestration (`src/ingestion/pipeline.py`)

  * **Function:** `run_ingestion(input_dir: str, output_dir: str)`
  * **Logic:**
    1.  Glob all `.pdf` files in `input_dir`.
    2.  Loop through files:
          * Call `parser.parse_pdf`.
          * Call `chunker.chunk_text`.
          * Format chunks into JSON structure required for the hackathon:
            ```json
            {
              "id": "uuid",
              "content": "chunk_text",
              "source_file": "filename",
              "page_number": "int"
            }
            ```
    3.  Save the result as `processed_data.json` (JSON Lines format) in `output_dir`.
    4.  Log progress via `src/utils/logger.py`.

-----

## Phase 3: Vertex AI Integration (Step 4)

### 3.1 Search Client (`src/search/vertex_client.py`)

  * **Class:** `VertexSearchClient`
  * **Init:** Load `PROJECT_ID`, `LOCATION`, `DATA_STORE_ID` from environment.
  * **Method:** `search(query: str) -> str`
  * **Logic:**
      * Initialize `discoveryengine.SearchServiceClient`.
      * Execute a search query against the data store.
      * Parse the response to return a consolidated string of "Context" to feed the LLM.
      * Handle exceptions (e.g., store not found).

-----

## Phase 4: The Agent (Step 5)

### 4.1 Gemini Agent (`src/agent/bot.py`)

  * **Class:** `RAGAgent`
  * **Init:** Initialize `vertexai` and the `GenerativeModel` (e.g., `gemini-1.5-flash`).
  * **Method:** `ask(question: str)`
  * **Logic:**
      * **Tool Definition:** Define a Python function `retrieve_documents(query)` that wraps `VertexSearchClient.search`.
      * **Bind Tool:** Bind this tool to the Gemini model.
      * **Chat Session:** Start a chat session (`model.start_chat()`).
      * **Prompting:** Send the user's question. The model should decide to call the tool.
      * **Execution:** Execute the tool call if requested, feed the context back to Gemini, and return the final natural language response.

-----

## Phase 5: Entry Point & CLI

### 5.1 Main Execution (`main.py`)

  * Use `argparse` to create two modes:
    1.  `ingest`: Runs `src/ingestion/pipeline.py`.
    2.  `chat`: Instantiates `RAGAgent` and starts a `while True` input loop for the user.
  * **Example Usage:**
      * `python main.py --mode ingest`
      * `python main.py --mode chat`

-----

## Implementation Notes for the Developer

1.  **Environment:** Ensure you have the Google Cloud SDK installed and authenticated (`gcloud auth application-default login`).
2.  **Vertex Setup:** You must manually create a "Vertex AI Search" App and Data Store in the Google Cloud Console first. This code assumes the Data Store exists.
3.  **Import Strategy:** Use absolute imports (e.g., `from src.utils.logger import setup_logger`).
4.  **Error Handling:** Every major function should be wrapped in `try/except` blocks with logging.