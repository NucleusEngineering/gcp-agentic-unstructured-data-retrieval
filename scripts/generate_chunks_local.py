#!/usr/bin/env python3
"""
Generate chunked data locally without uploading to GCS.
This creates the processed_data.json file that can be used for testing.
"""

import os
import sys
import json
from glob import glob
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.parser import parse_pdf
from src.ingestion.chunker import chunk_text
from src.shared.sanitizer import sanitize_id

INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "processed_data.json")


def generate_chunks_locally():
    """Parse PDFs, chunk them, and save to local JSON file."""

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find all PDF files
    pdf_files = glob(os.path.join(INPUT_DIR, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {INPUT_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF files")
    print(f"Generating chunks locally...\n")

    processed_data = []

    for file_path in pdf_files:
        try:
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]

            # Parse the PDF
            print(f"Parsing {file_name}...")
            text_content = parse_pdf(file_path)

            # Chunk the text
            print(f"Chunking {file_name}...")
            chunks = chunk_text(text_content)
            print(f"  ✓ Created {len(chunks)} chunks\n")

            # Add each chunk as a separate entry
            for chunk_idx, chunk in enumerate(chunks):
                processed_data.append({
                    "id": sanitize_id(f"{base_name}_chunk_{chunk_idx}"),
                    "structData": {
                        "text_content": chunk,
                        "source_file": file_name,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks)
                    }
                })

        except Exception as e:
            print(f"  ✗ Error processing {file_name}: {e}\n")

    # Save to JSONL format (one JSON object per line)
    print(f"Saving {len(processed_data)} chunks to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in processed_data:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Successfully saved {len(processed_data)} chunks to {OUTPUT_FILE}")
    print(f"\nYou can now run: python scripts/generate_golden_dataset.py")


if __name__ == "__main__":
    generate_chunks_locally()
