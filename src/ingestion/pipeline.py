import os
import json
from glob import glob
import pypdf
from google.cloud import storage
from src.shared.logger import setup_logger
from src.search.vertex_client import VertexSearchClient
from src.shared.sanitizer import sanitize_id

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
    pdf_files = glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in input directory: {input_dir}")
        return

    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket_name)
    metadata_list = []

    logger.info(f"--- Uploading {len(pdf_files)} PDF files to GCS ---")
    for file_path in pdf_files:
        try:
            file_name = os.path.basename(file_path)
            gcs_raw_path = f"raw/{file_name}"
            
            blob = bucket.blob(gcs_raw_path)
            blob.upload_from_filename(file_path)
            gcs_uri = f"gs://{gcs_bucket_name}/{gcs_raw_path}"
            logger.info(f"Uploaded {file_name} to {gcs_uri}")

            base_name = os.path.splitext(file_name)[0]
            doc_id = sanitize_id(base_name)
            metadata_list.append({
                "id": doc_id,
                "structData": {"source_file": file_name},
                "content": {
                    "mimeType": "application/pdf",
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
    _generate_local_processed_data(pdf_files, output_dir)

def _generate_local_processed_data(pdf_files: list[str], output_dir: str):
    """
    Parses PDFs locally and saves the output to a JSON file for inspection.
    This is a simulation of the chunking that Vertex AI would perform.
    """
    logger.info("--- Generating local processed_data.json for chunking visibility ---")
    processed_data = []

    for file_path in pdf_files:
        try:
            file_name = os.path.basename(file_path)
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                processed_data.append({
                    "id": sanitize_id(f"{file_name}_page_{i+1}"),
                    "structData": {
                        "text_content": page.extract_text(),
                        "source_file": file_name,
                        "page_number": i + 1,
                    }
                })
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")

    output_file_path = os.path.join(output_dir, "processed_data.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        for entry in processed_data:
            f.write(json.dumps(entry) + "\n")
    
    logger.info(f"Local processed data saved to: {output_file_path}")

