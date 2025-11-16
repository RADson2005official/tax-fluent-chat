# PostgreSQL Setup Guide

## Option 1: Docker Installation (Recommended)

### Install Docker Desktop for Windows

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the prompts
3. Restart your computer after installation
4. Start Docker Desktop

### Start PostgreSQL with Docker

After Docker is installed, run:

```powershell
cd "d:\final year project\tax-fluent-chat"
docker compose up -d postgres
```

This will:
- Download PostgreSQL 15 Alpine image
- Create a container named `tax-agent-db`
- Initialize the database with `init-db.sql`
- Expose PostgreSQL on port 5432
- Set up pgAdmin on port 5050

### Access PostgreSQL

**Via Command Line:**
```powershell
docker exec -it tax-agent-db psql -U taxagent -d tax_filing_db
```

**Via pgAdmin:**
1. Open browser: http://localhost:5050
2. Login with:
   - Email: admin@taxagent.com
   - Password: admin123
3. Add server:
   - Host: postgres (Docker network) or host.docker.internal
   - Port: 5432
   - Database: tax_filing_db
   - Username: taxagent
   - Password: taxagent_secure_password_2024

---

## Option 2: Native PostgreSQL Installation

### Install PostgreSQL on Windows

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer (PostgreSQL 15 recommended)
3. During installation:
   - Set password for postgres user
   - Use default port 5432
   - Install pgAdmin 4

### Create Database and User

Open PowerShell and run:

```powershell
# Connect to PostgreSQL
psql -U postgres

# In psql prompt, run:
CREATE DATABASE tax_filing_db;
CREATE USER taxagent WITH PASSWORD 'taxagent_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE tax_filing_db TO taxagent;
ALTER DATABASE tax_filing_db OWNER TO taxagent;
\q
```

### Run Initialization Script

```powershell
cd "d:\final year project\tax-fluent-chat"
psql -U taxagent -d tax_filing_db -f backend\init-db.sql
```

### Update .env File

Update the DATABASE_URL in `backend/.env.dev`:

```env
DATABASE_URL=postgresql://taxagent:taxagent_secure_password_2024@localhost:5432/tax_filing_db
```

---

## Option 3: Quick Test with SQLite (Development Only)

If you want to test quickly without PostgreSQL:

1. Update `backend/app/database.py`:

```python
# For SQLite (development/testing only)
DATABASE_URL = "sqlite:///./tax_filing.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

2. Install SQLite support:

```powershell
pip install aiosqlite
```

**Note:** SQLite is NOT recommended for production. Use PostgreSQL for production deployment.

---

## Verify Installation

Run the test script to verify database connection:

```powershell
cd "d:\final year project\tax-fluent-chat\backend"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python test_db_connection.py
```

You should see: ✅ Database connection successful!

---

## Common Issues

### Issue: Port 5432 already in use
**Solution:** Stop existing PostgreSQL service or change port in docker-compose.yml

### Issue: Cannot connect to database
**Solution:** 
1. Verify PostgreSQL is running: `docker ps` or check Windows Services
2. Check firewall settings
3. Verify credentials in .env file

### Issue: Permission denied
**Solution:** Ensure user has proper privileges:
```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO taxagent;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tax_data TO taxagent;
```

---

## Next Steps

After PostgreSQL is running:

1. Install Python dependencies: `pip install -r requirements.txt`
2. Run database migrations: `alembic upgrade head`
3. Start the FastAPI backend: `uvicorn app.main:app --reload`
4. Access API docs: http://localhost:8000/docs
