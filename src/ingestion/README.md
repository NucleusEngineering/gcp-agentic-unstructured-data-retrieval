# Ingestion

This directory is responsible for processing and preparing data for the search engine. It includes modules for parsing different file formats, chunking large documents, and running the ingestion pipeline.

## Files

-   `pipeline.py`: This file manages the ingestion process. The `run_ingestion` function handles the flow of taking raw local files, uploading them to a storage bucket, and triggering the import process in the search service.
-   `parser.py`: This module contains logic for reading and extracting text content from different file formats. It currently handles PDF files and is designed to be extended for other types.
-   `chunker.py`: This module is responsible for breaking down large blocks of text into smaller chunks, which helps the search engine effectively index and retrieve relevant passages.