# PostgreSQL Installation & Setup Guide for Windows

## 🚀 Quick Installation Steps

### Method 1: Using Chocolatey (Easiest - Requires Admin)

**Run PowerShell as Administrator**, then execute:

```powershell
# Install PostgreSQL 15
choco install postgresql15 --params '/Password:taxagent_secure_password_2024' -y

# Refresh environment variables
refreshenv

# Verify installation
psql --version
```

---

### Method 2: Manual Download & Install (No Admin Rights Issues)

1. **Download PostgreSQL**
   - Visit: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Download: PostgreSQL 15.x for Windows x86-64
   - File size: ~350 MB

2. **Run the Installer**
   - Double-click the downloaded `.exe` file
   - Click "Next" through the welcome screen
   
3. **Installation Settings**
   - **Installation Directory**: `C:\Program Files\PostgreSQL\15` (default is fine)
   - **Components**: Select all (PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools)
   - **Data Directory**: `C:\Program Files\PostgreSQL\15\data` (default is fine)
   - **Password**: `taxagent_secure_password_2024` (⚠️ IMPORTANT: Remember this!)
   - **Port**: `5432` (default)
   - **Locale**: Default locale

4. **Complete Installation**
   - Click "Next" > "Next" > "Finish"
   - Uncheck "Launch Stack Builder" (not needed now)

5. **Verify Installation**
   ```powershell
   # Add to PATH if not already added
   $env:Path += ";C:\Program Files\PostgreSQL\15\bin"
   
   # Check version
   psql --version
   ```

---

## 📋 Post-Installation Setup

### Step 1: Create Database and User

**Option A: Using pgAdmin 4 (GUI)**

1. Open **pgAdmin 4** from Start Menu
2. Enter master password when prompted
3. Right-click "Databases" > "Create" > "Database"
   - Database: `tax_filing_db`
   - Owner: `postgres`
4. Open Query Tool (Tools > Query Tool)
5. Run this SQL:

```sql
-- Create user
CREATE USER taxagent WITH PASSWORD 'taxagent_secure_password_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tax_filing_db TO taxagent;

-- Connect to the database
\c tax_filing_db

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO taxagent;
ALTER DATABASE tax_filing_db OWNER TO taxagent;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

**Option B: Using Command Line (psql)**

```powershell
# Open PowerShell and run:
cd "d:\final year project\tax-fluent-chat"

# Connect as postgres superuser (password: taxagent_secure_password_2024)
psql -U postgres

# In psql, run:
CREATE DATABASE tax_filing_db;
CREATE USER taxagent WITH PASSWORD 'taxagent_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE tax_filing_db TO taxagent;
ALTER DATABASE tax_filing_db OWNER TO taxagent;
\c tax_filing_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
GRANT ALL PRIVILEGES ON SCHEMA public TO taxagent;
\q
```

### Step 2: Run Database Initialization Script

```powershell
cd "d:\final year project\tax-fluent-chat"
psql -U taxagent -d tax_filing_db -f backend\init-db.sql
```

If prompted for password, enter: `taxagent_secure_password_2024`

---

## 🔧 Configure the Project

### Update Environment Variables

The `.env.dev` file is already configured, but verify it matches your setup:

```env
DATABASE_URL=postgresql://taxagent:taxagent_secure_password_2024@localhost:5432/tax_filing_db
```

### Install Python Dependencies

```powershell
cd "d:\final year project\tax-fluent-chat\backend"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Test Database Connection

```powershell
# Make sure you're in backend directory and venv is activated
python test_db_connection.py
```

**Expected Output:**
```
============================================================
🔍 Testing Database Connection
============================================================

📍 Database URL: localhost:5432/tax_filing_db
⏳ Creating database engine...
⏳ Testing connection...

✅ Database connection successful!
📊 PostgreSQL Version: PostgreSQL 15.x
📂 Available schemas: public
🔧 Installed extensions: uuid-ossp, pgcrypto

============================================================
✅ All database checks passed!
============================================================
```

---

## 🛠️ Troubleshooting

### Issue: "psql: command not found"

**Solution**: Add PostgreSQL to PATH

```powershell
# Temporary (current session only)
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"

# Permanent
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\PostgreSQL\15\bin", "User")
```

### Issue: "password authentication failed"

**Solution**: 
1. Check password is correct: `taxagent_secure_password_2024`
2. Verify user exists: `psql -U postgres -c "\du"`
3. Reset password if needed:
   ```sql
   ALTER USER taxagent WITH PASSWORD 'taxagent_secure_password_2024';
   ```

### Issue: "database does not exist"

**Solution**: Create it manually
```powershell
psql -U postgres -c "CREATE DATABASE tax_filing_db OWNER taxagent;"
```

### Issue: "connection refused"

**Solution**: Start PostgreSQL service
```powershell
# Check service status
Get-Service postgresql-x64-15

# Start service if stopped
Start-Service postgresql-x64-15
```

### Issue: Port 5432 already in use

**Solution**: 
1. Find what's using the port: `netstat -ano | findstr :5432`
2. Either stop that service or use a different port in `.env.dev`

---

## ✅ Verification Checklist

After installation, verify these steps:

- [ ] PostgreSQL service is running
- [ ] `psql --version` shows version 15.x
- [ ] Database `tax_filing_db` exists
- [ ] User `taxagent` exists with correct password
- [ ] Extensions `uuid-ossp` and `pgcrypto` are enabled
- [ ] Python test script runs successfully
- [ ] Can connect via pgAdmin 4

---

## 🎯 Next Steps

Once PostgreSQL is installed and tested:

1. **Create database tables**:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   python test_db_connection.py
   ```

2. **Start the FastAPI backend**:
   ```powershell
   uvicorn app.main:app --reload
   ```

3. **Access API documentation**:
   - Open browser: http://localhost:8000/docs

---

## 📞 Quick Reference

**Database Credentials:**
- Host: `localhost`
- Port: `5432`
- Database: `tax_filing_db`
- Username: `taxagent`
- Password: `taxagent_secure_password_2024`

**PostgreSQL Commands:**
```powershell
# Connect to database
psql -U taxagent -d tax_filing_db

# List databases
psql -U taxagent -l

# Execute SQL file
psql -U taxagent -d tax_filing_db -f script.sql

# Backup database
pg_dump -U taxagent tax_filing_db > backup.sql

# Restore database
psql -U taxagent -d tax_filing_db < backup.sql
```

**Service Management:**
```powershell
# Check status
Get-Service postgresql-x64-15

# Start service
Start-Service postgresql-x64-15

# Stop service
Stop-Service postgresql-x64-15

# Restart service
Restart-Service postgresql-x64-15
```
