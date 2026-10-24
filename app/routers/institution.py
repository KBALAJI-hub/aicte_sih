from typing import Optional
import io
import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import Session, select

from app.auth import get_current_user, require_role
from app.audit import log_audit
from app.database import get_session
from app.models import Institution, Program, Student, User, ValidationFlag
from app.security import generate_student_hash
from app.validation import check_program_intake_limits, validate_single_student

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/institution", tags=["Institution Portal"])


@router.get("/dashboard", response_class=HTMLResponse)
async def institution_dashboard(
    request: Request,
    user: User = Depends(require_role("INSTITUTION", "AICTE_ADMIN")),
    session: Session = Depends(get_session)
):
    """
    Renders institution management dashboard with program capacities and student statistics.
    """
    inst_id = user.institution_id
    institution = session.get(Institution, inst_id) if inst_id else None

    # Fetch programs belonging to this institution
    programs = session.exec(
        select(Program).where(Program.institution_id == inst_id)
    ).all() if inst_id else []

    # Fetch total enrolled students
    students = session.exec(
        select(Student).where(Student.institution_id == inst_id)
    ).all() if inst_id else []

    # Fetch open validation flags
    flags = session.exec(
        select(ValidationFlag).where(
            ValidationFlag.institution_id == inst_id,
            ValidationFlag.status == "OPEN"
        )
    ).all() if inst_id else []

    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={
            "request": request,
            "title": "Institution Dashboard | AICTE APAAR",
            "user": user,
            "institution": institution,
            "programs": programs,
            "total_students": len(students),
            "open_flags": len(flags)
        }
    )


@router.post("/upload-csv")
async def upload_student_csv(
    program_id: int = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(require_role("INSTITUTION", "AICTE_ADMIN")),
    session: Session = Depends(get_session)
):
    """
    Ingests and validates student CSV batches against approved intake and APAAR Registry.
    """
    inst_id = user.institution_id
    if not inst_id:
        raise HTTPException(status_code=400, detail="User not assigned to an institution.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    inserted_count = 0
    generated_flags = 0

    for _, row in df.iterrows():
        student_data = row.to_dict()
        apaar_id = str(student_data.get("apaar_id", "")).strip()

        # Run compliance rules
        flags = validate_single_student(session, student_data, inst_id, program_id)
        for flag in flags:
            session.add(flag)
            generated_flags += 1

        # Generate cryptographic tamper-evident hash
        rec_hash = generate_student_hash(
            apaar_id=apaar_id,
            institution_id=inst_id,
            program_id=program_id,
            student_id=str(student_data.get("student_id", "")),
            dob=str(student_data.get("dob", ""))
        )

        student = Student(
            apaar_id=apaar_id,
            institution_id=inst_id,
            program_id=program_id,
            student_id=str(student_data.get("student_id", "")),
            full_name=str(student_data.get("full_name", "")),
            dob=str(student_data.get("dob", "")),
            gender=str(student_data.get("gender", "")),
            category=str(student_data.get("category", "GENERAL")),
            admission_type=str(student_data.get("admission_type", "REGULAR")),
            admission_year=int(student_data.get("admission_year", 2024)),
            record_hash=rec_hash
        )
        session.add(student)
        inserted_count += 1

    # Check program capacity limit breach
    cap_flags = check_program_intake_limits(session, inst_id, program_id)
    for cf in cap_flags:
        session.add(cf)
        generated_flags += 1

    session.commit()

    # Log audit entry
    log_audit(
        session=session,
        action="BATCH_CSV_UPLOAD",
        entity="Student",
        details=f"Uploaded {inserted_count} students into program {program_id}. Generated {generated_flags} flags.",
        user=user
    )

    return {
        "status": "success",
        "students_imported": inserted_count,
        "flags_raised": generated_flags
    }
