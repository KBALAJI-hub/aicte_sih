from typing import Dict, List
from sqlmodel import Session, select
from app.apaar_registry import is_valid_apaar_format, verify_against_registry
from app.models import Program, Student, ValidationFlag


def validate_single_student(
    session: Session,
    student_data: dict,
    institution_id: int,
    program_id: int
) -> List[ValidationFlag]:
    """
    Applies AICTE compliance rules to a student record and generates flags if violated.
    """
    flags: List[ValidationFlag] = []
    apaar_id = str(student_data.get("apaar_id", "")).strip()
    full_name = str(student_data.get("full_name", "")).strip()
    dob = str(student_data.get("dob", "")).strip()
    gender = str(student_data.get("gender", "")).strip()
    admission_type = str(student_data.get("admission_type", "REGULAR")).strip().upper()

    # Rule 1: 12-digit numeric APAAR ID format
    if not is_valid_apaar_format(apaar_id):
        flags.append(ValidationFlag(
            institution_id=institution_id,
            program_id=program_id,
            rule_code="RULE_INVALID_APAAR_FORMAT",
            severity="HIGH",
            message=f"Student '{full_name}' has invalid APAAR ID '{apaar_id}'. Must be exactly 12 digits.",
            status="OPEN"
        ))
    else:
        # Rule 2: Cross-check against mock Central APAAR Registry
        reg_result = verify_against_registry(session, apaar_id, full_name, dob, gender)
        if reg_result["status"] == "NOT_FOUND":
            flags.append(ValidationFlag(
                institution_id=institution_id,
                program_id=program_id,
                rule_code="RULE_REGISTRY_NOT_FOUND",
                severity="HIGH",
                message=f"APAAR ID {apaar_id} does not exist in Central Registry.",
                status="OPEN"
            ))
        elif reg_result["status"] == "MISMATCH":
            flags.append(ValidationFlag(
                institution_id=institution_id,
                program_id=program_id,
                rule_code="RULE_DEMOGRAPHIC_MISMATCH",
                severity="MEDIUM",
                message=f"Registry mismatch for APAAR {apaar_id}: {reg_result['message']}",
                status="OPEN"
            ))

        # Rule 3: Duplicate enrollment check across institutions
        existing_active = session.exec(
            select(Student).where(
                Student.apaar_id == apaar_id,
                Student.status == "ACTIVE"
            )
        ).all()
        if existing_active:
            inst_ids = {s.institution_id for s in existing_active}
            if inst_ids != {institution_id}:
                flags.append(ValidationFlag(
                    institution_id=institution_id,
                    program_id=program_id,
                    rule_code="RULE_DUPLICATE_ENROLLMENT",
                    severity="HIGH",
                    message=f"APAAR {apaar_id} is simultaneously enrolled active in another institution.",
                    status="OPEN"
                ))

    return flags


def check_program_intake_limits(
    session: Session,
    institution_id: int,
    program_id: int
) -> List[ValidationFlag]:
    """
    Verifies that total active students in a program do not breach approved sanctioned limits.
    """
    flags: List[ValidationFlag] = []
    program = session.get(Program, program_id)
    if not program:
        return flags

    # Count current active regular and supernumerary students
    regular_count = len(session.exec(
        select(Student).where(
            Student.program_id == program_id,
            Student.status == "ACTIVE",
            Student.admission_type == "REGULAR"
        )
    ).all())

    supernumerary_count = len(session.exec(
        select(Student).where(
            Student.program_id == program_id,
            Student.status == "ACTIVE",
            Student.admission_type == "SUPERNUMERARY"
        )
    ).all())

    # Regular intake breach
    if regular_count > program.approved_intake:
        flags.append(ValidationFlag(
            institution_id=institution_id,
            program_id=program_id,
            rule_code="RULE_INTAKE_CAP_EXCEEDED",
            severity="HIGH",
            message=f"Regular admissions ({regular_count}) exceed approved intake ({program.approved_intake}) for '{program.name}'.",
            status="OPEN"
        ))

    # Supernumerary quota breach
    if supernumerary_count > program.supernumerary_cap:
        flags.append(ValidationFlag(
            institution_id=institution_id,
            program_id=program_id,
            rule_code="RULE_SUPERNUMERARY_CAP_EXCEEDED",
            severity="HIGH",
            message=f"Supernumerary admissions ({supernumerary_count}) exceed allowed quota ({program.supernumerary_cap}) for '{program.name}'.",
            status="OPEN"
        ))

    return flags
