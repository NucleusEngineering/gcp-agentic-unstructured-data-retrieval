import re

def sanitize_id(doc_id: str) -> str:
    """
    Sanitizes a string to be used as a document ID in Vertex AI Search.
    Keeps only alphanumeric characters, hyphens, and underscores.
    """
    return re.sub(r"[^a-zA-Z0-9-_]", "", doc_id)
