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
import pypdf
from google.cloud import storage
from src.shared.logger import setup_logger
from src.search.vertex_client import VertexSearchClient
from src.shared.sanitizer import sanitize_id
from src.ingestion.parser import parse_pdf, parse_other_format # Import the new parser

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

    logger.info(f"--- Uploading {len(all_files)} files to GCS ---")
    for file_path in all_files:
        try:
            file_name = os.path.basename(file_path)
            gcs_raw_path = f"raw/{file_name}"
            
            blob = bucket.blob(gcs_raw_path)
            blob.upload_from_filename(file_path)
            gcs_uri = f"gs://{gcs_bucket_name}/{gcs_raw_path}"
            logger.info(f"Uploaded {file_name} to {gcs_uri}")

            base_name = os.path.splitext(file_name)[0]
            doc_id = sanitize_id(base_name)

            # Determine mimeType based on file extension
            file_extension = os.path.splitext(file_name)[1].lower()
            mime_type_map = {
                ".pdf": "application/pdf",
                ".txt": "text/plain",
                ".csv": "text/csv",
                ".eml": "message/rfc822"
            }
            mime_type = mime_type_map.get(file_extension, "application/octet-stream")

            metadata_list.append({
                "id": doc_id,
                "structData": {"source_file": file_name},
                "content": {
                    "mimeType": mime_type,
                    "uri": gcs_uri
                }
            })
        except Exception as e:
            logger.error(f"Failed to upload or process {file_path}: {e}")
    
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

            if file_extension == ".pdf":
                text_content = parse_pdf(file_path)
            elif file_extension in [".txt", ".csv", ".eml"]:
                text_content = parse_other_format(file_path)
            else:
                logger.warning(f"Unsupported file type {file_extension} for {file_name}, skipping.")
                continue

            if text_content:
                processed_data.append({
                    "id": sanitize_id(f"{file_name}"),
                    "structData": {
                        "text_content": text_content,
                        "source_file": file_name,
                    }
                })
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")

    output_file_path = os.path.join(output_dir, "processed_data.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        for entry in processed_data:
            f.write(json.dumps(entry) + "\n")
    
    logger.info(f"Local processed data saved to: {output_file_path}")
