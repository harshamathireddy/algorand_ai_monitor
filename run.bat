@echo off
REM Algorand AI Monitor - Startup Script

echo Installing dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting AlgoGuard AI application...
echo.
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

python app.py

pause
