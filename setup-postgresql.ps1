# PostgreSQL Automated Setup Script for Tax Filing AI Agent
# This script guides you through setting up PostgreSQL

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Setup for Tax Filing AI Agent" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some operations may fail without admin rights" -ForegroundColor Yellow
    Write-Host ""
}

# Function to test if PostgreSQL is installed
function Test-PostgreSQL {
    try {
        $version = psql --version 2>$null
        if ($version) {
            Write-Host "✅ PostgreSQL is installed: $version" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ PostgreSQL is not installed" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to test database connection
function Test-DatabaseConnection {
    param (
        [string]$Database = "tax_filing_db",
        [string]$Username = "taxagent",
        [string]$Password = "taxagent_secure_password_2024"
    )
    
    $env:PGPASSWORD = $Password
    try {
        $result = psql -U $Username -d $Database -c "SELECT version();" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully connected to database '$Database'" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ Failed to connect to database '$Database'" -ForegroundColor Red
        return $false
    }
    finally {
        $env:PGPASSWORD = $null
    }
    return $false
}

# Step 1: Check PostgreSQL Installation
Write-Host "Step 1: Checking PostgreSQL Installation..." -ForegroundColor Cyan
Write-Host ""

$pgInstalled = Test-PostgreSQL

if (-not $pgInstalled) {
    Write-Host ""
    Write-Host "PostgreSQL is not installed. Choose installation method:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Install using Chocolatey (requires admin rights)" -ForegroundColor White
    Write-Host "2. Manual download from postgresql.org" -ForegroundColor White
    Write-Host "3. Skip installation (I'll install it myself)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-3)"
    
    switch ($choice) {
        "1" {
            if (-not $isAdmin) {
                Write-Host ""
                Write-Host "❌ Admin rights required for Chocolatey installation" -ForegroundColor Red
                Write-Host "   Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
                Write-Host ""
                Read-Host "Press Enter to exit"
                exit 1
            }
            
            Write-Host ""
            Write-Host "Installing PostgreSQL via Chocolatey..." -ForegroundColor Cyan
            choco install postgresql15 --params '/Password:taxagent_secure_password_2024' -y
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ PostgreSQL installed successfully" -ForegroundColor Green
                refreshenv
            }
            else {
                Write-Host "❌ Installation failed" -ForegroundColor Red
                Write-Host "   Please try manual installation instead" -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
        "2" {
            Write-Host ""
            Write-Host "Opening download page in browser..." -ForegroundColor Cyan
            Start-Process "https://www.enterprisedb.com/downloads/postgres-postgresql-downloads"
            Write-Host ""
            Write-Host "📖 Please follow these steps:" -ForegroundColor Yellow
            Write-Host "   1. Download PostgreSQL 15.x for Windows" -ForegroundColor White
            Write-Host "   2. Run the installer" -ForegroundColor White
            Write-Host "   3. Set password: taxagent_secure_password_2024" -ForegroundColor White
            Write-Host "   4. Use default port: 5432" -ForegroundColor White
            Write-Host "   5. Complete installation" -ForegroundColor White
            Write-Host ""
            Write-Host "📄 Detailed instructions: POSTGRESQL_INSTALLATION_WINDOWS.md" -ForegroundColor Cyan
            Write-Host ""
            Read-Host "Press Enter after installation is complete"
            
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            
            # Check if installed now
            if (-not (Test-PostgreSQL)) {
                Write-Host "❌ PostgreSQL not detected after installation" -ForegroundColor Red
                Write-Host "   You may need to restart PowerShell" -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
        "3" {
            Write-Host ""
            Write-Host "⚠️  Please install PostgreSQL manually, then run this script again" -ForegroundColor Yellow
            Write-Host "   See: POSTGRESQL_INSTALLATION_WINDOWS.md for instructions" -ForegroundColor Cyan
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 0
        }
        default {
            Write-Host "Invalid choice. Exiting." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 2: Check PostgreSQL Service
Write-Host "Step 2: Checking PostgreSQL Service..." -ForegroundColor Cyan
Write-Host ""

$service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($service) {
    if ($service.Status -eq "Running") {
        Write-Host "✅ PostgreSQL service is running" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  PostgreSQL service is stopped. Starting..." -ForegroundColor Yellow
        Start-Service $service.Name
        Write-Host "✅ PostgreSQL service started" -ForegroundColor Green
    }
}
else {
    Write-Host "⚠️  PostgreSQL service not found" -ForegroundColor Yellow
    Write-Host "   It may be running as a different service name" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 3: Create Database and User
Write-Host "Step 3: Setting up Database..." -ForegroundColor Cyan
Write-Host ""

$postgresPassword = Read-Host "Enter PostgreSQL 'postgres' user password" -AsSecureString
$postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))

# Test postgres connection
$env:PGPASSWORD = $postgresPasswordPlain
$testConnection = psql -U postgres -c "SELECT 1;" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to connect with postgres user" -ForegroundColor Red
    Write-Host "   Please verify the password is correct" -ForegroundColor Yellow
    $env:PGPASSWORD = $null
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Connected as postgres user" -ForegroundColor Green
Write-Host ""

# Create database and user
Write-Host "Creating database and user..." -ForegroundColor Cyan

$setupSQL = @"
-- Create database
CREATE DATABASE tax_filing_db;

-- Create user
CREATE USER taxagent WITH PASSWORD 'taxagent_secure_password_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tax_filing_db TO taxagent;
ALTER DATABASE tax_filing_db OWNER TO taxagent;
"@

$setupSQL | psql -U postgres 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database and user created successfully" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Database/user may already exist (this is OK)" -ForegroundColor Yellow
}

# Enable extensions
Write-Host "Enabling extensions..." -ForegroundColor Cyan

$extensionSQL = @"
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
GRANT ALL PRIVILEGES ON SCHEMA public TO taxagent;
"@

$extensionSQL | psql -U postgres -d tax_filing_db 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Extensions enabled successfully" -ForegroundColor Green
}

$env:PGPASSWORD = $null

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 4: Test Connection
Write-Host "Step 4: Testing Database Connection..." -ForegroundColor Cyan
Write-Host ""

if (Test-DatabaseConnection) {
    Write-Host ""
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host "  🎉 PostgreSQL Setup Complete!" -ForegroundColor Green
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Database Credentials:" -ForegroundColor Cyan
    Write-Host "  Host:     localhost" -ForegroundColor White
    Write-Host "  Port:     5432" -ForegroundColor White
    Write-Host "  Database: tax_filing_db" -ForegroundColor White
    Write-Host "  Username: taxagent" -ForegroundColor White
    Write-Host "  Password: taxagent_secure_password_2024" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test database connection:" -ForegroundColor White
    Write-Host "     cd backend" -ForegroundColor Gray
    Write-Host "     python test_db_connection.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Start the FastAPI backend:" -ForegroundColor White
    Write-Host "     uvicorn app.main:app --reload" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Access pgAdmin 4 from Start Menu to manage database" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host "❌ Database connection test failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Verify PostgreSQL service is running" -ForegroundColor White
    Write-Host "  2. Check credentials are correct" -ForegroundColor White
    Write-Host "  3. See: POSTGRESQL_INSTALLATION_WINDOWS.md" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Read-Host "Press Enter to exit"
