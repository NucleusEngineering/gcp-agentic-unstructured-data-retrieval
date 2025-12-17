# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law of agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Splits text into context-aware segments.

    Args:
        text (str): The input text to chunk.
        chunk_size (int): The desired size of each chunk.
        overlap (int): The number of characters to overlap between chunks.

    Returns:
        List[str]: A list of text chunks.
    """

    # =================================================================================================
    # TODO: HACKATHON CHALLENGE (Pillar 1: Completeness)
    #
    # The current chunking logic is a basic, fixed-size sliding window. This is inefficient and
    # often splits sentences or paragraphs in awkward places, leading to poor context for the LLM.
    #
    # Your challenge is to replace this naive implementation with a more intelligent chunking strategy.
    #
    # REQUIREMENT: You must implement ONE of the following advanced chunking methods:
    #
    #   1. RECURSIVE CHUNKING:
    #      - Split the text recursively by a list of separators (e.g., "\n\n", "\n", " ", "").
    #      - This method tries to keep paragraphs, sentences, and words together as long as possible.
    #      - HINT: Look at how libraries like LangChain implement `RecursiveCharacterTextSplitter`.
    #
    #   2. SEMANTIC CHUNKING:
    #      - Use a sentence embedding model (like `text-embedding-004`) to measure the semantic
    #        similarity between consecutive sentences.
    #      - Split the text where the similarity score drops, indicating a change in topic.
    #      - This is the most advanced method and will likely yield the best RAG performance.
    #      - HINT: You'll need to calculate cosine similarity between sentence embeddings.
    #
    # =================================================================================================

    # =================================================================================================
    # CONFIGURATION: Customize chunk intro and section starters here
    # =================================================================================================

    # Define which fields to extract and prepend to each chunk
    # Format: {"field_name": "prefix_to_match"} - the prefix will be removed from the value
    intro_fields = {
        "patient_name": "Patient:",
        "date": "Date:"
    }

    # Define which sections should start a new chunk
    chunkSectionStarters = ["Provider", "SUBJECTIVE", "OBJECTIVE", "ASSESSMENT", "PLAN"]

    # Define substarters for specific sections (e.g., numbered PLAN items)
    planChunkSubstarters = [1, 2, 3]

    # =================================================================================================

    def extract_intro_values(lines: List[str]) -> dict:
        """Extract intro field values from the document."""
        intro_values = {}
        for line in lines:
            line_stripped = line.strip()
            for field_name, prefix in intro_fields.items():
                if line_stripped.startswith(prefix):
                    intro_values[field_name] = line_stripped.replace(prefix, "").strip()
            # Stop once all fields are found
            if len(intro_values) == len(intro_fields):
                break
        return intro_values

    def build_intro_prefix(intro_values: dict) -> str:
        """Build the intro prefix string from extracted values."""
        return " ".join(intro_values.values()) + " |"

    def save_chunk(content_list: List[str], intro_prefix: str, chunks: List[str]):
        """Save a chunk with the intro prefix prepended."""
        if content_list:
            content = ' '.join(content_list)
            chunks.append(f"{intro_prefix} {content}")

    # Section-aware chunking based on medical note structure
    chunks = []
    lines = text.split('\n')
    current_section = None
    current_content = []

    # Extract intro values and build prefix
    intro_values = extract_intro_values(lines)
    intro_prefix = build_intro_prefix(intro_values)

    for line in lines:
        # Replace newlines within the line content (normalize to single line)
        line_stripped = line.strip().replace('\n', ' ')

        # Check if line starts a new section
        section_found = False
        for starter in chunkSectionStarters:
            if line_stripped.startswith(f"{starter}:"):
                # Save previous section if exists
                if current_section and current_content:
                    save_chunk(current_content, intro_prefix, chunks)

                # Start new section
                current_section = starter
                current_content = [line_stripped]
                section_found = True
                break

        # Check for PLAN substarters (PLAN_1, PLAN_2, etc.)
        if not section_found and current_section == "PLAN":
            for substarter in planChunkSubstarters:
                if line_stripped.startswith(f"{substarter}."):
                    # Save previous plan subsection if exists
                    if current_content:
                        save_chunk(current_content, intro_prefix, chunks)

                    # Start new plan subsection with modified header
                    current_content = [line_stripped.replace(f"{substarter}.", f"PLAN_{substarter}:", 1)]
                    section_found = True
                    break

        # If no new section found, add line to current content
        if not section_found and line_stripped and current_section:
            current_content.append(line_stripped)

    # Add the last section
    if current_content and current_section:
        save_chunk(current_content, intro_prefix, chunks)

    logger.info(f"Chunked text into {len(chunks)} sections based on medical note structure.")
    return chunks
