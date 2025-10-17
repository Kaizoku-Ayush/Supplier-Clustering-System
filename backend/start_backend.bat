@echo off
REM SupplierIQ Backend Server Launcher
REM ===================================

echo.
echo ========================================
echo  SupplierIQ Backend Server
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

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing backend dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting backend server on http://localhost:5000...
echo.
echo API Endpoints:
echo   - Auth:            http://localhost:5000/api/auth
echo   - Companies:       http://localhost:5000/api/companies
echo   - Transactions:    http://localhost:5000/api/transactions
echo   - Recommendations: http://localhost:5000/api/recommendations
echo   - Upload:          http://localhost:5000/api/upload
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start Flask server
cd /d "%~dp0src"
python app.py

pause
