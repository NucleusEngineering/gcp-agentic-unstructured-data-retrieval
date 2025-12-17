# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import json
from glob import glob
from google.cloud import storage
from src.shared.logger import setup_logger
from src.search.vertex_client import VertexSearchClient
from src.shared.sanitizer import sanitize_id
from src.ingestion.parser import parse_pdf, parse_other_format
from src.ingestion.chunker import chunk_text

logger = setup_logger(__name__)

def run_ingestion(input_dir: str, output_dir: str):
    """
    Orchestrates the GCS-based ingestion process for Vertex AI Search.
    1. Uploads raw PDFs to GCS.
    2. Creates a metadata JSONL file pointing to the GCS URIs of the PDFs.
    3. Uploads the metadata file to GCS.
    4. Triggers the import job in Vertex AI Search.
    """
    gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not gcs_bucket_name:
        logger.error("GCS_BUCKET_NAME environment variable not set.")
        return

    os.makedirs(output_dir, exist_ok=True)

    # =================================================================================================
    # TODO: HACKATHON CHALLENGE (Pillar 2: Extensibility)
    #
    # The current pipeline only processes PDF files. Your challenge is to extend it to support
    # the new file format you implemented in `src/ingestion/parser.py`.
    #
    # REQUIREMENTS:
    #   1. Modify the `glob` pattern below to include your new file type (e.g., "*.pdf", "*.txt").
    #   2. Implement logic within the loop to detect the file type and call the appropriate
    #      parser function (`parse_pdf` or `parse_other_format`).
    #   3. Ensure the `mimeType` in the `metadata_list` entry is correctly set for your new file type.
    #
    # HINT: You can use `file_name.lower().endswith(".your_extension")` to check the file type.
    # =================================================================================================
    supported_extensions = ["*.pdf", "*.txt", "*.csv", "*.eml"]
    all_files = []
    for pattern in supported_extensions:
        all_files.extend(glob(os.path.join(input_dir, pattern)))

    if not all_files:
        logger.warning(f"No files found in input directory: {input_dir}")
        return

    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket_name)
    metadata_list = []

    logger.info(f"--- Processing {len(all_files)} files with semantic chunking ---")
    total_chunks = 0

    for file_path in all_files:
        try:
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            base_name = os.path.splitext(file_name)[0]

            logger.info(f"Parsing {file_name}...")
            if file_extension == ".pdf":
                text_content = parse_pdf(file_path)
            elif file_extension in [".txt", ".csv", ".eml"]:
                text_content = parse_other_format(file_path)
            else:
                logger.warning(f"Unsupported file type {file_extension}, skipping {file_name}")
                continue

            if not text_content or not text_content.strip():
                logger.warning(f"No text extracted from {file_name}, skipping")
                continue

            logger.info(f"Applying semantic chunking to {file_name}...")
            chunks = chunk_text(text_content, chunk_size=1000, overlap=0)
            logger.info(f"Created {len(chunks)} semantic chunks from {file_name}")

            for chunk_index, chunk_content in enumerate(chunks):
                chunk_filename = f"{base_name}_chunk_{chunk_index}.txt"
                gcs_chunk_path = f"chunks/{chunk_filename}"

                blob = bucket.blob(gcs_chunk_path)
                blob.upload_from_string(chunk_content, content_type="text/plain")
                gcs_uri = f"gs://{gcs_bucket_name}/{gcs_chunk_path}"

                chunk_doc_id = sanitize_id(f"{base_name}_chunk_{chunk_index}")
                metadata_list.append({
                    "id": chunk_doc_id,
                    "structData": {
                        "source_file": file_name,
                        "chunk_index": chunk_index,
                        "total_chunks": len(chunks)
                    },
                    "content": {
                        "mimeType": "text/plain",
                        "uri": gcs_uri
                    }
                })

            total_chunks += len(chunks)
            logger.info(f"Uploaded {len(chunks)} chunks from {file_name} to GCS")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            continue

    logger.info(f"--- Total: {total_chunks} chunks from {len(all_files)} files ---")
    
    metadata_file_path = os.path.join(output_dir, "metadata.jsonl")
    with open(metadata_file_path, "w", encoding="utf-8") as f:
        for entry in metadata_list:
            f.write(json.dumps(entry) + "\n")
    logger.info(f"Metadata file created at: {metadata_file_path}")

    gcs_metadata_path = "metadata/metadata.jsonl"
    metadata_blob = bucket.blob(gcs_metadata_path)
    metadata_blob.upload_from_filename(metadata_file_path)
    metadata_gcs_uri = f"gs://{gcs_bucket_name}/{gcs_metadata_path}"
    logger.info(f"Uploaded metadata file to {metadata_gcs_uri}")

    try:
        vertex_client = VertexSearchClient()
        vertex_client.import_from_gcs(metadata_gcs_uri)
    except Exception as e:
        logger.error(f"Failed to trigger Vertex AI import: {e}")

    # Also generate a local processed_data.json for chunking visibility
    _generate_local_processed_data(all_files, output_dir)

def _generate_local_processed_data(files: list[str], output_dir: str):
    """
    Parses files locally and saves the output to a JSON file for inspection.
    This is a simulation of the chunking that Vertex AI would perform.
    """
    logger.info("--- Generating local processed_data.json for chunking visibility ---")
    processed_data = []

    for file_path in files:
        try:
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            base_name = os.path.splitext(file_name)[0]

            if file_extension == ".pdf":
                text_content = parse_pdf(file_path)
            elif file_extension in [".txt", ".csv", ".eml"]:
                text_content = parse_other_format(file_path)
            else:
                logger.warning(f"Unsupported file type {file_extension} for {file_name}, skipping.")
                continue

            if not text_content or not text_content.strip():
                continue

            chunks = chunk_text(text_content, chunk_size=1000, overlap=0)
            for chunk_index, chunk_content in enumerate(chunks):
                processed_data.append({
                    "id": sanitize_id(f"{base_name}_chunk_{chunk_index}"),
                    "structData": {
                        "source_file": file_name,
                        "chunk_index": chunk_index,
                        "total_chunks": len(chunks),
                        "chunk_content": chunk_content,
                        "chunk_length": len(chunk_content)
                    }
                })

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")

    output_file_path = os.path.join(output_dir, "processed_data.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        for entry in processed_data:
            f.write(json.dumps(entry) + "\n")

    logger.info(f"Local processed data with {len(processed_data)} chunks saved to: {output_file_path}")
