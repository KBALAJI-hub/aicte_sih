import re
from typing import Dict, Optional
from sqlmodel import Session, select
from app.models import ApaarRegistry


def is_valid_apaar_format(apaar_id: str) -> bool:
    """
    Checks if APAAR ID is exactly 12 numeric digits.
    """
    if not apaar_id:
        return False
    return bool(re.fullmatch(r"^\d{12}$", str(apaar_id).strip()))


def verify_against_registry(
    session: Session,
    apaar_id: str,
    full_name: str,
    dob: str,
    gender: str
) -> Dict[str, any]:
    """
    Cross-checks student details against the mock Central APAAR Registry.
    Returns:
        status: 'MATCH' | 'MISMATCH' | 'NOT_FOUND' | 'INVALID_FORMAT'
        details: Explanation of discrepancies if any.
    """
    cleaned_id = str(apaar_id).strip()

    # 1. Format check
    if not is_valid_apaar_format(cleaned_id):
        return {
            "status": "INVALID_FORMAT",
            "message": "APAAR ID must be exactly 12 numeric digits.",
            "registry_record": None
        }

    # 2. Registry lookup
    registry_record = session.exec(
        select(ApaarRegistry).where(ApaarRegistry.apaar_id == cleaned_id)
    ).first()

    if not registry_record:
        return {
            "status": "NOT_FOUND",
            "message": "APAAR ID not found in Central Registry.",
            "registry_record": None
        }

    # 3. Demographic field comparison
    mismatches = []
    if registry_record.full_name.strip().lower() != full_name.strip().lower():
        mismatches.append(f"Name mismatch: provided '{full_name}', registry has '{registry_record.full_name}'")

    if str(registry_record.dob).strip() != str(dob).strip():
        mismatches.append(f"DOB mismatch: provided '{dob}', registry has '{registry_record.dob}'")

    if registry_record.gender.strip().upper() != gender.strip().upper():
        mismatches.append(f"Gender mismatch: provided '{gender}', registry has '{registry_record.gender}'")

    if mismatches:
        return {
            "status": "MISMATCH",
            "message": "; ".join(mismatches),
            "registry_record": registry_record
        }

    return {
        "status": "MATCH",
        "message": "Demographic details fully match Central APAAR Registry.",
        "registry_record": registry_record
    }
