# Tax Filing Agent - Startup Guide

## Quick Start

### 1. Database Setup
Ensure PostgreSQL is running with pgvector extension:
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database and user
CREATE DATABASE tax_filing_db;
CREATE USER taxagent WITH PASSWORD 'taxagent_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE tax_filing_db TO taxagent;

-- Enable pgvector extension
\c tax_filing_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Backend Setup
```cmd
cd backend

:: Create virtual environment (if not exists)
python -m venv venv

:: Activate virtual environment
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Copy environment file
copy .env.dev .env

:: Run backend
python main.py
```

**Backend URLs:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/health

### 3. Frontend Setup
```cmd
:: Install dependencies (in root folder)
npm install

:: Run frontend
npm run dev
```

**Frontend URL:** http://localhost:8080

---

## One-Click Start
Double-click `run_app.bat` to start both backend and frontend.

---

## Troubleshooting

### PostgreSQL Connection Error
- Check if PostgreSQL service is running
- Verify credentials in `backend/.env`
- Ensure pgvector extension is installed

### Import Errors in Backend
- Make sure you're in the `backend` directory
- Virtual environment must be activated
- Run `pip install -r requirements.txt`

### Frontend Not Loading
- Check if npm dependencies are installed
- Look for errors in browser console
- Verify backend is running (CORS)

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)
- `GET /api/auth/me` - Get current user

### Tax Filing
- `GET /api/chat/filing/start/{session_id}` - Start conversational filing
- `POST /api/chat/filing/respond` - Send response in filing conversation
- `GET /api/chat/filing/status/{session_id}` - Get filing status
- `POST /api/chat/filing/generate-pdf/{session_id}` - Generate ITR-1 PDF

### Chat
- `POST /api/chat/message` - Send chat message to AI
- `GET /api/chat/history/{session_id}` - Get chat history
