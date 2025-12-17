#!/usr/bin/env python3
"""
Simple test script for the chunker module.
Tests the section-aware chunking on a sample medical record PDF.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.parser import parse_pdf
from src.ingestion.chunker import chunk_text

print(f"Project root: {project_root}")

def main():
    # Use one of the PDFs from data/raw
    pdf_path = project_root / "data" / "raw" / "medical_record_Arthur_Miller_0.pdf"

    print("=" * 80)
    print(f"Testing Chunker with: {pdf_path.name}")
    print("=" * 80)

    # Parse the PDF
    print("\n1. Parsing PDF...")
    try:
        text = parse_pdf(str(pdf_path))
        print(f"   ✓ Successfully extracted text ({len(text)} characters)")
        print("\n2. Extracted Text:")
        print("-" * 80)
        print(text)
        print("-" * 80)
    except Exception as e:
        print(f"   ✗ Error parsing PDF: {e}")
        return

    # Chunk the text
    print("\n3. Chunking text by medical note sections...")
    try:
        chunks = chunk_text(text)
        print(f"   ✓ Created {len(chunks)} chunks")
    except Exception as e:
        print(f"   ✗ Error chunking text: {e}")
        return

    # Display the chunks
    print("\n4. Chunks:")
    print("=" * 80)
    for i, chunk in enumerate(chunks, 1):
        # print(f"\nChunk {i}:")
        # print("-" * 80)
        print(chunk)
        # print("-" * 80)
        # print(f"Length: {len(chunk)} characters")

    print("\n" + "=" * 80)
    print(f"Summary: Successfully created {len(chunks)} chunks from the medical record")
    print("=" * 80)

if __name__ == "__main__":
    main()
