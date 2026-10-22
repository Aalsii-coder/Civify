@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run run_civify.bat first to create the Python environment.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" test_matching.py
".venv\Scripts\python.exe" evaluate.py
pause
