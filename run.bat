@echo off
setlocal
cd /d "%~dp0"

set "VENV_ACTIVATE=%~dp0venv\Scripts\activate.bat"

if exist "%VENV_ACTIVATE%" (
    call "%VENV_ACTIVATE%"
) else (
    echo [WARNING] venv not found at %VENV_ACTIVATE%, attempting system python...
)

python run.py