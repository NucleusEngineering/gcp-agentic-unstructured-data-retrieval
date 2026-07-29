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
        # TODO: HACKATHON CHALLENGE (Optional, but good for completeness)
        # If you want to handle scanned PDFs (images of text), you would integrate an OCR (Optical Character Recognition)
        # library here, such as Google Cloud Vision AI or Tesseract. This is not a core requirement for the hackathon,
        # but a valuable extension for real-world unstructured data.
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        raise

def parse_other_format(file_path: str) -> str:
    """
    Placeholder for parsing other document formats.

    Args:
        file_path (str): The absolute path to the file.

    Returns:
        str: The extracted text content.
    """
    # =================================================================================================
    # TODO: HACKATHON CHALLENGE (Pillar 2: Extensibility)
    #
    # This function is a placeholder. Your challenge is to implement logic to parse at least one
    # new file format (e.g., .txt, .csv, .docx, .html) beyond PDFs.
    #
    # REQUIREMENTS:
    #   1. Choose a new file format to support (e.g., plain text, CSV, Word document, HTML).
    #   2. Implement the necessary code to read the content of that file type and return it as a string.
    #   3. You may need to install new libraries (e.g., `python-docx` for .docx, `pandas` for .csv).
    #      Remember to add any new dependencies to `pyproject.toml` and install them with `poetry install`.
    #   4. Ensure robust error handling for unsupported formats or corrupted files.
    #
    # HINT: For simple text files, you can just read the file content directly.
    #       For CSV, you might read it into a pandas DataFrame and then convert it to a string representation.
    #       For HTML, you could use BeautifulSoup to extract visible text.
    #
    # =================================================================================================
    logger.warning(f"Parsing for {file_path} is not yet implemented. Returning empty string.")
    return "" # Placeholder, replace with actual parsing logic
