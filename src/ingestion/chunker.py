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
import os
import re
from typing import List
import numpy as np
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from src.shared.logger import setup_logger

logger = setup_logger(__name__)


SIMILARITY_THRESHOLD = 0.75
MIN_SENTENCES_PER_CHUNK = 2
EMBEDDING_MODEL_NAME = "text-embedding-004"
EMBEDDING_BATCH_SIZE = 250
EMBEDDING_DIMENSIONALITY = 768

_embedding_model_cache = None


def _get_embedding_model() -> TextEmbeddingModel:
    global _embedding_model_cache

    if _embedding_model_cache is not None:
        return _embedding_model_cache

    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")
    if not project_id:
        raise RuntimeError("PROJECT_ID environment variable not set")

    try:
        aiplatform.init(project=project_id, location=location)
        _embedding_model_cache = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL_NAME)
        logger.info(f"Initialized Vertex AI embedding model: {EMBEDDING_MODEL_NAME} (cached for reuse)")
    except Exception as initialization_error:
        raise RuntimeError(f"Embedding model initialization failed: {initialization_error}")

    return _embedding_model_cache


def split_into_sentences(text: str) -> List[str]:
    if not text or not text.strip():
        logger.warning("Empty text provided to split_into_sentences")
        return []

    # Pattern explanation:
    # (?<=[.!?]) - lookbehind for sentence-ending punctuation
    # \s+ - one or more whitespace characters
    # (?=[A-Z0-9]) - lookahead for capital letter or number (start of new sentence)
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z0-9])'
    sentences = re.split(sentence_pattern, text)

    cleaned_sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    logger.debug(f"Split text into {len(cleaned_sentences)} sentences.")
    return cleaned_sentences


def generate_embeddings_for_sentences(sentences: List[str]) -> List[np.ndarray]:
    if not sentences:
        logger.warning("No sentences provided to generate_embeddings_for_sentences")
        return []

    embedding_model = _get_embedding_model()

    all_embeddings = []
    for batch_start_index in range(0, len(sentences), EMBEDDING_BATCH_SIZE):
        batch_end_index = min(batch_start_index + EMBEDDING_BATCH_SIZE, len(sentences))
        sentence_batch = sentences[batch_start_index:batch_end_index]

        try:
            logger.debug(f"Generating embeddings for batch {batch_start_index // EMBEDDING_BATCH_SIZE + 1} ({len(sentence_batch)} sentences)")

            embeddings_response = embedding_model.get_embeddings(
                sentence_batch,
                output_dimensionality=EMBEDDING_DIMENSIONALITY
            )

            batch_embeddings = [
                np.array(embedding.values, dtype=np.float32)
                for embedding in embeddings_response
            ]
            all_embeddings.extend(batch_embeddings)

        except Exception as api_error:
            raise RuntimeError(f"Embedding generation failed at index {batch_start_index}: {api_error}")

    logger.info(f"Successfully generated {len(all_embeddings)} embeddings.")
    return all_embeddings


def calculate_cosine_similarity(embedding_vector_a: np.ndarray, embedding_vector_b: np.ndarray) -> float:
    if embedding_vector_a.shape != embedding_vector_b.shape:
        raise ValueError(
            f"Embedding vectors must have the same shape. "
            f"Got {embedding_vector_a.shape} and {embedding_vector_b.shape}"
        )

    dot_product = np.dot(embedding_vector_a, embedding_vector_b)
    magnitude_a = np.linalg.norm(embedding_vector_a)
    magnitude_b = np.linalg.norm(embedding_vector_b)
    if magnitude_a == 0 or magnitude_b == 0:
        logger.warning("Zero vector detected in cosine similarity calculation.")
        return 0.0

    cosine_similarity_score = dot_product / (magnitude_a * magnitude_b)

    # NOTE: Clamping to [0, 1] range but tbh I'm not sure - maybe we should allow [-1, 1]
    cosine_similarity_score = max(0.0, min(1.0, float(cosine_similarity_score)))

    return cosine_similarity_score


def identify_semantic_split_points(
    embeddings: List[np.ndarray],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
    min_sentences_per_chunk: int = MIN_SENTENCES_PER_CHUNK
) -> List[int]:
    if len(embeddings) < 2:
        logger.debug("Fewer than 2 embeddings provided; no split points identified.")
        return []

    split_point_indices = []
    sentences_since_last_split = 0
    for index in range(len(embeddings) - 1):
        current_embedding = embeddings[index]
        next_embedding = embeddings[index + 1]

        similarity_score = calculate_cosine_similarity(current_embedding, next_embedding)
        sentences_since_last_split += 1
        if sentences_since_last_split >= min_sentences_per_chunk and similarity_score < similarity_threshold:
            split_point_indices.append(index + 1)
            sentences_since_last_split = 0
            logger.debug(f"Semantic split detected at sentence {index + 1} (similarity: {similarity_score:.3f})")

    logger.info(f"Identified {len(split_point_indices)} semantic split points.")
    return split_point_indices


