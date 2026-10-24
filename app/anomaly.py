from typing import Any, Dict, List
from sqlmodel import Session, select
from app.models import Program, Student, ValidationFlag


def detect_institution_anomalies(session: Session, institution_id: int) -> List[Dict[str, Any]]:
    """
    Analyzes an institution's data for operational and regulatory anomalies.
    """
    anomalies = []

    # 1. High Flag Ratio Anomaly
    total_students = len(session.exec(
        select(Student).where(Student.institution_id == institution_id)
    ).all())

    open_flags = len(session.exec(
        select(ValidationFlag).where(
            ValidationFlag.institution_id == institution_id,
            ValidationFlag.status == "OPEN"
        )
    ).all())

    if total_students > 0 and (open_flags / total_students) > 0.15:
        anomalies.append({
            "type": "HIGH_FLAG_RATE",
            "severity": "HIGH",
            "message": f"High discrepancy rate: {open_flags} open validation flags across {total_students} students (>{15}%)."
        })

    # 2. Intake saturation / capacity warning (>90% full)
    programs = session.exec(
        select(Program).where(Program.institution_id == institution_id)
    ).all()

    for prog in programs:
        active_count = len(session.exec(
            select(Student).where(
                Student.program_id == prog.id,
                Student.status == "ACTIVE"
            )
        ).all())

        if prog.approved_intake > 0:
            utilization = (active_count / prog.approved_intake) * 100
            if utilization >= 100:
                anomalies.append({
                    "type": "CAPACITY_OVERFLOW",
                    "severity": "HIGH",
                    "message": f"Program '{prog.name}' is at {utilization:.1f}% capacity ({active_count}/{prog.approved_intake})."
                })
            elif utilization >= 90:
                anomalies.append({
                    "type": "CAPACITY_NEAR_LIMIT",
                    "severity": "MEDIUM",
                    "message": f"Program '{prog.name}' is near saturation ({utilization:.1f}% of approved intake)."
                })

    return anomalies
