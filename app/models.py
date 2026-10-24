from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Returns timezone-aware UTC datetime for SQLModel compatibility."""
    return datetime.now(timezone.utc)


# 1. User Account Model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    role: str  # AICTE_ADMIN, INSTITUTION, VERIFIER
    institution_id: Optional[int] = Field(default=None, foreign_key="institution.id")
    full_name: str


# 2. Institution Model
class Institution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    aicte_id: str = Field(unique=True, index=True)  # Official AICTE Permanent ID
    name: str
    state: str
    institution_type: str  # Central, State, Private, Deemed
    api_key: Optional[str] = None


# 3. Academic Program Model
class Program(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    institution_id: int = Field(foreign_key="institution.id")
    name: str  # e.g., B.Tech Computer Science
    level: str  # UG, PG, Diploma, PGDM
    academic_year: str  # e.g., 2024-2025
    approved_intake: int = Field(default=60)  # Sanctioned intake capacity
    supernumerary_cap: int = Field(default=15)  # NRI/PIO/CW allowed cap


# 4. Mock Central APAAR Registry (Simulates Government APAAR DB)
class ApaarRegistry(SQLModel, table=True):
    apaar_id: str = Field(primary_key=True, index=True)  # 12-digit numeric identifier
    full_name: str
    dob: str  # YYYY-MM-DD
    gender: str  # MALE, FEMALE, TRANSGENDER


# 5. Student Enrollment Record Model
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    apaar_id: str = Field(index=True)  # 12-digit numeric string
    institution_id: int = Field(foreign_key="institution.id")
    program_id: int = Field(foreign_key="program.id")
    student_id: str  # Roll number / Enrollment ID
    full_name: str
    dob: str  # YYYY-MM-DD
    gender: str
    category: str = "GENERAL"  # GENERAL, OBC, SC, ST, EWS
    admission_type: str = "REGULAR"  # REGULAR / SUPERNUMERARY
    is_nri: bool = False
    oci_status: bool = False
    is_foreign_national: bool = False
    nationality: str = "Indian"
    admission_year: int
    mode: str = "FULL_TIME"  # FULL_TIME / PART_TIME
    status: str = "ACTIVE"  # ACTIVE / WITHDRAWN / GRADUATED
    consent_given: bool = True
    consent_timestamp: Optional[datetime] = None
    record_hash: Optional[str] = None  # SHA-256 HMAC for tamper verification
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# 6. Validation Flag Model (Discrepancies & Violations)
class ValidationFlag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    institution_id: int = Field(foreign_key="institution.id")
    program_id: Optional[int] = None
    student_id: Optional[int] = None
    rule_code: str  # e.g., RULE_FORMAT, RULE_INTAKE_BREACH, RULE_REGISTRY_MISMATCH
    severity: str = "MEDIUM"  # HIGH / MEDIUM / LOW
    message: str
    status: str = "OPEN"  # OPEN / RESOLVED
    created_at: datetime = Field(default_factory=utc_now)


# 7. System Audit Log Model
class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str  # e.g., CSV_UPLOAD, VERIFY_APAAR, FLAG_RESOLVED
    entity: str  # e.g., Student, Program, Flag
    entity_id: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=utc_now)


# 8. Third-Party Verification Query Log Model
class VerificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    verifier_id: Optional[int] = None
    apaar_id: str = Field(index=True)
    result: str  # e.g., VERIFIED, NOT_FOUND, DATA_MISMATCH
    timestamp: datetime = Field(default_factory=utc_now)
