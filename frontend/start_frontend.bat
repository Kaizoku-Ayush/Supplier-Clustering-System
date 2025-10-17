@echo off
REM SupplierIQ Frontend Server Launcher
REM ====================================

echo.
echo ========================================
echo  SupplierIQ Frontend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Starting frontend server on http://localhost:8000...
echo.
echo Available pages:
echo   - Login:           http://localhost:8000/login.html
echo   - Register:        http://localhost:8000/register.html
echo   - Dashboard:       http://localhost:8000/pages/dashboard.html
echo   - Transactions:    http://localhost:8000/pages/transactions.html
echo   - Upload:          http://localhost:8000/pages/upload.html
echo   - Recommendations: http://localhost:8000/pages/recommendations.html
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start Python HTTP server
cd /d "%~dp0"
python -m http.server 8000

pause
