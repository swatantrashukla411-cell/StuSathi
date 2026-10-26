# CampusPilot AI — Voice-First Personal Academic Agent

> **A production-grade, voice-first academic co-pilot for college students.**  
> Powered by FastAPI, SQLAlchemy, Next.js 14, Web Audio API, and Gemini 1.5 Flash Tool Orchestration.  
> Includes a direct live integration connector for **Quantum University (QUMS)**.

---

## 📸 Key Features & Architecture

```
[ Student Voice / Hinglish Query / Text ]
                   │
                   ▼
       [ Next.js 14 Responsive UI ] ◄─── (Live QUMS Sync with Real Captcha Stream)
                   │
                   ▼
      [ FastAPI Modular Monolith ]
                   │
                   ├──► [ Agent Orchestration (Gemini 1.5 Flash) ]
                   │             │
                   │             ▼ (Tool Calls)
                   ├──► [ Deterministic Attendance & GPA Engines (Zero AI Math!) ]
                   │
                   ├──► [ Schedule Engine (Live Countdown to Next Class) ]
                   │
                   └──► [ Async SQLAlchemy 2.0 Database Models (Multi-Tenant) ]
```

### 1. Attendance Intelligence Engine
* **Deterministic Calculations:** Strict mathematical formulas for current attendance, max safe bunks allowed, and 75% recovery targets.
* **What-If Absence Simulator:** Real-time projection of semester-end attendance when missing $y$ upcoming classes.
* **Risk Categorization:** Automatically flags subjects as `SAFE` ($\ge 80\%$), `CAUTION` ($75\% - 79.9\%$), `CRITICAL` ($< 75\%$), or `UNRECOVERABLE`.

### 2. Quantum University (QUMS) Live Connector
* **Real-Time Captcha Streaming:** Fetches live session and Base64 captcha images directly from `https://qums.quantumuniversity.edu.in`.
* **Zero Password Storage in Database:** Credentials are processed strictly in-memory during the single sync request and immediately flushed from RAM.
* **Automatic Table Parsing:** BeautifulSoup4 extracts Subject Code, Name, Conducted, and Attended lectures from the student dashboard.

### 3. Voice-First Conversational Agent
* **Multi-Lingual:** Fluent in English, Hindi, and natural college Hinglish.
* **Function Calling Tools:**
  * `get_today_schedule()`
  * `get_next_class()`
  * `get_subject_attendance(subject)`
  * `simulate_absence(subject, count)`
  * `calculate_attendance_recovery(subject)`
  * `calculate_required_future_sgpa(target_cgpa)`

---

## 🚀 Quickstart & Setup Guide

### 1. Backend Setup (FastAPI)
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run automated test suite (45/45 tests passing!)
pytest -q tests

# Seed realistic student database (Swatantra Shukla, B.Tech CSE Sem 5)
python -m apps.api.src.seed_data

# Start FastAPI server on port 8000
uvicorn apps.api.src.main:app --reload --port 8000
```
Interactive API documentation available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup (Next.js 14)
```bash
cd apps/web

# Start Next.js development server on port 3000
npm run dev
```
Open in browser: `http://localhost:3000`

---

## 🧪 Test Verification Report

```bash
$ pytest tests
============================= test session starts =============================
tests/test_attendance_service.py ................                       [ 35%]
tests/test_gpa_service.py .........                                     [ 55%]
tests/test_api_endpoints.py ..........                                  [ 77%]
tests/test_qums_service.py ...                                          [ 84%]
tests/test_agent_orchestrator.py .......                                [100%]
============================== 45 passed in 4.53s ==============================
```
