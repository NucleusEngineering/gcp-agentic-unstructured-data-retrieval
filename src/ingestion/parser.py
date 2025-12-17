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
import os
import email
from email import policy
from email.parser import BytesParser
import pypdf
import pandas as pd
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


def parse_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        logger.info(f"Successfully parsed TXT: {file_path}")
        return text
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            logger.warning(f"Parsed TXT with latin-1 encoding: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path}: {e}")
            raise
    except Exception as e:
        logger.error(f"Error parsing TXT {file_path}: {e}")
        return ""


def parse_csv(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path)

        text_lines = []
        text_lines.append(f"CSV File: {os.path.basename(file_path)}")
        text_lines.append(f"Columns: {', '.join(df.columns.tolist())}")
        text_lines.append(f"Total Records: {len(df)}\n")

        for idx, row in df.iterrows():
            text_lines.append(f"--- Record {idx + 1} ---")
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    value = "N/A"
                text_lines.append(f"{col}: {value}")
            text_lines.append("")

        text = "\n".join(text_lines)
        logger.info(f"Successfully parsed CSV: {file_path} ({len(df)} rows)")
        return text
    except Exception as e:
        logger.error(f"Error parsing CSV {file_path}: {e}")
        return ""


def parse_eml(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        email_from = msg.get('From', 'N/A')
        email_to = msg.get('To', 'N/A')
        email_subject = msg.get('Subject', 'N/A')
        email_date = msg.get('Date', 'N/A')

        body_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body_parts.append(part.get_content())
        else:
            body_parts.append(msg.get_content())

        email_body = '\n'.join(body_parts) if body_parts else "No body content"

        text_lines = [
            f"Email: {os.path.basename(file_path)}",
            f"From: {email_from}",
            f"To: {email_to}",
            f"Subject: {email_subject}",
            f"Date: {email_date}",
            "",
            "Body:",
            email_body
        ]

        text = "\n".join(text_lines)
        logger.info(f"Successfully parsed EML: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error parsing EML {file_path}: {e}")
        return ""


def parse_other_format(file_path: str) -> str:
    """
    Placeholder for parsing other document formats.

    Args:
        file_path (str): The absolute path to the file.

    Returns:
        str: The extracted text content.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".txt":
        return parse_txt(file_path)
    elif file_extension == ".csv":
        return parse_csv(file_path)
    elif file_extension == ".eml":
        return parse_eml(file_path)
    else:
        return ""
