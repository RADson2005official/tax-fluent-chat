@echo off
echo.
echo ====================================================================
echo   PostgreSQL Setup for Tax Filing AI Agent
echo ====================================================================
echo.
echo This script will help you install and configure PostgreSQL.
echo.
echo IMPORTANT: If you need to install PostgreSQL using Chocolatey,
echo            right-click this file and select "Run as Administrator"
echo.
echo Press any key to continue...
pause >nul

powershell -ExecutionPolicy Bypass -File "%~dp0setup-postgresql.ps1"

pause
