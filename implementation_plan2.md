# implementation_plan.md
## SIH 26263: APAAR ID-Based Student Data Management & Verification Platform (AICTE)
**Team:** 4 beginners | **Time:** 24 hours | **Build style:** LLM-assisted IDE, one codebase, runs locally

---

## 0. The Strategy in 60 Seconds

1. **You are not building AICTE's real system. You are building a convincing, working prototype that demonstrates the full pipeline** from the problem statement:
   `Institution → Upload → APAAR Validation → Verification → Central Repository → Analytics → Authorized Verification`
2. **Judges score what they see in the demo video and PPT.** A smooth 5-minute demo of 8-10 working features beats a half-working "complete" system.
3. **APAAR's real registry (via DigiLocker / ABC) is not publicly accessible.** Build a **Mock APAAR Registry** (a table of fake APAAR IDs) behind a clean adapter interface. Say clearly in the PPT: *"Plug-in point for the real APAAR/DigiLocker API."* This is the honest, standard hackathon approach.
4. **Hard feature freeze at Hour 14.** Hours 14-24 are for PPT, video, and submission. Do not break this rule.

---

## 1. Tech Stack (Deliberately Boring)

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.11+** | LLMs write it best; beginners can read it |
| Backend | **FastAPI** | Auto-generates Swagger docs at `/docs`, which directly demonstrates "API integration capability" (Req. 7) for free |
| Database | **SQLite** via **SQLModel** | Zero setup, single file, easy to reset and re-seed |
| Frontend | **Jinja2 server-rendered templates + Tailwind CSS (CDN) + Chart.js (CDN)** | No Node, no build step, no React debugging |
| Auth | **JWT in HTTP-only cookie**, `passlib[bcrypt]` hashing | Simple RBAC with a dependency function |
| Data processing | **pandas** | CSV upload parsing and validation |
| QR codes | `qrcode[pil]` | Verifiable record QR |
| PDF | Printable HTML page (browser "Save as PDF") | Avoids PDF-library pain |
| Anomaly detection | Rule-based + z-score (pandas); `scikit-learn` IsolationForest as stretch | Looks "intelligent", is easy |
| Run | `uvicorn app.main:app --reload` | No Docker, no cloud |

**Do NOT use:** microservices, Docker, Kubernetes, React/Next.js, Postgres, Redis, Celery, blockchain, real OTP/SMS, cloud deploy (unless you have spare time at the end).

---

## 2. Scope: What's IN and What's CUT

### MVP (Must Build)
| # | Feature | Maps to Requirement |
|---|---|---|
| 1 | Login with 3 roles: **AICTE Admin, Institution, Verifier** (RBAC) | 5, 8 |
| 2 | Institution can **add/edit a student** (form) and **bulk upload CSV** | 1, 2 |
| 3 | **Mock APAAR Registry** + APAAR validation (format, existence, name/DOB match) | 3 |
| 4 | **Validation engine** (duplicates, invalid APAAR, intake exceeded, inconsistencies, cross-institution duplicate) | 3 |
| 5 | **Anomaly detection** (enrolment surge, abnormal NRI/FN share, fill-ratio outliers) | Innovation |
| 6 | **Institution dashboard** and **AICTE dashboard** with charts | 4 |
| 7 | **Verification portal** for employers/regulators with **consent-aware** output | 5, 8 |
| 8 | **Verifiable student record**: HMAC-signed hash + QR code + public verify URL | 6 |
| 9 | **Certificate preview** showing Student ID + APAAR ID | 10 |
| 10 | **Audit log** page (who did what, when) | 8 |
| 11 | **Reports export** (CSV downloads + printable summary) | 9 |
| 12 | **Swagger API docs** + API-key endpoint for integration | 7 |

### Cut / Slide-Only (mention in PPT as "Future Scope")
- Real APAAR/DigiLocker integration, real OTP-based consent
- Blockchain, microservices, cloud autoscaling
- Multi-year historical analytics beyond seeded data
- Email/SMS notifications, full mobile responsiveness

