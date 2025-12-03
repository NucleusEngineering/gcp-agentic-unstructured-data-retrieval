import os
import json
import uuid
from glob import glob
from src.ingestion.parser import parse_pdf
from src.ingestion.chunker import chunk_text
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def run_ingestion(input_dir: str, output_dir: str):
    """
    Orchestrates the PDF parsing, chunking, and JSON conversion process.

    Args:
        input_dir (str): The directory containing raw PDF files.
        output_dir (str): The directory where processed JSON files will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in input directory: {input_dir}")
        return

    processed_data = []
    for file_path in pdf_files:
        try:
            logger.info(f"Processing file: {file_path}")
            text = parse_pdf(file_path)
            chunks = chunk_text(text)

            file_name = os.path.basename(file_path)
            for i, chunk in enumerate(chunks):
                processed_data.append({
                    "id": str(uuid.uuid4()),
                    "content": chunk,
                    "source_file": file_name,
                    "page_number": i + 1  # Assuming chunks are sequential and can be mapped to pages roughly
                })
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

    output_file_path = os.path.join(output_dir, "processed_data.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        for entry in processed_data:
            f.write(json.dumps(entry) + "\n")
    logger.info(f"Ingestion complete. Processed data saved to {output_file_path}")
