# AICTE APAAR ID Student Data Management & Verification Platform

A unified, tamper-evident student data compliance and credential verification platform for AICTE-approved institutions and background verifiers using the **12-digit APAAR ID** (Automated Permanent Academic Account Registry).

---

## 🛠️ Tech Stack
- **Backend:** Python 3.11, FastAPI
- **Database:** SQLModel + SQLite (`apaar.db`)
- **Frontend:** Jinja2 Templates, Tailwind CSS (via CDN), Chart.js (via CDN)
- **Data & Security:** pandas, bcrypt, python-jose (JWT), HMAC-SHA256, qrcode

---

## 📁 Project Structure
```
apaar-platform/
├── app/
│   ├── main.py            # FastAPI app, router registration
│   ├── database.py        # SQLite engine, session generator
│   ├── models.py          # SQLModel database tables
│   ├── auth.py            # Login, JWT cookies, role dependencies
│   ├── apaar_registry.py  # Mock Central APAAR Registry adapter
│   ├── validation.py      # AICTE compliance & intake rules engine
│   ├── anomaly.py         # Anomaly & intake saturation detection
│   ├── security.py        # HMAC-SHA256 signing, QR code generation
│   ├── audit.py           # System audit log helper
│   ├── routers/
│   │   ├── institution.py # Institution batch CSV upload & flag resolution
│   │   ├── aicte.py       # AICTE Admin oversight & nationwide analytics
│   │   ├── verify.py      # Third-party verifier lookup & QR verification
│   │   └── api.py         # JSON integration API for external systems
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html
│   │   └── login.html
│   └── static/            # Static assets & styling
├── seed.py                # Generates initial demo users, colleges & mock APAAR DB
├── sample_data/           # Demonstration CSV datasets
│   ├── good_students.csv  # Clean batch conforming to sanctioned intake
│   └── bad_students.csv   # Batch containing regulatory discrepancies
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Seed Demo Data
Populate demo institutions, academic programs, mock APAAR registry, and role accounts:
```bash
python seed.py
```

### 2. Start Application Server
```bash
python -m uvicorn app.main:app --reload
```

- **Web Portal:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Sign In:** [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)
- **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Demo Credentials

| Role | Username | Password | Purpose |
|---|---|---|---|
| **AICTE_ADMIN** | `admin` | `admin123` | Nationwide oversight, flag inspection, audit trails |
| **INSTITUTION** | `college_admin` | `college123` | DTU college staff, CSV roster upload, flag resolution |
| **VERIFIER** | `verifier_tcs` | `verifier123` | Third-party background verifier, QR credential checks |