> **Rule:** if a feature isn't in the MVP table, it does not get code. It may get a slide.

---

## 3. Team Roles (4 People, Minimal Conflict)

| Person | Role | Owns |
|---|---|---|
| **P1: Backend Lead** | FastAPI, DB models, auth, RBAC, API routes | `models.py`, `auth.py`, `routers/` |
| **P2: Validation & Data Lead** | Mock registry, seed data, validation engine, anomaly detection | `validation.py`, `anomaly.py`, `seed.py` |
| **P3: Frontend Lead** | Jinja templates, dashboards, Chart.js, certificate, verify page | `templates/`, `static/` |
| **P4: Product / Demo Lead** | PPT, demo script, video, README, testing, submission | `docs/`, `demo_script.md`, final QA |

**P4 is not "the non-coder."** From Hour 1, P4 writes the demo script, creates test CSVs (using the LLM), reviews each merged feature, and is the designated bug-reporter.

**Git:** one repo, each person on their own branch, merge to `main` every ~2 hours. Split by files (above) so conflicts are rare. Commit often. **Never** let the LLM "rewrite the whole project."

---

## 4. Timeline (24 Hours)

> Plan a sleep rotation: at least 2 people awake at all times, and everyone gets 3-4 hours of sleep between Hours 14-22 when work is mostly PPT/video.

| Hours | Phase | Output |
|---|---|---|
| 0-1 | **Phase 0: Setup & alignment** | Repo, venv, skeleton running on every laptop |
| 1-3 | **Phase 1: DB models, auth, RBAC, seed** | Login works for 3 roles; seeded data exists |
| 3-6 | **Phase 2: Student entry + CSV upload + validation engine** | Core pipeline works end-to-end |
| 6-9 | **Phase 3: Dashboards + anomaly detection** | Charts and flags visible |
| 9-11 | **Phase 4: Verification, signed records, QR, certificate, audit, reports** | All MVP features exist |
| 11-14 | **Phase 5: Integration testing, bug-fix, polish** | Stable demo flow |
| **14** | **FEATURE FREEZE** | `git tag v1-demo` |
| 14-18 | **Phase 6: PPT + architecture diagram + screenshots** | PPT draft complete |
| 18-21 | **Phase 7: Record demo video (2-3 takes) + edit** | Final video |
| 21-23 | **Phase 8: Submission prep** | Everything uploaded, double-checked |
| 23-24 | **Safety buffer** | Portal glitches, upload limits, last fixes |

---

## 5. Phase 0: Setup (Hours 0-1)

### Step 5.1: Environment
Everyone installs Python 3.11+, Git, and VS Code (or an AI IDE with a free LLM).

```bash
mkdir apaar-platform && cd apaar-platform
python -m venv venv
# Windows: venv\Scripts\activate    Mac/Linux: source venv/bin/activate
pip install fastapi "uvicorn[standard]" sqlmodel jinja2 python-multipart \
    "passlib[bcrypt]" "python-jose[cryptography]" pandas "qrcode[pil]" \
    scikit-learn faker itsdangerous
pip freeze > requirements.txt
```

> If `passlib`/`bcrypt` throws a version error, pin `bcrypt==4.0.1`.

### Step 5.2: Project Structure
```
apaar-platform/
├── app/
│   ├── main.py            # FastAPI app, router registration
│   ├── database.py        # engine, session
│   ├── models.py          # SQLModel tables
│   ├── auth.py            # login, JWT, role dependency
│   ├── apaar_registry.py  # mock registry adapter
│   ├── validation.py      # rules engine
│   ├── anomaly.py         # anomaly detection
│   ├── security.py        # HMAC signing, QR generation
│   ├── audit.py           # audit log helper
│   ├── routers/
│   │   ├── institution.py
│   │   ├── aicte.py
│   │   ├── verify.py
│   │   └── api.py         # JSON integration API
│   ├── templates/         # Jinja2 HTML
│   └── static/
├── seed.py                # generates demo data
├── sample_data/           # CSVs for demo (good + bad)
├── requirements.txt
└── README.md
```

