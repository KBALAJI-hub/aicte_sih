from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.auth import get_current_user_optional
from app.database import get_session
from app.models import Institution, Program, Student, VerificationLog
from app.security import generate_qr_code_base64, verify_student_hash

router = APIRouter(prefix="/verify", tags=["Credential Verification"])


@router.get("/{apaar_id}")
async def verify_student(
    apaar_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Direct verification of a student's academic credentials using their 12-digit APAAR ID.
    Performs tamper-evidence checks and returns a cryptographically verified payload.
    """
    cleaned_id = str(apaar_id).strip()

    # Query active student record
    student = session.exec(
        select(Student).where(
            Student.apaar_id == cleaned_id,
            Student.status == "ACTIVE"
        )
    ).first()

    verifier_user = get_current_user_optional(request, session)
    verifier_id = verifier_user.id if verifier_user else None

    if not student:
        # Log negative verification attempt
        session.add(VerificationLog(
            verifier_id=verifier_id,
            apaar_id=cleaned_id,
            result="NOT_FOUND",
            timestamp=datetime.now(timezone.utc)
        ))
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active student record found for APAAR ID: {cleaned_id}"
        )

    # Check HMAC hash integrity
    is_tamper_free = verify_student_hash(
        apaar_id=student.apaar_id,
        institution_id=student.institution_id,
        program_id=student.program_id,
        student_id=student.student_id,
        dob=student.dob,
        expected_hash=student.record_hash
    )

    institution = session.get(Institution, student.institution_id)
    program = session.get(Program, student.program_id)

    # Log successful verification event
    session.add(VerificationLog(
        verifier_id=verifier_id,
        apaar_id=cleaned_id,
        result="VERIFIED" if is_tamper_free else "TAMPERED",
        timestamp=datetime.now(timezone.utc)
    ))
    session.commit()

    # Generate QR Code for mobile verification
    qr_data = f"AICTE-VERIFIED|APAAR:{student.apaar_id}|NAME:{student.full_name}|INST:{institution.name if institution else ''}|INTEGRITY:{'OK' if is_tamper_free else 'FAIL'}"
    qr_code_b64 = generate_qr_code_base64(qr_data)

    return {
        "status": "VERIFIED" if is_tamper_free else "TAMPER_SUSPECTED",
        "apaar_id": student.apaar_id,
        "full_name": student.full_name,
        "institution": institution.name if institution else None,
        "program": program.name if program else None,
        "admission_year": student.admission_year,
        "enrollment_status": student.status,
        "tamper_proof_valid": is_tamper_free,
        "qr_code_preview": qr_code_b64
    }
