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
import json
import random
from datetime import datetime
import pandas as pd
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_REGION", "us-central1")
PROCESSED_DATA_FILE = "data/processed/processed_data.json"  # Use pre-chunked data
OUTPUT_FILE = "data/processed/golden_dataset.jsonl"  # Use JSONL for compatibility
NUM_PATIENTS = 5  # Number of random patients to select

def generate_qa_pairs():
    """Generates a golden dataset (Q&A pairs) from pre-chunked medical records."""

    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    # NOTE: gemini-1.5-flash-001 and gemini-1.0-pro are not available in europe-west1, using gemini-2.0-flash instead.
    model = GenerativeModel("gemini-2.0-flash")

    dataset = []

    # Read pre-chunked data from processed_data.json (JSONL format)
    print(f"Loading pre-chunked data from {PROCESSED_DATA_FILE}...")

    all_chunks = []
    chunk_metadata = []

    try:
        with open(PROCESSED_DATA_FILE, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                chunk_text = entry["structData"]["text_content"]

                all_chunks.append(chunk_text)
                chunk_metadata.append({
                    "id": entry["id"],
                    "source_file": entry["structData"]["source_file"],
                    "chunk_index": entry["structData"]["chunk_index"],
                    "total_chunks": entry["structData"]["total_chunks"]
                })
    except FileNotFoundError:
        print(f"Error: {PROCESSED_DATA_FILE} not found. Please run ingestion first:")
        print("  python main.py --mode ingest")
        return
    except Exception as e:
        print(f"Error reading processed data: {e}")
        return

    print(f"Loaded {len(all_chunks)} chunks from processed data")

    # Group chunks by patient (source_file)
    patients = {}
    for idx, metadata in enumerate(chunk_metadata):
        source_file = metadata["source_file"]
        if source_file not in patients:
            patients[source_file] = []
        patients[source_file].append(idx)

    print(f"Found {len(patients)} unique patients")

    # Randomly select patients
    selected_patients = random.sample(list(patients.keys()), min(NUM_PATIENTS, len(patients)))

    print(f"Randomly selected {len(selected_patients)} patients:")
    for patient in selected_patients:
        print(f"  - {patient}")
    print()

    # Get current date for prompts
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Patient schedules —————————————————————————————————————————

    for patient_file in selected_patients:
        # Get all chunks for this patient
        patient_chunk_indices = patients[patient_file]

        # Filter to only use PLAN chunks (which contain medication info)
        patient_plan_chunks = [
            all_chunks[idx] for idx in patient_chunk_indices
            if "PLAN" in all_chunks[idx]
        ]

        # If no PLAN chunks found, skip this patient
        if not patient_plan_chunks:
            print(f"⚠ Skipping {patient_file}: No PLAN chunks found")
            continue

        # Combine all PLAN chunks for this patient as context
        patient_context = "\n\n".join(patient_plan_chunks)

        try:
            # Generate Q&A for this patient
            prompt = f"""
            You are a medical staff member tasked with handling medication for the medical practice.

            Today's date is {current_date}.

            Based on the following complete medical record for a patient, generate 2 diverse question-answer pairs about creating medication schedules for this patient.

            Questions should be specific to this patient and answerable from the provided medical record.
            Answers should provide clear medication schedules in a structured format list, containing medication name, dosage, date, and possibly time of day (if relevant). Always create the schedule for each day, so that it is clear on which date they need to take which medication and how much. So instead of "10mg of Medication A twice daily", you should write "Date, Medication A, 10mg" and "Date, Medication B, 5mg", from the date of the appointment to the last intake expected. If there is no final date, e.g. a duration of four weeks, make it up to 3 months. If there is a follow-up expected, this sets the end date of the medication schedule, so not the 3 months but the date of the follow-up.

            Format the output strictly as a list of JSON objects:
            [
                {{"question": "...", "answer": "..."}},
                {{"question": "...", "answer": "..."}}
            ]

            Complete Medical Record:
            {patient_context}
            """

            response = model.generate_content(prompt)

            # Parse JSON response
            content = response.text.replace("```json", "").replace("```", "").strip()
            qa_pairs = json.loads(content, strict=False)

            for pair in qa_pairs:
                dataset.append({
                    "context": patient_context,
                    "question": pair["question"],
                    "reference_answer": pair["answer"],
                    "source_file": patient_file
                })

            print(f"✓ Generated {len(qa_pairs)} Q&A pairs for: {patient_file}")

        except Exception as e:
            print(f"✗ Failed to generate Q&A for {patient_file}: {e}")


    # Practice-wide supply ordering —————————————————————————————————————————

    print(f"\nGenerating practice-wide supply ordering Q&A pairs...")

    # Use ALL PLAN chunks from ALL patients for comprehensive practice view
    all_plan_chunks = [chunk for chunk in all_chunks if "PLAN" in chunk]

    # Take a representative sample of PLAN chunks from across the practice
    sample_size = min(20, len(all_plan_chunks))
    sample_plan_chunks = random.sample(all_plan_chunks, sample_size)

    # Generate practice-wide supply ordering questions
    combined_context = "\n\n---\n\n".join(sample_plan_chunks)

    ordering_prompt = f"""
    You are a medical practice administrator responsible for ordering medication supplies for the entire practice.

    Today's date is {current_date}. Since our date is in the past, please also test out dates that were within the past three months to simulate realistic ordering schedules.

    Based on the following PLAN sections from multiple patients across the practice, generate 3 diverse question-answer pairs about creating supply ordering schedules for the practice.

    Questions should focus on:
    - Monthly bulk medication orders based on aggregate patient needs
    - Inventory management and reordering schedules
    - Quantity calculations for commonly prescribed medications

    Each answer should provide a clear ordering list in a structured format (table or list), including medication names, quantities needed, so that the practice has enough medication in stock for the next month at least. We want to have all medication usually in stock 3 times the expected need to avoid any shortage. We always place orders on the last day of the month.

    Format the output strictly as a list of JSON objects:
    [
        {{"question": "...", "answer": "..."}},
        {{"question": "...", "answer": "..."}},
        {{"question": "...", "answer": "..."}}
    ]

    PLAN Sections from Multiple Patients:
    {combined_context[:10000]}
    """

    try:
        response = model.generate_content(ordering_prompt)
        content = response.text.replace("```json", "").replace("```", "").strip()

        # Use strict=False to be more lenient with control characters
        qa_pairs = json.loads(content, strict=False)

        for pair in qa_pairs:
            dataset.append({
                "context": combined_context,
                "question": pair["question"],
                "reference_answer": pair["answer"],
                "source_file": "practice_wide_supply_ordering"
            })

        print(f"✓ Generated {len(qa_pairs)} practice-wide supply ordering Q&A pairs")

    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse JSON for practice ordering: {e}")
        if 'response' in locals():
            print(f"Response content (first 1000 chars):\n{response.text[:1000]}")
    except Exception as e:
        print(f"✗ Failed to generate practice ordering Q&A pairs: {e}")


    # Save to JSONL format (one JSON object per line)
    print(f"\nSaving dataset to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Golden dataset saved to {OUTPUT_FILE} ({len(dataset)} pairs)")

if __name__ == "__main__":
    generate_qa_pairs()