### Step 5.3: The Master Context Prompt
**Paste this at the start of EVERY new LLM chat.** Save it in `docs/context_prompt.md`.

```
PROJECT CONTEXT:
I'm building a hackathon prototype "APAAR ID-based Student Data Management and
Verification Platform" for AICTE. Stack: Python 3.11, FastAPI, SQLModel + SQLite,
Jinja2 templates, Tailwind CSS via CDN, Chart.js via CDN, pandas. NO React, NO Docker,
NO microservices. Single codebase, runs with `uvicorn app.main:app --reload`.

RULES FOR YOU:
1. Keep code simple, beginner-readable, with short comments.
2. Only modify the files I mention. Never rewrite the whole project.
3. Give complete file contents for new files; for edits show only the changed functions.
4. Tell me exact terminal commands to run and what output to expect.
5. If something might fail, say how I'd see the error.

ROLES: AICTE_ADMIN, INSTITUTION, VERIFIER.
KEY TABLES: User, Institution, Program, ApaarRegistry (mock), Student, ValidationFlag, AuditLog.
APAAR ID = 12-digit numeric string.
```

### Step 5.4: Smoke Test
Prompt: *"Create `app/main.py` with a FastAPI app, a Jinja2 templates folder, and a `/` route rendering `base.html` with Tailwind CDN. Show the run commands."* Everyone must see the page at `http://127.0.0.1:8000` and Swagger at `/docs`. **Commit and push.**

---

## 6. Phase 1: Data Model, Auth, Seed (Hours 1-3)

### Step 6.1: Data Model (P1)

| Table | Key Fields |
|---|---|
| `User` | id, username, password_hash, role, institution_id (nullable), full_name |
| `Institution` | id, aicte_id, name, state, institution_type, api_key |
| `Program` | id, institution_id, name, level (UG/PG/Diploma/PGDM), academic_year, **approved_intake**, **supernumerary_cap** |
| `ApaarRegistry` (mock) | apaar_id (12 digits, unique), full_name, dob, gender |
| `Student` | id, **apaar_id**, institution_id, program_id, student_id (roll no.), full_name, dob, gender, category, **admission_type** (REGULAR / SUPERNUMERARY), **is_nri**, **oci_status**, **is_foreign_national**, nationality, admission_year, mode (FULL_TIME/PART_TIME), status (ACTIVE/WITHDRAWN/GRADUATED), **consent_given**, consent_timestamp, record_hash, created_at, updated_at |
| `ValidationFlag` | id, institution_id, program_id, student_id (nullable), rule_code, severity (HIGH/MEDIUM/LOW), message, status (OPEN/RESOLVED), created_at |
| `AuditLog` | id, user_id, username, action, entity, entity_id, details, timestamp |
| `VerificationLog` | id, verifier_id, apaar_id, result, timestamp |

**Prompt:**
> "Using SQLModel, create `app/models.py` and `app/database.py` for these tables: [paste table]. Add `create_db_and_tables()` called at startup. Use SQLite file `apaar.db`."

### Step 6.2: Auth + RBAC (P1)
- Login page, `POST /login` sets a JWT in an HTTP-only cookie.
- Dependency `require_role("AICTE_ADMIN")` protects routes.
- Redirect after login: Admin → `/aicte/dashboard`, Institution → `/institution/dashboard`, Verifier → `/verify`.

**Prompt:**
> "Create `app/auth.py` with bcrypt hashing, JWT creation/decoding (python-jose), login and logout routes, a `get_current_user` dependency reading a cookie, and a `require_role(*roles)` dependency factory. Add `login.html`."

