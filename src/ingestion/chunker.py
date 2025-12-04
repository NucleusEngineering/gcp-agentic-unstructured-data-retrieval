from typing import List
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Splits text into context-aware segments using a simple sliding window approach.

    Args:
        text (str): The input text to chunk.
        chunk_size (int): The desired size of each chunk.
        overlap (int): The number of characters to overlap between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    if overlap >= chunk_size:
        logger.warning("Overlap is greater than or equal to chunk_size. Adjusting overlap to be chunk_size - 1.")
        overlap = chunk_size - 1

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        if start >= len(text) and end < len(text):
            # Add the last remaining part if it's smaller than chunk_size but not yet added
            remaining = text[end:]
            if remaining:
                chunks.append(remaining)

    logger.info(f"Chunked text into {len(chunks)} segments with chunk_size={chunk_size} and overlap={overlap}.")
    # TODO: This is where 'Semantic Chunking' logic should be injected for more advanced use cases.
    return chunks
