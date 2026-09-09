# Sahakar Sahayak (सहकार सहायक) 🇮🇳
### Digital Guide & Intelligence Platform for Cooperative Societies

Sahakar Sahayak is an intelligent, bilingual digital kiosk and assistant tailored for the Indian cooperative ecosystem under the guidance of cooperative policies and schemes.

---

## 🔐 Complete Authentication System

A production-grade, secure authentication system implemented across both frontend (React 19 + Vite) and backend (FastAPI + SQLAlchemy + SQLite).

### 1. Key Features

- **Registration with Email & Phone**:
  - Requires Full Name, Email Address, Indian Mobile Number (`+91` format or 10-digit), Password, User Type, and Preferred Language (`en`, `hi`, `kn`, `ne`).
  - Both `email` and `phone` are uniquely stored in the database.
  - Enforces duplicate detection with HTTP `409 Conflict`:
    - Duplicate email: `"Email is already registered. Please log in or use a different email."`
    - Duplicate phone: `"Phone number is already registered. Please log in or use a different phone number."`
- **Dual-Identifier Login**:
  - Users can log in using **either** their registered **Email** OR their registered **Phone Number** (`+91 9876543210` or `9876543210`) with password.
  - Returns clear, meaningful errors for wrong passwords (HTTP `401`) and unregistered accounts (HTTP `404`).
- **Cryptographic Security**:
  - Passwords hashed using standard **PBKDF2-HMAC-SHA256** with 100,000 iterations and 16-byte random salts.
  - Timing attack prevention via constant-time digest verification.
  - Signed **JWT (JSON Web Tokens)** issued upon authentication for stateless session handling.
- **Profile Management & Session Persistence**:
  - Fully integrated Profile page allowing viewing and updating details, including phone number.
  - Auto-synchronization on app reload via `/api/auth/me`.
  - Guest mode exploration preserved without friction.

---

## 📡 Authentication API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register with name, email, phone (`+91`), password | No |
| `POST` | `/api/auth/login` | Log in with Email OR Phone + password | No |
| `GET` | `/api/auth/me` | Fetch currently authenticated user profile | Yes (Bearer JWT) |
| `PUT` | `/api/auth/profile` | Update profile with email/phone duplicate check | Yes (Bearer JWT) |

---

## 📂 Summary of Changes & Architecture

### Backend Changes
- **`backend/models/database.py`**: SQLite database connection via SQLAlchemy with `init_db()` auto-migration.
- **`backend/models/user.py`**: `User` model with unique indexed `email` and `phone` columns, hashed passwords, roles, and timestamps.
- **`backend/models/auth_schemas.py`**: Pydantic schemas for registration, login, profile updates, and authentication tokens.
- **`backend/services/auth_service.py`**: PBKDF2 password hasher, phone number normalizer with Indian `+91` and 10-digit suffix matching, JWT generator/decoder, and FastAPI auth dependency.
- **`backend/routes/auth.py`**: FastAPI router handling registration, dual-identifier login, profile updates, and duplicate conflict detection.
- **`backend/main.py`**: Mounted authentication endpoints at `/api/auth` and `/auth` with startup database lifecycle initialization.
- **`backend/test_auth.py`**: Comprehensive 8-step automated test suite validating the complete auth flow.

### Frontend Changes
- **`src/services/authService.js`**: Real HTTP API client communicating with backend auth endpoints.
- **`src/context/AppContext.jsx`**: Global auth state management with JWT token persistence in `localStorage` and startup `/api/auth/me` verification.
- **`src/pages/Register.jsx`**: Added Indian Phone Number input (`+91 9876543210`), `.gov.in` placeholders, and duplicate error alerts.
- **`src/pages/Login.jsx`**: Added dual Email/Phone identifier input and user-friendly error messages.
- **`src/pages/Profile.jsx`**: Added phone number viewing and editing with backend synchronization.
- **`src/pages/Help.jsx`**: Updated national contact details to Ministry of Cooperation, New Delhi, India.
- **`src/locales/` (`en.js`, `hi.js`, `kn.js`, `ne.js`)**: Added localized strings for `phoneNumber` and `emailOrPhone`.
- **`vite.config.js`**: Configured dev server proxy forwarding `/api` to backend port 8000.
- **`.gitignore`**: Ignored local SQLite database files (`*.db`, `*.sqlite`, `*.sqlite3`).

---

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
# Install npm dependencies
npm install

# Start development server
npm run dev
```
Open `http://localhost:5173` in your browser.

### 4. Running Automated Auth Tests
```bash
python backend/test_auth.py
```
All 8 automated test cases verify registration, duplicate email/phone prevention, email login, phone login, wrong password rejection, and authenticated endpoints.