### Step 6.3: Seed Data (P2). The Most Important Step for a Good Demo
`seed.py` creates:
- **1 AICTE admin** (`aicte_admin` / `Admin@123`)
- **5 institutions** (mix of Engineering, PGDM, Pharmacy, Management), each with one institution user (`inst1`..`inst5` / `Inst@123`) and an API key
- **2-4 programs per institution**, approved intake like 60, 120, 180, for **two academic years**
- **1 verifier** (`employer1` / `Verify@123`)
- **~800 mock APAAR registry entries** (12-digit IDs, `Faker("en_IN")` names)
- **~500 students**, mostly clean, with **deliberately planted problems**:
  - Institution 3, one program: enrolment at 135% of intake
  - 3 duplicate APAAR IDs within one institution
  - 4 APAAR IDs enrolled at two institutions simultaneously
  - 5 APAAR IDs not in the registry
  - 5 name/DOB mismatches vs the registry
  - Institution 4 with ~40% NRI share
  - Institution 2 with a 3x year-on-year enrolment jump
  - A few `is_foreign_national=True` rows with `nationality="India"`
- `consent_given=True` for ~70%, `False` for ~30%
- Use fixed seeds (`Faker.seed(42)`, `random.seed(42)`) so every reset gives the same data

**Prompt:**
> "Write `seed.py` using Faker('en_IN') and my models. It resets the DB and creates [list above], planting the specific data problems so a validation engine will find them. Print login credentials at the end."

**Checkpoint (Hour 3):** `python seed.py`, run the server, log in as all 3 roles. Commit.

---

## 7. Phase 2: Student Entry, CSV Upload, Validation (Hours 3-6)

### Step 7.1: Mock APAAR Registry Adapter (P2)
`app/apaar_registry.py`:
```python
def validate_apaar_format(apaar_id: str) -> bool: ...   # 12 digits, numeric
def lookup_apaar(apaar_id: str) -> dict | None: ...      # query ApaarRegistry table
def match_identity(apaar_id, name, dob) -> bool: ...     # fuzzy name match + exact DOB
```
Design it as an **interface**. Put this in the PPT: *"Replace `lookup_apaar` with an HTTPS call to the real APAAR/DigiLocker API."*

### Step 7.2: Validation Rules (P2)

| Code | Rule | Severity | Level |
|---|---|---|---|
| **R1** | APAAR missing or not exactly 12 digits | HIGH | Row |
| **R2** | APAAR not found in registry | HIGH | Row |
| **R3** | Name/DOB doesn't match registry | MEDIUM | Row |
| **R4** | Duplicate APAAR within the same institution | HIGH | Row |
| **R5** | Same APAAR actively enrolled (full-time) at another institution | HIGH | Cross |
| **R6** | Regular admissions in a program exceed approved intake | HIGH | Program |
| **R7** | Supernumerary admissions exceed cap | MEDIUM | Program |
| **R8** | Inconsistent data: NRI and FN both true; FN but nationality India; OCI but nationality India; implausible age; future admission year | MEDIUM | Row |
| **R9** | Mandatory fields missing (name, DOB, program, admission year) | HIGH | Row |
| **R10** | Consent not captured | LOW | Row |

> **Assumption to state in the PPT:** the supernumerary cap is configurable per program (demo default: 10% of intake). NRI/OCI/FN are tracked as separate fields so AICTE can apply its own limits.

**Prompt:**
> "Create `app/validation.py`. Write `validate_student_row(row, session)` returning a list of flags for R1-R5 and R8-R10, and `validate_program_intake(program_id, session)` for R6-R7. Each flag has rule_code, severity, message. Add `run_full_validation(institution_id, session)` which clears old OPEN flags and regenerates them. Keep each rule a small separate function."

### Step 7.3: Student Form + CSV Upload (P1 + P3)
**Institution routes:**
- `GET /institution/students`: table with search, program filter, flag badges
- `GET/POST /institution/students/new` and `/{id}/edit`
- `GET /institution/upload`: upload page with a "Download CSV template" link
- `POST /institution/upload`: parse with pandas, show a summary such as *"120 rows: 104 accepted, 11 with warnings, 5 rejected"*, with a downloadable error-report CSV

**CSV columns:** `apaar_id, student_id, full_name, dob, gender, category, program_name, admission_year, admission_type, is_nri, oci_status, is_foreign_national, nationality, mode, consent_given`

