from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlmodel import Session, select

from app.auth import require_role
from app.database import get_session
from app.models import AuditLog, Institution, Program, Student, User, ValidationFlag

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter(prefix="/aicte", tags=["AICTE Admin Portal"])


@router.get("/dashboard", response_class=HTMLResponse)
async def aicte_dashboard(
    request: Request,
    user: User = Depends(require_role("AICTE_ADMIN")),
    session: Session = Depends(get_session)
):
    """
    Central AICTE Admin oversight dashboard with nationwide metrics and open alerts.
    """
    institutions = session.exec(select(Institution)).all()
    programs = session.exec(select(Program)).all()
    students = session.exec(select(Student)).all()
    flags = session.exec(select(ValidationFlag).where(ValidationFlag.status == "OPEN")).all()
    recent_logs = session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(15)).all()

    return {
        "admin": user.username,
        "total_institutions": len(institutions),
        "total_programs": len(programs),
        "total_students": len(students),
        "open_validation_flags": len(flags),
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
