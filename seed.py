"""
seed.py - Populates apaar.db with initial demonstration records:
1. Users for each role (AICTE_ADMIN, INSTITUTION, VERIFIER)
2. Sample AICTE Institution & Academic Program
3. Mock Central APAAR Registry records for cross-verification
"""

from sqlmodel import Session, select
from app.auth import hash_password
from app.database import create_db_and_tables, engine
from app.models import ApaarRegistry, Institution, Program, User


def seed_database():
    print("Checking database tables...")
    create_db_and_tables()

    with Session(engine) as session:
        # 1. Use existing Institution or create demo one
        institution = session.exec(select(Institution)).first()

        if not institution:
            institution = Institution(
                aicte_id="1-10023456",
                name="Delhi Technological University (DTU)",
                state="Delhi",
                institution_type="State University",
                api_key="dtu-demo-api-key-2026"
            )
            session.add(institution)
            session.commit()
            session.refresh(institution)
            print(f"[+] Seeded Institution: {institution.name} (ID: {institution.id})")
        else:
            print(f"[i] Using existing Institution: {institution.name} (ID: {institution.id}, AICTE: {institution.aicte_id})")

        # 2. Check Academic Program for this Institution
        program = session.exec(
            select(Program).where(Program.institution_id == institution.id)
        ).first()

        if not program:
            program = Program(
                institution_id=institution.id,
                course="B.Tech Computer Science and Engineering",
                level="UG",
                academic_year="2024-2025",
                intake=60
            )
            session.add(program)
            session.commit()
            session.refresh(program)
            print(f"[+] Seeded Program: {program.course} (Approved Intake: {program.approved_intake})")
        else:
            print(f"[i] Using existing Program: {program.course} (Approved Intake: {program.approved_intake})")

        # 3. Seed Users for All 3 Roles
        demo_users = [

            {
                "username": "admin",
                "password": "admin123",
                "role": "AICTE_ADMIN",
                "full_name": "Dr. Rajesh Sharma (AICTE Chief)",
                "institution_id": None
            },
            {
                "username": "college_admin",
                "password": "college123",
                "role": "INSTITUTION",
                "full_name": "Prof. Anita Roy (Dean DTU)",
                "institution_id": institution.id
            },
            {
                "username": "verifier_tcs",
                "password": "verifier123",
                "role": "VERIFIER",
                "full_name": "Vikram Sen (TCS Background Verification)",
                "institution_id": None
            }
        ]

        for u_data in demo_users:
            user = session.exec(select(User).where(User.username == u_data["username"])).first()
            if not user:
                user = User(
                    username=u_data["username"],
                    password_hash=hash_password(u_data["password"]),
                    role=u_data["role"],
                    full_name=u_data["full_name"],
                    institution_id=u_data["institution_id"]
                )
                session.add(user)
                print(f"[+] Seeded User: {u_data['username']} ({u_data['role']})")

        # 4. Seed Mock Central APAAR Registry (12-digit numeric IDs)
        sample_apaar_records = [
            {"apaar_id": "100000000001", "full_name": "Aarav Sharma", "dob": "2004-05-14", "gender": "MALE"},
            {"apaar_id": "100000000002", "full_name": "Diya Patel", "dob": "2003-11-22", "gender": "FEMALE"},
            {"apaar_id": "100000000003", "full_name": "Rohan Verma", "dob": "2004-01-30", "gender": "MALE"},
            {"apaar_id": "100000000004", "full_name": "Ananya Iyer", "dob": "2004-08-09", "gender": "FEMALE"},
            {"apaar_id": "100000000005", "full_name": "Kabir Mehta", "dob": "2003-07-19", "gender": "MALE"},
            {"apaar_id": "100000000006", "full_name": "Sanya Gupta", "dob": "2004-03-25", "gender": "FEMALE"},
            {"apaar_id": "100000000007", "full_name": "Ishaan Nair", "dob": "2003-12-11", "gender": "MALE"},
            {"apaar_id": "100000000008", "full_name": "Pooja Deshmukh", "dob": "2004-09-03", "gender": "FEMALE"},
            {"apaar_id": "100000000009", "full_name": "Aditya Rao", "dob": "2004-04-18", "gender": "MALE"},
            {"apaar_id": "100000000010", "full_name": "Meera Joshi", "dob": "2003-06-27", "gender": "FEMALE"},
        ]

        for reg in sample_apaar_records:
            exists = session.get(ApaarRegistry, reg["apaar_id"])
            if not exists:
                session.add(ApaarRegistry(**reg))

        session.commit()
        print(f"[+] Seeded {len(sample_apaar_records)} Central APAAR Registry records.")
        print("\nDatabase seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