**Simple, explainable behavior:** rows with HIGH row-level errors (R1, R2, R9) are **rejected** and listed in the error report. Everything else is **accepted with flags**.

**Prompt:**
> "In `app/routers/institution.py` add CSV upload using pandas. For each row run `validate_student_row`; reject rows with HIGH row-level flags, save the rest as Students with flags in ValidationFlag. Afterwards call `validate_program_intake` for affected programs. Show a result page with counts and an error CSV download. Write an audit log entry."

### Step 7.4: Audit Helper (P1)
`audit.py`: `log_action(session, user, action, entity, entity_id, details)`. Call it from login, student create/edit, upload, verification, and report export.

**Checkpoint (Hour 6):** Upload `sample_data/bad_upload.csv` (P4 creates it with intentional errors) and confirm correct rejections and flags. Merge.

---

## 8. Phase 3: Dashboards + Anomaly Detection (Hours 6-9)

### Step 8.1: Anomaly Detection (P2), `app/anomaly.py`
Keep it explainable. Each anomaly gets a plain-English reason.

| Code | Check | Method |
|---|---|---|
| **A1** | Fill-ratio outlier vs peers | z-score of (enrolment/intake); flag \|z\| > 2 or ratio > 1.0 |
| **A2** | Year-on-year surge | growth > 50% vs previous year |
| **A3** | Abnormal NRI / FN / OCI share | share above threshold (e.g., 15%) or z-score > 2 vs institution-type average |
| **A4** | Suspicious cluster | many students sharing one DOB (e.g., 01-01) in one program |
| **A5 (stretch)** | IsolationForest on `[fill_ratio, nri_share, fn_share, yoy_growth]` per institution | Show an anomaly score |

Also compute an **Institution Compliance Score (0-100)**: start at 100, subtract weighted penalties for open HIGH/MEDIUM flags. It is trivial to build and looks great on a dashboard.

### Step 8.2: Institution Dashboard (P3)
- KPI cards: Total Students, Approved Intake, Fill %, Open Flags, Compliance Score
- Bar chart: **Approved Intake vs Actual Enrolment** by program (red if exceeded)
- Doughnut: category / NRI / OCI / FN / Supernumerary breakdown
- Table: open flags with "view student" and "resolve" actions

### Step 8.3: AICTE Dashboard (P3)
- KPI cards: Institutions, Total Enrolment, Total Intake, Flagged Institutions, Cross-institution Duplicates
- Bar chart: top institutions by fill ratio
- Chart: flags by rule type
- Table: institutions ranked by compliance score, with drill-down
- **Alerts panel**: latest HIGH-severity flags
- **Auto-refresh**: `setInterval` JS refetches `/api/aicte/summary` every 10 seconds. An upload in another tab changing the dashboard is your "real-time" demo moment.
- Filters: state, institution type, academic year

**Prompt (one per dashboard):**
> "Create `GET /aicte/dashboard` and a JSON endpoint `GET /api/aicte/summary` in `routers/aicte.py` returning totals, per-institution intake vs enrolment, flags grouped by rule_code, and top alerts. Create `aicte_dashboard.html` extending `base.html` with Tailwind KPI cards and Chart.js charts that fetch that JSON and refresh every 10 seconds."

**Checkpoint (Hour 9):** Both dashboards show the planted anomalies. Commit.

---

## 9. Phase 4: Verification, Signed Records, Certificate, Reports (Hours 9-11)

### Step 9.1: Verifiable Record (P1), `security.py`
- `compute_record_hash(student)`: HMAC-SHA256 over a canonical string of `apaar_id | student_id | institution aicte_id | program | admission_year | status`, using a server secret.
- Save to `Student.record_hash` on create/update.
- `GET /verify/record/{student_id}?sig=<hash>` is a **public** page that recomputes the hash and shows **"Authentic record"** or **"Tampered / not found"** with minimal info.
- A QR code (via `qrcode`) encodes that URL and appears on the student record page and certificate.

