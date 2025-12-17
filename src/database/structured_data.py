import hashlib
from typing import Dict, List, Optional
from src.database.builder import load_medical_records_from_default_path
from src.database.medical_record import MedicalRecord, Medication
from src.shared.logger import setup_logger

logger = setup_logger(__name__)


class MedicalDatabase:
    """
    In-memory database for medical records with persistent hashmaps.
    Singleton-like behavior to avoid reloading data.
    """

    def __init__(self):
        """Initialize the database and load all data once."""
        logger.info("Initializing MedicalDatabase...")
        self._name_to_hash: Dict[str, str] = {}
        self._patients_to_medical_record_db: Dict[str, MedicalRecord] = {}
        self._patient_to_medication_db: Dict[str, Medication] = {}
        self._patient_to_doctor_diagnosis_db: Dict[str, str] = {}
        self._patient_to_plan_summary_db: Dict[str, str] = {}
        self._patient_to_date_of_visit_db: Dict[str, str] = {}
        # self._medication_to_summary: Dict[str, str] = {}
        self._medication_to_patients_db: Dict[str, List[str]] = {}

        self._loaded = False
        self._load_data()

    def _load_data(self):
        """Load all medical records and build hashmaps."""
        if self._loaded:
            logger.debug("Data already loaded, skipping reload")
            return

        logger.info("Loading medical records from JSON files...")
        records = load_medical_records_from_default_path()

        for record in records:
            patient_hash = self._generate_patient_hash(record.patient)

            # Store in all hashmaps
            self._name_to_hash[record.patient.lower().strip()] = patient_hash
            self._patients_to_medical_record_db[patient_hash] = record
            self._patient_to_doctor_diagnosis_db[patient_hash] = record.assessment
            self._patient_to_plan_summary_db[patient_hash] = record.plan
            self._patient_to_date_of_visit_db[patient_hash] = record.date

            # Handle medications safely
            if record.medications:
                self._patient_to_medication_db[patient_hash] = record.medications[0]

                # Build medication to patients mapping
                for medication in record.medications:
                    medication_hash = self._generate_medication_hash(medication.medication)
                    if medication_hash not in self._medication_to_patients_db:
                        self._medication_to_patients_db[medication_hash] = []
                    else:
                        self._medication_to_patients_db[medication_hash].append(record.patient)
            else:
                self._patient_to_medication_db[patient_hash] = None

            logger.debug(f"Added patient {record.patient} with hash {
                         patient_hash[:8]}...")

        self._loaded = True
        logger.info(f"MedicalDatabase loaded with {
                    len(self._patients_to_medical_record_db)} patients")

    @staticmethod
    def _generate_patient_hash(patient_name: str) -> str:
        """Generate a unique hash ID for a patient based on their name."""
        normalized_name = patient_name.lower().strip()
        return hashlib.sha256(normalized_name.encode('utf-8')).hexdigest()

    @staticmethod
    def _generate_medication_hash(medication_name: str) -> str:
        """Generate a unique hash ID for a medication based on its name."""
        normalized_name = medication_name.lower().strip()
        return hashlib.sha256(normalized_name.encode('utf-8')).hexdigest()

    def get_patient_full_medical_record_by_name(self, patient_name: str) -> Optional[MedicalRecord]:
        """Find a patient record by their name using hash lookup."""
        normalized_name = patient_name.lower().strip()
        patient_hash = self._name_to_hash.get(normalized_name)

        if patient_hash:
            return self._patients_to_medical_record_db.get(patient_hash)
        return None

    def get_patient_medications(self, patient_name: str) -> List[str]:
        """Get all medications for a specific patient."""
        normalized_name = patient_name.lower().strip()
        patient_hash = self._name_to_hash.get(normalized_name)

        if patient_hash:
            record = self._patients_to_medical_record_db.get(patient_hash)
            if record and record.medications:
                return [med.medication for med in record.medications]
        return []

    def count_patient_medications(self, patient_name: str) -> int:
        """Count total medications for a patient."""
        return len(self.get_patient_medications(patient_name))

    def get_all_patients(self) -> List[str]:
        """Get list of all patient names."""
        return list(self._name_to_hash.keys())

    def get_patient_count(self) -> int:
        """Get total number of patients in database."""
        return len(self._patients_to_medical_record_db)

    def search_patients_by_medication(self, medication_name: str) -> List[str]:
        """Find all patients taking a specific medication."""
        medication_hash = self._generate_medication_hash(medication_name)
        matching_patients_names = self._medication_to_patients_db.get(medication_hash, [])

        return matching_patients_names

    def search_doctor_by_patient_name(self, patient_name: str) -> Optional[str]:
        """Find the responsible doctor for a patient by patient name"""
        patient_hash = self._generate_patient_hash(patient_name)
        record = self._patients_to_medical_record_db.get(patient_hash)

        if record:
            return record.provider
        return None


# Global singleton instance
_db_instance: Optional[MedicalDatabase] = None


def get_medical_database() -> MedicalDatabase:
    """Get the singleton instance of MedicalDatabase."""
    global _db_instance
    if _db_instance is None:
        _db_instance = MedicalDatabase()
    return _db_instance
