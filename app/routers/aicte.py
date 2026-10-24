from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlmodel import Session, select

from app.auth import require_role
from app.database import get_session
from app.models import AuditLog, Institution, Program, Student, User, ValidationFlag

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter(prefix="/aicte", tags=["AICTE Admin Portal"])


from sqlmodel import func

@router.get("/dashboard")
async def aicte_dashboard(
    request: Request,
    user: User = Depends(require_role("AICTE_ADMIN")),
    session: Session = Depends(get_session)
):
    """
    Central AICTE Admin oversight dashboard with nationwide metrics and open alerts.
    """
    total_institutions = session.exec(select(func.count(Institution.id))).one()
    total_programs = session.exec(select(func.count(Program.id))).one()
    total_students = session.exec(select(func.count(Student.id))).one()
    open_flags = session.exec(
        select(func.count(ValidationFlag.id)).where(ValidationFlag.status == "OPEN")
    ).one()
    recent_logs = session.exec(
        select(AuditLog).order_by(AuditLog.id.desc()).limit(15)
    ).all()

    return {
        "admin": user.username,
        "total_institutions": total_institutions,
        "total_programs": total_programs,
        "total_students": total_students,
        "open_validation_flags": open_flags,
        "recent_audit_events": len(recent_logs)
    }



@router.get("/flags")
async def list_all_flags(
    user: User = Depends(require_role("AICTE_ADMIN")),
    session: Session = Depends(get_session)
):
    """List all open regulatory flags across all institutions."""
    return session.exec(select(ValidationFlag).where(ValidationFlag.status == "OPEN")).all()


@router.get("/audit-logs")
async def list_audit_logs(
    user: User = Depends(require_role("AICTE_ADMIN")),
    session: Session = Depends(get_session)
):
    """Inspection endpoint for immutable system audit logs."""
    return session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50)).all()