> PPT wording: *"Digital signature (HMAC in the prototype; production would use asymmetric signing, e.g., RSA/ECDSA with managed keys)."*

### Step 9.2: Verification Portal with Consent (P1 + P3)
**Roles:** VERIFIER (employers, regulators); AICTE can use it too.
- Enter an APAAR ID and get a result.
- **Consent logic (key privacy demo):**
  - Found + `consent_given=True`: show institution, program, admission year, status, authenticity badge.
  - Found + `consent_given=False`: show only *"APAAR valid. Student has not consented to share details."*
  - Not found: *"No record."*
- Every lookup writes a `VerificationLog` and audit entry, shown in "My verification history".
- **Student consent toggle:** a simple page `/consent/{apaar_id}`, labeled "simulated DigiLocker consent flow." Real OTP/DigiLocker consent goes in Future Scope.

### Step 9.3: Certificate Preview (P3), Requirement 10
`GET /certificate/{student_id}` is a printable HTML page styled as a degree certificate: institution, student name, program, **Student ID | APAAR ID**, QR code, and a signature snippet. Add a "Print / Save as PDF" button (`window.print()`) with print CSS.

### Step 9.4: Reports (P2 / P3)
AICTE and institutions can download (CSV via `Response` with `text/csv`):
- Enrolment vs intake
- Validation flags
- Category / NRI / OCI / FN breakdown
- Cross-institution duplicates
- A printable "Compliance Summary" HTML page for accreditation use

### Step 9.5: Integration API (P1), Requirement 7
In `routers/api.py` (auto-documented in Swagger):
- `POST /api/v1/students/bulk` (JSON array), authenticated with an **`X-API-Key`** header per institution
- `GET /api/v1/students/{apaar_id}/verify`
- `GET /api/v1/institutions/{aicte_id}/summary`

In the demo, open `/docs`, click "Try it out" on the bulk endpoint, and show it succeed. It takes 20 seconds and proves interoperability.

### Step 9.6: Audit Log Page
`GET /aicte/audit` (admin only): table filterable by user, action, and date.

**Checkpoint (Hour 11):** Every MVP row is ticked. Tag `mvp-complete`.

---

## 10. Phase 5: Integration, Testing, Polish (Hours 11-14)

### 10.1 Test Script (P4 drives; others fix)
Run this sequence **three times from a fresh `python seed.py`**:

| # | Action | Expected |
|---|---|---|
| 1 | Login as `inst3` | Dashboard shows intake exceeded (red) |
| 2 | Upload `bad_upload.csv` | Rejected + flagged rows reported; error CSV downloads |
| 3 | Add one student via form with a valid APAAR | Appears in list; record hash created |
| 4 | Add the same APAAR again | R4 duplicate flag |
| 5 | Add a student whose APAAR is active at another institution | R5 cross-institution flag |
| 6 | Login as `aicte_admin` | New flags appear (auto-refresh) |
| 7 | Open anomaly alerts | NRI-share and surge anomalies with reasons |
| 8 | Login as `employer1`, verify a consented APAAR | Full details + authentic badge |
| 9 | Verify a non-consented APAAR | Limited result only |
| 10 | Open a certificate's QR link | "Authentic record" |
| 11 | Change a student's field directly in the DB, reopen the link | "Tampered" (great demo moment) |
| 12 | Call the bulk API from `/docs` with an API key | 200 OK |
| 13 | Check the audit log | All the above actions appear |
| 14 | Institution user opens `/aicte/dashboard` | 403 / redirect (RBAC proof) |

### 10.2 Polish (only if tests pass)
- Role-based navbar, title "APAAR Verify: AICTE Student Data Platform"
- Color-coded severity badges
- Friendly error pages and empty states
- An admin-only **"Reset demo data"** button that re-runs the seed (a lifesaver for video retakes)
- README with run instructions and credentials

