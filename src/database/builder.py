from typing import List
from pathlib import Path
import json
from src.database.medical_record import MedicalRecord
from src.shared.logger import setup_logger

logger = setup_logger(__name__)


def load_medical_records_from_json_directory(directory_path: str) -> List[MedicalRecord]:
    """
    Load all medical records from JSON files in the specified directory.

    Args:
        directory_path: Path to directory containing medical record JSON files

    Returns:
        List of validated MedicalRecord objects
    """
    records = []
    directory = Path(directory_path)

    if not directory.exists():
        logger.error(f"Directory does not exist: {directory_path}")
        return records

    if not directory.is_dir():
        logger.error(f"Path is not a directory: {directory_path}")
        return records

    json_files = list(directory.glob("medical_record_*.json"))
    logger.info(f"Found {len(json_files)} medical record JSON files in {directory_path}")

    for json_file in json_files:
        try:
            logger.debug(f"Loading {json_file.name}")
            record = MedicalRecord.from_json_file(str(json_file))
            records.append(record)
            logger.debug(f"Successfully loaded record for {record.patient}")
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")

    logger.info(f"Successfully loaded {len(records)} medical records")
    return records


def load_medical_records_from_default_path() -> List[MedicalRecord]:
    """
    Load medical records from the default processed JSON directory.

    Returns:
        List of validated MedicalRecord objects
    """
    default_path = "data/processed/medical_records_json"
    return load_medical_records_from_json_directory(default_path)


records = load_medical_records_from_default_path()

for record in records:
    name = record.patient
    medication = record.medications[0].medication
    print(f"Patient name: {name}. Medication: {medication}\n")
