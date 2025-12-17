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
import random
from faker import Faker
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

fake = Faker()

# Medical-sounding context to randomize
SYMPTOMS = ["chronic migraine", "lower back pain", "persistent cough", "irregular heartbeat", "fatigue", "blurred vision", "joint stiffness"]
DIAGNOSES = ["Type 2 Diabetes", "Hypertension", "Acute Bronchitis", "Generalized Anxiety Disorder", "Osteoarthritis", "Migraine w/ Aura"]
MEDICATIONS = ["Metformin 500mg", "Lisinopril 10mg", "Amoxicillin 500mg", "Sertraline 50mg", "Ibuprofen 400mg", "Sumatriptan 50mg"]

def generate_medical_text(patient_name):
    """Generates a block of unstructured medical text in SOAP format."""
    symptom = random.choice(SYMPTOMS)
    diagnosis = random.choice(DIAGNOSES)
    medication = random.choice(MEDICATIONS)
    
    # A "SOAP" note format (Subjective, Objective, Assessment, Plan)
    # This mixes structured headers with free-text paragraphs - perfect for testing RAG.
    text_block = f"""
    PATIENT ENCOUNTER NOTE
    -----------------------
    Patient: {patient_name}
    Date: {fake.date_this_year()}
    Provider: Dr. {fake.last_name()}
    
    SUBJECTIVE:
    Patient presents today complaining of {symptom} which started approximately 2 weeks ago. 
    They describe the pain/discomfort as a {random.randint(1,10)}/10. Patient reports difficulty 
    sleeping due to the symptoms. They deny any recent trauma or travel.
    
    OBJECTIVE:
    Vitals: BP {random.randint(110,140)}/{random.randint(70,90)}, HR {random.randint(60,100)}, Temp {random.uniform(97.0, 99.5):.1f}F.
    Physical exam reveals tenderness in the affected area if applicable. No acute distress noted.
    Lungs are clear to auscultation.
    
    ASSESSMENT:
    Findings are consistent with {diagnosis}. Differential diagnosis includes viral etiology 
    or stress-related exacerbation.
    
    PLAN:
    1. Start {medication} once daily.
    2. Follow up in 4 weeks if symptoms do not improve.
    3. Patient education provided regarding lifestyle changes and warning signs.
    """
    return text_block

def create_pdf(filename, text):
    """Writes the text to a simple PDF file."""
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER
    
    c.setFont("Helvetica", 12)
    y_position = height - 50
    
    # Simple line wrapping loop
    for line in text.split('\n'):
        c.drawString(50, y_position, line)
        y_position -= 15
        if y_position < 50: # New page if we run out of space
            c.showPage()
            y_position = height - 50
        
    c.save()
    

def main():
    # Ensure the output directory exists
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating mock data in {output_dir}...")
    
    # Generate 10 mock PDFs
    # Challenge: Increase this number to stress test the ingestion pipeline!
    for i in range(10):
        patient_name = fake.name()
        text_content = generate_medical_text(patient_name)
        
        # Sanitize filename
        safe_name = patient_name.replace(" ", "_")
        filename = os.path.join(output_dir, f"medical_record_{safe_name}_{i}.pdf")
        
        create_pdf(filename, text_content)
        print(f"  -> Generated: {filename}")
        
    print("\nDone! Run 'poetry run python main.py --mode ingest' to process these files.")

if __name__ == "__main__":
    main()