### 10.3 FEATURE FREEZE at Hour 14
- `git tag v1-demo`, zip a backup of the folder and `apaar.db`.
- From now on: bug fixes only, and only if visible in the demo.

---

## 11. LLM Prompting Playbook

1. **One small task per prompt.** "Create the student form route and template" is good. "Build the whole institution module" is bad.
2. **Paste the master context prompt** at the start of every new chat.
3. **Give the LLM the full traceback** plus the relevant file: *"Here's the error and the file. Fix only this."*
4. **Ask for complete files** when they're small (under ~150 lines) to avoid broken partial edits.
5. **Run after every prompt.** Never stack three unverified changes.
6. **If the LLM loops** (same bug 3 times): `git checkout` to revert, restate the requirement concretely, or ask for "the simplest possible version, ignoring edge cases."
7. **Free-tier rate limits:** spread work across teammates' accounts and tools; keep prompts tight.
8. **Use the LLM for non-code work too:** seed CSVs, PPT text, demo script, README, test cases.
9. **Don't let it change the stack** ("let's switch to React/Postgres" → no).
10. **Commit before every risky prompt.** `git commit -am "before X"` is your undo button.

---

## 12. Phase 6: PPT (Hours 14-18), P4 leads, all contribute

Check the official SIH PPT template and slide limits first, then fit this content in:

| Slide | Content |
|---|---|
| 1 | Title, team name, PS ID **26263**, theme *Smart Automation* |
| 2 | **Problem**: fragmented student data (only PGDM gives detail, others give totals), no verifiability, excess/duplicate enrolment risk |
| 3 | **Solution**: one-line pitch + pipeline graphic |
| 4 | **Key Features** mapped to the 10 requirements |
| 5 | **Architecture Diagram** (see §13) |
| 6 | **Validation & Anomaly Engine**: rules table, explainable flags, compliance score |
| 7 | **Security & Privacy**: RBAC, JWT/bcrypt, audit trail, consent-based verification, signed records + QR, data minimization |
| 8 | **Innovation / USP**: cross-institution duplicate detection, anomaly alerts, compliance score, tamper-evident QR records, consent-aware verification |
| 9 | **Screenshots**: dashboards, upload result, verification result, certificate |
| 10 | **Integration**: REST API, API keys, Swagger, adapter for real APAAR/DigiLocker, embedding in the AICTE portal |
| 11 | **Feasibility & Scalability**: SQLite → PostgreSQL, containers, queued bulk uploads, caching, NIC/cloud deployment (roadmap) |
| 12 | **Impact**: for AICTE, institutions, students, employers |
| 13 | **Future Scope**: real APAAR API, DigiLocker consent, ML models, multilingual UI, mobile app |
| 14 | **Tech stack & Team** |

**Be honest on the slides:** "Prototype uses a simulated APAAR registry; the adapter is designed to swap in the real API." Judges respect clear prototype boundaries more than vague overclaims.

---

## 13. Architecture Diagram (draw.io / Excalidraw, ~20 min)

```
 [Institution Portal]   [Institution ERP/Systems]
        │ (Web form / CSV)        │ (REST API + API Key)
        └───────────┬─────────────┘
                    ▼
        ┌──────────────────────────┐
        │   FastAPI Application    │
        │  Auth + RBAC + Audit     │
        │  ┌────────────────────┐  │
        │  │ Validation Engine  │──┼──► APAAR Registry Adapter ─► (Mock now / Real APAAR API later)
        │  │ Anomaly Engine     │  │
        │  │ Signing + QR       │  │
        │  └────────────────────┘  │
        └────────────┬─────────────┘
                     ▼
          [AICTE Central Repository (DB)]
              │              │
              ▼              ▼
   [AICTE Analytics     [Verification Portal / API]
    Dashboards,          Employers, Regulators
    Reports]             (consent-aware)
```

---

## 14. Phase 7: Demo Video (Hours 18-21)

