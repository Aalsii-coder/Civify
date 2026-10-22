D@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating the local Python environment...
    py -m venv .venv
    if errorlevel 1 (
        echo Could not create the environment. Check that Python is installed.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py
pause
