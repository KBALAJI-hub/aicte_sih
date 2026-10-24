from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Returns timezone-aware UTC datetime for SQLModel compatibility."""
    return datetime.now(timezone.utc)


# 1. User Account Model
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    role: str  # AICTE_ADMIN, INSTITUTION, VERIFIER
    institution_id: Optional[int] = Field(default=None, foreign_key="institutions.id")
    full_name: str


# 2. Institution Model (Original 13,000+ AICTE colleges)
class Institution(SQLModel, table=True):
    __tablename__ = "institutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    aicte_id: str = Field(unique=True, index=True)  # Official AICTE Permanent ID
    name: str
    university: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    institution_type: Optional[str] = None  # Central, State, Private, Deemed, etc.
    women: Optional[str] = None
    minority: Optional[str] = None
    other_id: Optional[str] = None
    source_year: Optional[str] = None
    api_key: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=utc_now)
    updated_at: Optional[datetime] = Field(default_factory=utc_now)


# 3. Academic Program Model (Original 58,000+ AICTE sanctioned programs)
class Program(SQLModel, table=True):
    __tablename__ = "programs"

    id: Optional[int] = Field(default=None, primary_key=True)
    institution_id: int = Field(foreign_key="institutions.id")
    programme: Optional[str] = None
    level: Optional[str] = None  # UG, PG, DIPLOMA
    course: str = Field(default="GENERAL")  # e.g., MECHANICAL ENGINEERING
    course_type: Optional[str] = None
    shift: Optional[str] = None
    availability: Optional[str] = None
    intake: Optional[int] = Field(default=60)  # Sanctioned intake capacity
    enrollment: Optional[int] = None
    placement: Optional[int] = None
    academic_year: str = "2024-2025"

    @property
    def name(self) -> str:
        return self.course

    @property
    def approved_intake(self) -> int:
        return self.intake or 60

    @property
    def supernumerary_cap(self) -> int:
        return int((self.intake or 60) * 0.25)


# 4. Mock Central APAAR Registry (Original table: mock_apaar_registry)
class ApaarRegistry(SQLModel, table=True):
    __tablename__ = "mock_apaar_registry"

    apaar_id: str = Field(primary_key=True, index=True)  # 12-digit numeric identifier
    full_name: str
    dob: Optional[str] = None  # YYYY-MM-DD
    gender: Optional[str] = None  # MALE, FEMALE, TRANSGENDER
    created_at: Optional[datetime] = Field(default_factory=utc_now)


# 5. Student Enrollment Record Model (Original table: students)
class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: Optional[int] = Field(default=None, primary_key=True)
    apaar_id: str = Field(index=True)  # 12-digit numeric string
    institution_id: int = Field(foreign_key="institutions.id")
    program_id: int = Field(foreign_key="programs.id")
    student_id: str  # Roll number / Enrollment ID
    full_name: str
    dob: Optional[str] = None  # YYYY-MM-DD
    gender: Optional[str] = None
    category: Optional[str] = "GENERAL"  # GENERAL, OBC, SC, ST, EWS
    admission_type: str = "REGULAR"  # REGULAR / SUPERNUMERARY
    is_nri: bool = False
    oci_status: bool = False
    is_foreign_national: bool = False
    nationality: Optional[str] = "Indian"
    admission_year: int = 2024
    mode: str = "FULL_TIME"  # FULL_TIME / PART_TIME
    status: str = "ACTIVE"  # ACTIVE / WITHDRAWN / GRADUATED
    consent_given: bool = True
    consent_timestamp: Optional[datetime] = None
    record_hash: Optional[str] = None  # SHA-256 HMAC for tamper verification
    created_at: Optional[datetime] = Field(default_factory=utc_now)
    updated_at: Optional[datetime] = Field(default_factory=utc_now)


# 6. Validation Flag Model (Original table: validation_flags)
class ValidationFlag(SQLModel, table=True):
    __tablename__ = "validation_flags"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(default=None, foreign_key="students.id")
    institution_id: Optional[int] = Field(default=None, foreign_key="institutions.id")
    program_id: Optional[int] = Field(default=None, foreign_key="programs.id")
    flag_type: Optional[str] = None
    rule_code: Optional[str] = None  # e.g., RULE_FORMAT, RULE_INTAKE_BREACH
    severity: str = "MEDIUM"  # HIGH / MEDIUM / LOW
    description: Optional[str] = None
    message: Optional[str] = None
    status: str = "OPEN"  # OPEN / RESOLVED
    detected_at: Optional[datetime] = Field(default_factory=utc_now)
    created_at: Optional[datetime] = Field(default_factory=utc_now)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


# 7. System Audit Log Model (Original table: audit_logs)
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    institution_id: Optional[int] = None
    actor_type: Optional[str] = "USER"
    actor_id: Optional[str] = None
    action: str  # e.g., CSV_UPLOAD, VERIFY_APAAR, FLAG_RESOLVED
    entity_type: Optional[str] = None
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=utc_now)
    created_at: Optional[datetime] = Field(default_factory=utc_now)


# 8. Third-Party Verification Query Log Model (Original table: verification_logs)
class VerificationLog(SQLModel, table=True):
    __tablename__ = "verification_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: Optional[int] = None
    institution_id: Optional[int] = None
    requested_by: Optional[str] = None
    verification_type: Optional[str] = "APAAR_LOOKUP"
    verifier_id: Optional[int] = None
    apaar_id: Optional[str] = Field(default=None, index=True)
    result: str = "VERIFIED"  # e.g., VERIFIED, NOT_FOUND, DATA_MISMATCH
    message: Optional[str] = None
    checked_at: Optional[datetime] = Field(default_factory=utc_now)
    timestamp: Optional[datetime] = Field(default_factory=utc_now)