### 14.1 Format
- **4-5 minutes** (check the SIH limit; shorter is safer). Screen recording + voiceover.
- Tools: OBS Studio, Windows Game Bar, or Loom. Edit with CapCut / DaVinci Resolve / Clipchamp.
- Click "Reset demo data" before every take. Record at 1080p, zoom the browser to 110-125%, hide bookmarks, silence notifications.

### 14.2 Demo Script

| Time | Scene | Voiceover gist |
|---|---|---|
| 0:00-0:30 | Title + problem | "AICTE lacks record-level, verifiable student data. We built an APAAR-based platform to fix that." |
| 0:30-1:00 | Architecture slide | One sentence per block |
| 1:00-1:50 | **Institution login → upload CSV**: validation results, rejected rows, error report | "Every row is validated against the APAAR registry in seconds." |
| 1:50-2:20 | **Add a student with a duplicate / cross-institution APAAR** → flag raised | "Same student enrolled twice? Caught instantly." |
| 2:20-3:10 | **AICTE dashboard (live update)**, anomaly alerts, compliance ranking, drill-down | "AICTE sees excess intake and risky institutions in real time." |
| 3:10-3:50 | **Verifier**: consented vs non-consented lookup, QR authenticity, tamper demo | "Privacy-first verification with tamper-evident records." |
| 3:50-4:20 | **Certificate with APAAR ID + Student ID**, report download, Swagger API call | "Covers certificate, reporting, and integration requirements." |
| 4:20-4:45 | Audit log + RBAC denial | "Every action is audited; access is role-based." |
| 4:45-5:00 | Closing | Impact, future scope, team |

### 14.3 Recording Tips
- Write the voiceover first; read it while recording.
- Record **scene by scene** and stitch together. Don't attempt one perfect take.
- Do a timed dry run first.
- Keep a backup take of each scene.
- Check audio with headphones; bad audio hurts more than rough visuals.
- Export MP4 (H.264) and check the portal's file-size limit (compress with HandBrake if needed).

---

## 15. Phase 8: Submission (Hours 21-24)

- [ ] PPT in the **official template**, exported in the required format
- [ ] Demo video within size/time limits; tested on another device
- [ ] GitHub repo with README: setup steps, credentials, screenshots, architecture
- [ ] Zip backup of the code
- [ ] Optional unlisted YouTube upload as a backup link
- [ ] Team details and PS ID entered correctly
- [ ] A teammate opens all submitted links from their own account
- [ ] Screenshot of the submission confirmation
- [ ] **Submit at least 2 hours before the deadline**, because portals lag near deadlines

---

## 16. Risk Register & Cut Order

| Risk | Mitigation |
|---|---|
| LLM code breaks something | Commit often; revert fast; small prompts |
| Merge conflicts | File ownership by role; merge every ~2 hours |
| A feature isn't done by the freeze | **Cut order (first → last):** IsolationForest → filters → non-CSV reports → editable consent page → API-key endpoint → QR tamper demo. **Never cut:** upload + validation, AICTE dashboard, verification, certificate |
| Demo glitch while recording | "Reset demo data" button; deterministic seed |
| Dependency errors | Pin versions in `requirements.txt`; test in a fresh venv by Hour 3 |
| Team exhaustion | Sleep rotation; P4 drafts PPT while coders finish |
| Free LLM rate limits | Multiple accounts/tools; tight prompts |

---

## 17. Demo Credentials (put in README)

| Role | Username | Password |
|---|---|---|
| AICTE Admin | `aicte_admin` | `Admin@123` |
| Institution (1-5) | `inst1` ... `inst5` | `Inst@123` |
| Verifier / Employer | `employer1` | `Verify@123` |

---

## 18. Final Reminders

1. **A working, smooth, demonstrable pipeline wins.** Don't chase perfection.
2. **Map every feature to a numbered requirement** from the problem statement; judges check against it.
3. **State prototype boundaries honestly** (mock registry, simulated consent) and show how production would replace them.
4. **Freeze at Hour 14. No exceptions.** The video and PPT are what get scored.
5. Sleep a little. A rested team records a better video than an exhausted one.

Good luck. Build, freeze, record, submit.
