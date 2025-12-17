#!/usr/bin/env python3
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

"""
Script to convert medical record PDFs to structured JSON format.
Extracts patient information, visit details, and medication data.
"""

import os
import json
import re
import pypdf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class MedicalRecordParser:
    """Deterministic parser for medical record PDFs."""

    def __init__(self):
        self.medication_patterns = [
            # Pattern: "Start [Medication] [Dosage] [Frequency]" (most specific first)
            r'(?:Start|Continue)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+(?:\.\d+)?(?:mg|g|ml|mcg|units?))\s+((?:once|twice|three times|[\d]+\s+times?)\s+(?:daily|weekly|per day|a day))',
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
                return text.strip()
        except Exception as e:
            raise ValueError(f"Error reading PDF {pdf_path}: {str(e)}")

    def parse_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text."""
        # Look for "Patient: [Name]" until newline or next field
        pattern = r'Patient:\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s*\n|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None

    def parse_date(self, text: str) -> Optional[str]:
        """Extract visit date from text."""
        # Look for "Date: YYYY-MM-DD" format
        pattern = r'Date:\s+(\d{4}-\d{2}-\d{2})'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

    def parse_provider(self, text: str) -> Optional[str]:
        """Extract provider name from text."""
        # Look for "Provider: Dr. [Name]" or "Provider: [Name]" until newline
        pattern = r'Provider:\s+((?:Dr\.\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s*\n|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None

    def parse_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract content from a specific section (SUBJECTIVE, OBJECTIVE, ASSESSMENT, PLAN)."""
        # Pattern to match section headers and extract content until next section or end
        pattern = rf'{section_name.upper()}:\s*\n?(.*?)(?=\n\s*(?:SUBJECTIVE|OBJECTIVE|ASSESSMENT|PLAN):|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # Clean up extra whitespace
            content = re.sub(r'\n\s*\n', '\n', content)
            content = re.sub(r'\s+', ' ', content)
            return content
        return None

    def parse_medications(self, plan_text: str) -> List[Dict[str, str]]:
        """Extract medication information from the PLAN section."""
        if not plan_text:
            return []

        medications = []

        # Try each medication pattern
        for pattern in self.medication_patterns:
            matches = re.findall(pattern, plan_text, re.IGNORECASE)
            for match in matches:
                if len(match) == 3:
                    medication_name, dosage, frequency = match

                    # Clean up medication name (remove extra spaces, capitalize properly)
                    medication_name = ' '.join(word.capitalize() for word in medication_name.split())

                    # Standardize frequency format
                    frequency = self._standardize_frequency(frequency)

                    # Check if this medication is already in our list (avoid duplicates)
                    if not any(med['medication'] == medication_name for med in medications):
                        medications.append({
                            'medication': medication_name,
                            'dosage': dosage,
                            'frequency': frequency
                        })

        return medications

    def _standardize_frequency(self, frequency: str) -> str:
        """Standardize frequency descriptions."""
        frequency_lower = frequency.lower().strip()

        # Common frequency mappings
        frequency_map = {
            'once daily': 'Once daily',
            'once per day': 'Once daily',
            'once a day': 'Once daily',
            'twice daily': 'Twice daily',
            'twice per day': 'Twice daily',
            'twice a day': 'Twice daily',
            'three times daily': 'Three times daily',
            'three times per day': 'Three times daily',
            'three times a day': 'Three times daily',
        }

        # Check for exact matches
        if frequency_lower in frequency_map:
            return frequency_map[frequency_lower]

        # Handle patterns like "2 times daily", "3 times a day", etc.
        pattern = r'(\d+)\s+times?\s+(daily|per day|a day)'
        match = re.match(pattern, frequency_lower)
        if match:
            num = match.group(1)
            if num == '1':
                return 'Once daily'
            elif num == '2':
                return 'Twice daily'
            elif num == '3':
                return 'Three times daily'
            else:
                return f"{num} times daily"

        # Return original if no standardization found
        return frequency.strip()

    def parse_medical_record(self, pdf_path: str) -> Dict:
        """Parse a single medical record PDF and return structured data."""
        text = self.extract_text_from_pdf(pdf_path)

        # Extract basic information
        patient = self.parse_patient_name(text)
        date = self.parse_date(text)
        provider = self.parse_provider(text)

        # Extract sections
        subjective = self.parse_section(text, 'SUBJECTIVE')
        objective = self.parse_section(text, 'OBJECTIVE')
        assessment = self.parse_section(text, 'ASSESSMENT')
        plan = self.parse_section(text, 'PLAN')

        # Extract medications from PLAN section
        medications = self.parse_medications(plan) if plan else []

        # Create structured output
        record = {
            'filename': os.path.basename(pdf_path),
            'patient': patient,
            'date': date,
            'provider': provider,
            'subjective': subjective,
            'objective': objective,
            'assessment': assessment,
            'plan': plan,
            'medications': medications,
            'parsed_timestamp': None  # Will be set when saving
        }

        return record

    def process_pdf_folder(self, input_folder: str, output_folder: str) -> List[Dict]:
        """Process all PDF files in a folder and generate JSON files."""
        input_path = Path(input_folder)
        output_path = Path(output_folder)

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all PDF files
        pdf_files = list(input_path.glob('*.pdf'))

        if not pdf_files:
            print(f"No PDF files found in {input_folder}")
            return []

        parsed_records = []
        print(f"Found {len(pdf_files)} PDF files to process...")

        for pdf_file in pdf_files:
            try:
                print(f"Processing: {pdf_file.name}")

                # Parse the PDF
                record = self.parse_medical_record(str(pdf_file))

                # Add timestamp
                from datetime import datetime
                record['parsed_timestamp'] = datetime.now().isoformat()

                # Generate JSON filename
                json_filename = pdf_file.stem + '.json'
                json_path = output_path / json_filename

                # Save JSON file
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(record, f, indent=2, ensure_ascii=False)

                parsed_records.append(record)
                print(f"  → Created: {json_filename}")

                # Print summary for verification
                if record['medications']:
                    med_summary = [f"{med['medication']} {med['dosage']} {med['frequency']}"
                                 for med in record['medications']]
                    print(f"  � Medications: {', '.join(med_summary)}")

            except Exception as e:
                print(f"  L Error processing {pdf_file.name}: {str(e)}")
                continue

        print(f"\n Successfully processed {len(parsed_records)} out of {len(pdf_files)} PDFs")
        return parsed_records


def main():
    """Main function to run the PDF to JSON converter."""
    parser = argparse.ArgumentParser(description='Convert medical record PDFs to structured JSON')
    parser.add_argument('--input', '-i',
                       default='data/raw',
                       help='Input folder containing PDF files (default: data/raw)')
    parser.add_argument('--output', '-o',
                       default='data/processed/medical_records_json',
                       help='Output folder for JSON files (default: data/processed/medical_records_json)')
    parser.add_argument('--example',
                       action='store_true',
                       help='Process only the example file (Angela_Gordon_1.pdf)')

    args = parser.parse_args()

    # Initialize parser
    medical_parser = MedicalRecordParser()

    if args.example:
        # Process only the example file
        example_file = 'data/raw/medical_record_Angela_Gordon_1.pdf'
        if os.path.exists(example_file):
            print("Processing example file only...")
            record = medical_parser.parse_medical_record(example_file)

            # Add timestamp
            from datetime import datetime
            record['parsed_timestamp'] = datetime.now().isoformat()

            # Print the parsed record
            print("\n" + "="*60)
            print("PARSED MEDICAL RECORD")
            print("="*60)
            print(json.dumps(record, indent=2))
        else:
            print(f"Example file not found: {example_file}")
    else:
        # Process all files in the input folder
        records = medical_parser.process_pdf_folder(args.input, args.output)

        # Create a summary file
        from datetime import datetime
        summary_path = Path(args.output) / 'parsing_summary.json'
        summary = {
            'total_processed': len(records),
            'timestamp': datetime.now().isoformat(),
            'files': [record['filename'] for record in records]
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"Summary saved to: {summary_path}")


if __name__ == '__main__':
    main()