def assemble_chunks_from_sentences(
    sentences: List[str],
    split_point_indices: List[int],
    max_chunk_size: int
) -> List[str]:
    if not sentences:
        logger.warning("No sentences provided for chunk assembly.")
        return []

    final_chunks = []

    # NOTE: I just asked Claude to help me assemble the chunks given the split points
    # It came up with the following code and function `_subdivide_large_segment`
    # We can review it later if we don't like it
    boundary_indices = [0] + split_point_indices + [len(sentences)]
    for segment_index in range(len(boundary_indices) - 1):
        segment_start = boundary_indices[segment_index]
        segment_end = boundary_indices[segment_index + 1]

        segment_sentences = sentences[segment_start:segment_end]
        segment_text = " ".join(segment_sentences)
        if len(segment_text) <= max_chunk_size:
            final_chunks.append(segment_text)
            logger.debug(f"Created chunk with {len(segment_sentences)} sentences ({len(segment_text)} chars).")
        else:
            # Segment is too large; subdivide it by size while keeping sentence boundaries
            logger.debug(f"Segment too large ({len(segment_text)} chars); subdividing...")
            subdivided_chunks = _subdivide_large_segment(segment_sentences, max_chunk_size)
            final_chunks.extend(subdivided_chunks)

    logger.info(f"Assembled {len(final_chunks)} final chunks from {len(sentences)} sentences.")
    return final_chunks


def _subdivide_large_segment(sentences: List[str], max_chunk_size: int) -> List[str]:
    """
    Subdivides a semantically-coherent segment that exceeds the max chunk size.

    This helper function ensures large semantic chunks are split into smaller pieces
    while still respecting sentence boundaries as much as possible.

    Args:
        sentences: List of sentences forming a single semantic segment.
        max_chunk_size: Maximum character count per chunk.

    Returns:
        List of text chunks, each respecting the size constraint.
    """
    subdivided_chunks = []
    current_chunk_sentences = []
    current_chunk_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        # Check if adding this sentence would exceed the limit
        # +1 accounts for the space between sentences
        space_needed = 1 if current_chunk_sentences else 0
        if current_chunk_length + space_needed + sentence_length > max_chunk_size and current_chunk_sentences:
            # Finalize current chunk
            chunk_text_tmp = " ".join(current_chunk_sentences)
            subdivided_chunks.append(chunk_text_tmp)
            logger.debug(f"Subdivided chunk created: {len(current_chunk_sentences)} sentences, {len(chunk_text_tmp)} chars.")

            # Start new chunk
            current_chunk_sentences = [sentence]
            current_chunk_length = sentence_length
        else:
            # Add space only if there are already sentences in the chunk
            space_needed = 1 if len(current_chunk_sentences) > 0 else 0
            current_chunk_sentences.append(sentence)
            current_chunk_length += sentence_length + space_needed

    # Add remaining sentences as final chunk
    if current_chunk_sentences:
        chunk_text_tmp = " ".join(current_chunk_sentences)
        subdivided_chunks.append(chunk_text_tmp)
        logger.debug(f"Final subdivided chunk: {len(current_chunk_sentences)} sentences, {len(chunk_text_tmp)} chars.")

    return subdivided_chunks


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
    if not text or not text.strip():
        logger.warning("Empty text provided to chunk_text")
        return []

    logger.info(f"Starting semantic chunking for text of length {len(text)} characters.")

    # NOTE: just skipping `overlap` for now
    try:
        sentences = split_into_sentences(text)
        if len(sentences) == 0:
            logger.warning("No sentences extracted from text; returning original text as single chunk.")
            return [text]
        if len(sentences) == 1:
            logger.info("Only one sentence found; returning as single chunk.")
            return [sentences[0]]

        logger.info(f"Generating embeddings for {len(sentences)} sentences...")
        sentence_embeddings = generate_embeddings_for_sentences(sentences)

        logger.info("Identifying semantic boundaries...")
        split_point_indices = identify_semantic_split_points(
            embeddings=sentence_embeddings,
            similarity_threshold=SIMILARITY_THRESHOLD,
            min_sentences_per_chunk=MIN_SENTENCES_PER_CHUNK
        )

        logger.info("Assembling final chunks...")
        final_chunks = assemble_chunks_from_sentences(
            sentences=sentences,
            split_point_indices=split_point_indices,
            max_chunk_size=chunk_size
        )

        logger.info(f"Successfully chunked text into {len(final_chunks)} semantic chunks.")
        return final_chunks

    except Exception as error:
        logger.error(f"Error during semantic chunking: {error}")
        logger.warning("Falling back to returning original text as single chunk.")
        # I prefer to don't fail completely
        return [text]
