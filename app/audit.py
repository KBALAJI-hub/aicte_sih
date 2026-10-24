from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session
from app.models import AuditLog, User


def log_audit(
    session: Session,
    action: str,
    entity: str,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
    user: Optional[User] = None
) -> AuditLog:
    """
    Records an immutable audit trail entry for system operations.
    """
    audit_entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "SYSTEM",
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id else None,
        details=details,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(audit_entry)
    session.commit()
    session.refresh(audit_entry)
    return audit_entry
