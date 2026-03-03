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

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-cloud-aiplatform",
#     "python-dotenv",
#     "pypdf",
# ]
# ///

import os
import glob
import json
from vertexai.generative_models import GenerativeModel
import vertexai
from dotenv import load_dotenv
from src.ingestion.parser import parse_pdf  # Re-using existing parser logic

load_dotenv()

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_REGION", "us-central1")
INPUT_DIR = "data/raw"
OUTPUT_FILE = "data/processed/golden_dataset.jsonl"

def generate_qa_pairs():
    """Generates a golden dataset (Q&A pairs) from raw PDFs."""
    
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    # NOTE: gemini-1.5-flash-001 and gemini-1.0-pro are not available in europe-west1, using gemini-2.0-flash instead.
    model = GenerativeModel("gemini-2.0-flash")
    
    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    dataset = []

    print(f"Found {len(pdf_files)} PDF files. Generating Q&A pairs...")

    for file_path in pdf_files:
        try:
            # 1. Extract text using existing project logic
            text_content = parse_pdf(file_path)
            
            # 2. Prompt Gemini to generate Ground Truth
            prompt = f"""
            You are an expert medical annotator. 
            Analyze the following medical record and generate 3 diverse question-answer pairs.
            The questions should be specific to this patient.
            
            Format the output strictly as a list of JSON objects:
            [
                {{"question": "...", "answer": "..."}},
                ...
            ]

            Medical Record Content:
            {text_content[:8000]} # Truncate to fit context if needed
            """
            
            response = model.generate_content(prompt)
            
            # 3. Parse JSON response (Basic cleanup)
            content = response.text.replace("```json", "").replace("```", "").strip()
            qa_pairs = json.loads(content)
            
            for pair in qa_pairs:
                dataset.append({
                    "context": text_content, # The source text (Reference)
                    "question": pair["question"],
                    "reference_answer": pair["answer"],
                    "source_file": os.path.basename(file_path)
                })
                
            print(f"Processed: {os.path.basename(file_path)}")

        except Exception as e:
            print(f"Skipping {file_path}: {e}")

    # 4. Save to JSONL
    with open(OUTPUT_FILE, "w") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Golden dataset saved to {OUTPUT_FILE} ({len(dataset)} pairs)")

if __name__ == "__main__":
    generate_qa_pairs()
