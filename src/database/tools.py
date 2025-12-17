from typing import List, Optional
from src.database.structured_data import get_medical_database
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

# Initialize database singleton once
db = get_medical_database()


def get_patient_medications(patient_name: str) -> List[str]:
    """
    Get all medications for a specific patient.

    Args:
        patient_name: Full name of the patient (case insensitive)

    Returns:
        List of medication names the patient is taking
    """
    logger.info(f"Getting medications for patient: {patient_name}")
    medications = db.get_patient_medications(patient_name)
    logger.info(f"Found {len(medications)} medications for {patient_name}")
    return medications


def count_patient_medications(patient_name: str) -> int:
    """
    Count the total number of medications a patient is taking.

    Args:
        patient_name: Full name of the patient (case insensitive)

    Returns:
        Number of medications the patient is taking
    """
    logger.info(f"Counting medications for patient: {patient_name}")
    count = db.count_patient_medications(patient_name)
    logger.info(f"Patient {patient_name} takes {count} medications")
    return count


def search_patients_by_medication(medication_name: str) -> List[str]:
    """
    Find all patients taking a specific medication.

    Args:
        medication_name: Name of the medication to search for (case insensitive)

    Returns:
        List of patient names taking the specified medication
    """
    logger.info(f"Searching patients taking medication: {medication_name}")
    patients = db.search_patients_by_medication(medication_name)
    logger.info(f"Found {len(patients)} patients taking {medication_name}")
    return patients


def get_patient_doctor(patient_name: str) -> str:
    """
    Get the healthcare provider/doctor for a specific patient.

    Args:
        patient_name: Full name of the patient (case insensitive)

    Returns:
        Name of the patient's healthcare provider or "Not found" if patient doesn't exist
    """
    logger.info(f"Getting doctor for patient: {patient_name}")
    doctor = db.search_doctor_by_patient_name(patient_name)
    result = doctor if doctor else "Not found"
    logger.info(f"Doctor for {patient_name}: {result}")
    return result


def get_all_patients() -> List[str]:
    """
    Get a list of all patients in the medical database.

    Returns:
        List of all patient names in the database
    """
    logger.info("Getting all patients from database")
    patients = db.get_all_patients()
    logger.info(f"Found {len(patients)} patients in database")
    return patients


def get_patient_count() -> int:
    """
    Get the total number of patients in the medical database.

    Returns:
        Total number of patients
    """
    logger.info("Getting patient count")
    count = db.get_patient_count()
    logger.info(f"Total patients in database: {count}")
    return count


def get_patient_diagnosis(patient_name: str) -> str:
    """
    Get the medical diagnosis/assessment for a specific patient.

    Args:
        patient_name: Full name of the patient (case insensitive)

    Returns:
        Patient's medical diagnosis/assessment or "Not found" if patient doesn't exist
    """
    logger.info(f"Getting diagnosis for patient: {patient_name}")
    record = db.get_patient_full_medical_record_by_name(patient_name)

    if record:
        diagnosis = record.assessment
        logger.info(f"Diagnosis for {patient_name}: {diagnosis[:50]}...")
        return diagnosis
    else:
        logger.warning(f"Patient {patient_name} not found")
        return "Not found"


def get_patient_treatment_plan(patient_name: str) -> str:
    """
    Get the treatment plan for a specific patient.

    Args:
        patient_name: Full name of the patient (case insensitive)

    Returns:
        Patient's treatment plan or "Not found" if patient doesn't exist
    """
    logger.info(f"Getting treatment plan for patient: {patient_name}")
    record = db.get_patient_full_medical_record_by_name(patient_name)

    if record:
        plan = record.plan
        logger.info(f"Treatment plan for {patient_name}: {plan[:50]}...")
        return plan
    else:
        logger.warning(f"Patient {patient_name} not found")
        return "Not found"


def get_patient_visit_date(patient_name: str) -> str:
    """
    Get the date of the last medical visit for a specific patient.

    Args:
        patient_name: Full name of the patient (case insensitive)

    Returns:
        Date of the patient's medical visit or "Not found" if patient doesn't exist
    """
    logger.info(f"Getting visit date for patient: {patient_name}")
    record = db.get_patient_full_medical_record_by_name(patient_name)

    if record:
        visit_date = record.date
        logger.info(f"Visit date for {patient_name}: {visit_date}")
        return visit_date
    else:
        logger.warning(f"Patient {patient_name} not found")
        return "Not found"
