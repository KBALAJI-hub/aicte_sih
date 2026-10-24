from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Institution, Student

router = APIRouter(prefix="/api/v1", tags=["REST Integration API"])


def verify_api_key(
    x_api_key: str = Header(..., description="Institution API Key"),
    session: Session = Depends(get_session)
) -> Institution:
    """Dependency verifying institution API key for automated machine integrations."""
    institution = session.exec(
        select(Institution).where(Institution.api_key == x_api_key)
    ).first()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key."
        )
    return institution


@router.get("/institution/profile")
async def get_institution_profile(
    institution: Institution = Depends(verify_api_key)
):
    """Returns authenticated institution profile."""
    return {
        "id": institution.id,
        "aicte_id": institution.aicte_id,
        "name": institution.name,
        "state": institution.state,
        "type": institution.institution_type
    }


@router.get("/students/{apaar_id}")
async def query_student_by_apaar(
    apaar_id: str,
    institution: Institution = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Retrieve student enrollment details under the authenticated institution."""
    student = session.exec(
        select(Student).where(
            Student.apaar_id == apaar_id.strip(),
            Student.institution_id == institution.id
        )
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with APAAR ID {apaar_id} not found under institution {institution.name}."
        )

    return {
        "apaar_id": student.apaar_id,
        "student_id": student.student_id,
        "full_name": student.full_name,
        "status": student.status,
        "admission_year": student.admission_year,
        "record_hash": student.record_hash
    }
