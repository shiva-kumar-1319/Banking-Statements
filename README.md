# BankSense AI — Intelligent Banking Statement Analysis Platform

[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.x-blue.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.x-purple.svg)](https://vitejs.dev/)
[![JWT Auth](https://img.shields.io/badge/Auth-JWT%20SimpleJWT-orange.svg)](https://jwt.io/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **BankSense AI** transforms unstructured PDF, CSV, and Excel bank statements into actionable financial intelligence, dynamic dashboards, spending insights, and interactive AI assistance grounded in mathematical certainty.

---

## 🌐 Live Deployment & Demo Links

- **Live Application Link:** [https://banksense-ai.onrender.com](https://banksense-ai.onrender.com) *(or your deployed Render/Railway domain)*
- **GitHub Repository:** [https://github.com/shiva-kumar-1319/Banking-Statements](https://github.com/shiva-kumar-1319/Banking-Statements)

### Pre-Seeded Demo Credentials
| Field | Value |
| :--- | :--- |
| **Username** | `demo_user` |
| **Password** | `Password123!` |
| **Connected Accounts** | Primary Salary Account (HDFC) & Personal Savings (ICICI) |
| **Preloaded Activity** | 25 multi-month verified transactions, recurring bills, and categorized expenses |

---

## 🏛️ System Architecture

BankSense AI employs a clean, decoupled architecture separating presentation, API routing, business services, deterministic arithmetic, and parsing pipelines.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        BankSense AI Frontend                           │
│     React 18  •  Vite  •  Lucide Icons  •  Dark / Light Theme          │
│   (Dashboard, Accounts, Upload, Review Preview, Explorer, Assistant)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST + Bearer JWT
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Django REST Framework Gateway                       │
│    SimpleJWT Auth  •  Multi-Tenant User Isolation  •  Rate Limiting   │
└──────────────┬────────────────────┬────────────────────┬───────────────┘
               │                    │                    │
    ┌──────────▼─────────┐ ┌────────▼─────────┐ ┌────────▼─────────┐
    │  Statement Engine  │ │ Analytics Engine │ │ AI Grounding Svc │
    │  • PDF (pdfplumber)│ │ • Cashflow Trends│ │ • Intent Parser  │
    │  • CSV Sniffer     │ │ • Category Split │ │ • Exact Metrics  │
    │  • XLSX (openpyxl) │ │ • Recurring Dets │ │ • Zero-Fakes LLM │
    │  • Reconciler      │ │ • Anomalies      │ │ • Math Fallback  │
    └──────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
               │                    │                    │
┌──────────────▼────────────────────▼────────────────────▼───────────────┐
│                 Persistent Storage & Decimal Integrity                 │
│         SQLite3 (Local Dev)  •  PostgreSQL (Production Cloud)          │
│                Exact Decimal(14, 2) Monetary Precision                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Simple Understanding of How It Works
1. **Multi-Tenant Authentication:** Each user creates an account. Data rows (Bank Accounts, Statements, Transactions) are strictly isolated by `user_id`. One customer can never see another customer's financial records.
2. **Multi-Format Ingestion:** You upload a bank statement (`.pdf`, `.csv`, `.xlsx`).
3. **Deterministic Extraction & Categorization:** The engine parses tables and text, computes a SHA-256 hash to reject duplicate uploads, checks balance reconciliation (`Opening + Credits - Debits == Closing`), and maps entries to 12 explainable categories (Salary, Food, Shopping, Rent, Bills, Travel, etc.).
4. **Interactive Verification Preview:** Users review extracted transactions and reconciliation warnings **before** committing to persistent storage.
5. **Grounded AI Financial Assistant:** When users ask questions like *"How much did I spend on food?"* or *"What were my top five expenses?"*, deterministic Python functions query the database and calculate verified values first. The LLM only formats the natural explanation — **it is strictly prohibited from inventing financial figures.**

---

## ✨ Core Modules & Capabilities

- **Module 1: Authentication & Security:** User registration, JWT access/refresh token rotation, PBKDF2 password hashing, and user-level query filtering.
- **Module 2: Bank Account Portfolio:** Create and track multiple accounts (Savings, Checking, Credit Card, Investment), view masked account numbers (`•••• 1024`), and recalculate balances.
- **Module 3: Universal Statement Upload:** Support for PDF, CSV, and XLSX files up to 10MB with drag-and-drop, format validation, and duplicate file prevention.
- **Module 4: Transaction Extraction & Reconciliation:** Normalized date parsing (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD Mon YYYY`), debit/credit detection, and closing balance verification.
- **Module 5: Dynamic Dashboard:** Live summary cards (Total Balance, Income, Expenses, Savings Rate), monthly income vs. expense bars, category distribution, and recent activity.
- **Module 6: Transaction Explorer:** Full-text search, multi-filter dropdowns (account, category, date range, min/max amount), sort ordering, pagination, and one-click CSV export.
- **Module 7: Grounded AI Assistant:** Conversational agent with suggested prompt chips and zero-hallucination mathematical grounding. Works with Gemini, OpenAI, or the built-in deterministic analytics engine.
- **Module 8: Explainable Categorization:** 12 categories with confidence scoring and manual user overrides.
- **Module 9: Spending Insights:** Automated detection of recurring subscriptions (Netflix, broadband, rent) and statistical spending anomalies/spikes.
- **Module 10: Report Generation:** Instant download of print-ready **PDF Statement Reports** (ReportLab) and **raw CSV exports**.
- **Module 11: Production Fintech UI:** Built with React and Vite, featuring smooth transitions, accessible controls, and dark/light mode.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.10+ (Python 3.13 supported)
- Node.js 18+ and npm
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/shiva-kumar-1319/Banking-Statements.git
cd Banking-Statements
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
cd banking
python manage.py migrate

# Seed sample demo account and transactions
python manage.py seed_demo_data
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run build
```

### 4. Run the Application
You can run the unified production build via Django:
```bash
cd ../banking
python manage.py runserver 127.0.0.1:8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser. Log in with:
- **Username:** `demo_user`
- **Password:** `Password123!`

*(For hot-reloading frontend development, run `npm run dev` in `frontend/` on port 5173).*

---

## 🧪 Testing with Sample Bank Statements

Synthetic statement files are provided in `sample_statements/` for immediate testing:
1. `sample_statements/sample_bank_statement.csv`: Standard 6-column banking CSV.
2. `sample_statements/sample_salary_account.xlsx`: Excel statement with multiple date and amount formats.
3. `sample_statements/sample_premium_statement.pdf`: Multi-column bank statement PDF.

To regenerate sample files at any time:
```bash
python create_sample_statements.py
```

---

## 🚢 Deployment Guide

### Deploying to Render (Recommended)
1. Fork or push this repository to your GitHub account.
2. Sign in to [Render](https://render.com/) and create a **New Web Service**.
3. Select your repository. Render will automatically detect `render.yaml` or you can configure:
   - **Environment:** `Python 3`
   - **Build Command:** `npm --prefix frontend install && npm --prefix frontend run build && pip install -r requirements.txt && python banking/manage.py migrate && python banking/manage.py collectstatic --noinput && python banking/manage.py seed_demo_data`
   - **Start Command:** `gunicorn --chdir banking banking.wsgi:application --bind 0.0.0.0:$PORT`
4. Set environment variables:
   - `DJANGO_SECRET_KEY`: Random 50-character string
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: `.onrender.com`

### Deploying with Docker
```bash
# Build and run container
docker-compose up --build
```
Access at `http://localhost:8000`.

---

## 🛡️ Automated Test Suite

Run the full automated test suite covering authentication, account CRUD, multi-tenant isolation, PDF/CSV/Excel parsing, reconciler, and AI grounding:
```bash
cd banking
python manage.py test
```
**Results:** `Ran 15 tests ... OK (0 failures)`.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/auth/register/` | `POST` | Register user & initialize user profile |
| `/api/token/` / `/api/auth/login/` | `POST` | Obtain JWT access and refresh tokens |
| `/api/token/refresh/` | `POST` | Rotate JWT access token |
| `/api/auth/me/` | `GET`, `PATCH` | Fetch or update user profile and currency |
| `/api/accounts/` | `GET`, `POST` | List and create user bank accounts |
| `/api/accounts/{id}/` | `GET`, `PATCH`, `DELETE` | Retrieve, edit, or delete bank account |
| `/api/accounts/{id}/recalculate/`| `POST` | Recalculate account balance from transactions |
| `/api/statements/` | `GET`, `POST` | List and upload statement files (multipart) |
| `/api/statements/{id}/confirm/` | `POST` | Finalize and import verified transactions |
| `/api/transactions/` | `GET` | Filterable and searchable transaction explorer |
| `/api/transactions/categories/` | `GET` | List available transaction categories |
| `/api/transactions/{id}/update_category/` | `PATCH` | Override transaction category |
| `/api/analytics/dashboard/` | `GET` | Summary KPIs, trends, and recent records |
| `/api/analytics/insights/` | `GET` | Recurring obligations, anomalies, MoM comparison |
| `/api/assistant/chat/` | `POST` | Conversational grounded AI query assistant |
| `/api/reports/financial-summary/pdf/`| `GET` | Download official formatted PDF audit report |
| `/api/reports/transactions/csv/`| `GET` | Export filtered transaction records to CSV |

---

## 📄 License
This project is licensed under the MIT License.
