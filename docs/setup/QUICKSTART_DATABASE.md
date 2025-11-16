# 🚀 Quick Start: Install PostgreSQL & Connect Database

## 🎯 Choose Your Method

### ⭐ Method 1: Automated Setup (Easiest)

**Double-click this file:**
```
setup-postgresql.bat
```

The script will:
- ✅ Check if PostgreSQL is installed
- ✅ Guide you through installation if needed
- ✅ Create database and user automatically
- ✅ Enable required extensions
- ✅ Test the connection

**If Chocolatey installation is selected, RIGHT-CLICK and "Run as Administrator"**

---

### 🔧 Method 2: Manual PowerShell

**Run PowerShell as Administrator:**

```powershell
cd "d:\final year project\tax-fluent-chat"
.\setup-postgresql.ps1
```

---

### 📥 Method 3: Manual Download

1. **Download PostgreSQL 15**
   - Visit: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Download Windows x86-64 version

2. **Install with these settings:**
   - Password: `taxagent_secure_password_2024`
   - Port: `5432`
   - Select all components (PostgreSQL Server, pgAdmin 4, Command Line Tools)

3. **After installation, run setup script:**
   ```powershell
   .\setup-postgresql.bat
   ```

---

## ✅ Verify Installation

Once installed, test the connection:

```powershell
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test database connection
python test_db_connection.py
```

**Expected Output:**
```
✅ Database connection successful!
📊 PostgreSQL Version: PostgreSQL 15.x
```

---

## 📋 Database Credentials

```
Host:     localhost
Port:     5432
Database: tax_filing_db
Username: taxagent
Password: taxagent_secure_password_2024
```

---

## 🆘 Troubleshooting

### PowerShell Execution Policy Error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PostgreSQL Not in PATH

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"
```

### Service Not Running

```powershell
Get-Service postgresql-x64-15
Start-Service postgresql-x64-15
```

---

## 📖 Detailed Documentation

- **Complete guide**: `POSTGRESQL_INSTALLATION_WINDOWS.md`
- **Database setup**: `POSTGRESQL_SETUP.md`
- **Project progress**: `IMPLEMENTATION_PROGRESS.md`

---

## 🎯 Next Steps After PostgreSQL is Running

1. **Test connection**: `python backend\test_db_connection.py`
2. **Continue implementation**: Backend API endpoints
3. **Start development**: `uvicorn app.main:app --reload`
