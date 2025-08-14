@echo off
setlocal

REM Check if the virtual environment already exists
IF EXIST "env_realtimetts\Scripts\activate.bat" (
    echo Virtual environment found. Activating...
    call env_realtimetts\Scripts\activate.bat
    goto :install_and_run
)

REM If venv doesn't exist, try to create it with the available python
echo Virtual environment not found. Attempting to create it...
python -m venv env_realtimetts
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to create a Python virtual environment.
    echo Please ensure Python is correctly installed and added to your PATH.
    echo You can download it from https://www.python.org/downloads/
    echo.
    goto :end
)

echo Virtual environment created successfully. Activating...
call env_realtimetts\Scripts\activate.bat

:install_and_run
echo Installing dependencies from requirements.txt...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    goto :end
)

echo Starting the server...
python app.py

:end
pause
