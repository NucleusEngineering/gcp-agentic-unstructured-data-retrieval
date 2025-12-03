### MVP Development Checklist

**Phase 1: Environment & Configuration (Completed/User Action)**
*   [x] Project initialized with Poetry (`pyproject.toml`).
*   [x] `README.md` created and updated.
*   [x] `.gitignore` and `.env.example` are present.
*   [x] `Makefile` is present for convenience.
*   [ ] **(You)** Create your Vertex AI Search datastore in the Google Cloud Console.
*   [ ] **(You)** Create a `.env` file and add your `PROJECT_ID`, `LOCATION`, and `DATA_STORE_ID`.

**Phase 2: Scaffolding & Implementation (Agent Action)**
*   [x] **(I will do this next)** Create the directory structure (`data/raw`, `data/processed`, `src/ingestion`, `src/search`, `src/agent`).
*   [x] **(I will do this next)** Create the initial empty Python files (`logger.py`, `parser.py`, `chunker.py`, `pipeline.py`, `vertex_client.py`, `bot.py`, `main.py`).
*   [x] Implement Document Parsing (`src/ingestion/parser.py`).
*   [x] Implement Text Chunking (`src/ingestion/chunker.py`).
*   [x] Implement Conversion & Orchestration (`src/ingestion/pipeline.py`).
*   [x] Implement the Vertex AI Search Client.
*   [x] Implement the RAG Agent.
*   [x] Implement the CLI entrypoint (`main.py`).