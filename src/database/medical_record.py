from pydantic import BaseModel, Field
from typing import List, Optional
import json
from pathlib import Path


class Medication(BaseModel):
    """Represents a medication with dosage and frequency."""
    medication: str = Field(..., min_length=1, description="Medication name")
    dosage: str = Field(..., min_length=1, description="Medication dosage")
    frequency: str = Field(..., min_length=1, description="Frequency of medication")


class MedicalRecord(BaseModel):
    """Represents a complete medical record with all patient information."""
    filename: str = Field(..., description="Original PDF filename")
    patient: str = Field(..., min_length=1, description="Patient full name")
    date: str = Field(..., description="Encounter date")
    provider: str = Field(..., min_length=1, description="Healthcare provider name")
    subjective: str = Field(..., description="Subjective findings")
    objective: str = Field(..., description="Objective findings")
    assessment: str = Field(..., description="Clinical assessment")
    plan: str = Field(..., description="Treatment plan")
    medications: List[Medication] = Field(default_factory=list, description="List of prescribed medications")
    parsed_timestamp: str = Field(..., description="When this record was processed")

    @classmethod
    def from_json_file(cls, file_path: str) -> 'MedicalRecord':
        """Load and validate MedicalRecord from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.model_validate(data)

    @classmethod
    def load_all_from_directory(cls, directory_path: str) -> List['MedicalRecord']:
        """Load all medical records from a directory of JSON files."""
        records = []
        directory = Path(directory_path)

        for json_file in directory.glob("medical_record_*.json"):
            try:
                record = cls.from_json_file(str(json_file))
                records.append(record)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        return records

    def get_medication_count(self) -> int:
        """Get total number of medications for this patient."""
        return len(self.medications)

    def get_medication_names(self) -> List[str]:
        """Get list of all medication names for this patient."""
        return [med.medication for med in self.medications]

    def get_medication_details(self) -> List[dict]:
        """Get detailed medication information as dictionaries."""
        return [med.model_dump() for med in self.medications]

    def to_hashmap_entry(self) -> dict:
        """Convert to dictionary optimized for hashmap storage."""
        return {
            "patient_name": self.patient,
            "provider": self.provider,
            "date": self.date,
            "medications": self.get_medication_names(),
            "medication_count": self.get_medication_count(),
            "medication_details": self.get_medication_details(),
            "assessment": self.assessment,
            "subjective": self.subjective,
            "objective": self.objective,
            "plan": self.plan
        }
