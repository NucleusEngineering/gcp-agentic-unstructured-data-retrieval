import pypdf
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

def parse_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.

    Args:
        file_path (str): The absolute path to the PDF file.

    Returns:
        str: A single string containing the full document text.
    """
    try:
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.info(f"Successfully parsed PDF: {file_path}")
        # TODO: Implement OCR for scanned documents here if needed in the future.
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        raise
