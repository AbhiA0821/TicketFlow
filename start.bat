@echo off
setlocal

title TicketFlow - AI Support Ticket Triage

REM 1. Set working directory to the directory containing start.bat
cd /d "%~dp0"
set "APP_DIR=%~dp0"

echo ============================================================
echo   TicketFlow - NLP-Based Support Ticket Classification
echo ============================================================
echo(

REM 2. Check that app.py exists
if not exist "%APP_DIR%app.py" (
    echo [ERROR] app.py was not found in:
    echo         %APP_DIR%
    echo Please make sure start.bat is located in the TicketFlow root folder.
    echo(
    pause
    exit /b 1
)

REM 3. Check model artifacts
if not exist "%APP_DIR%model.pkl" (
    echo [ERROR] Trained model artifact model.pkl is missing.
    echo         Please train the model first by running: python train_model.py
    echo(
    pause
    exit /b 1
)

if not exist "%APP_DIR%tfidf_vectorizer.pkl" (
    echo [ERROR] TF-IDF Vectorizer artifact tfidf_vectorizer.pkl is missing.
    echo         Please train the model first by running: python train_model.py
    echo(
    pause
    exit /b 1
)

REM 4. Detect and activate virtual environment if present
if exist "%APP_DIR%.venv\Scripts\activate.bat" (
    echo [*] Activating local virtual environment .venv...
    call "%APP_DIR%.venv\Scripts\activate.bat"
)
if exist "%APP_DIR%venv\Scripts\activate.bat" (
    echo [*] Activating local virtual environment venv...
    call "%APP_DIR%venv\Scripts\activate.bat"
)

REM 5. Check Python availability
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not configured in your system PATH.
    echo         Please install Python 3.9+ and try again.
    echo(
    pause
    exit /b 1
)

REM 6. Check Streamlit availability
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Streamlit is not installed in the active Python environment.
    echo         Please install the required packages:
    echo         pip install -r requirements.txt
    echo(
    pause
    exit /b 1
)

REM 7. Check if port 8501 is already in use
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$conn = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1;" ^
  "if ($conn) { exit 10 } else { exit 0 }"

if %ERRORLEVEL% equ 10 (
    echo [*] TicketFlow is ALREADY running on port 8501.
    echo(
    echo     Application URL: http://127.0.0.1:8501
    echo(
    echo     Opening your default browser to the running instance...
    start "" "http://127.0.0.1:8501"
    echo     To stop or restart the application, run stop.bat first.
    echo(
    pause
    exit /b 0
)

REM 8. Launch Application
echo [*] Starting TicketFlow web application on 127.0.0.1:8501...
echo [*] Web URL: http://127.0.0.1:8501
echo [*] Press Ctrl+C in this terminal window to stop the server.
echo(

REM Launch browser in background after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start \"\" \"http://127.0.0.1:8501\""

REM Start Streamlit in foreground
streamlit run app.py --server.address 127.0.0.1 --server.port 8501

echo(
echo [*] TicketFlow server has stopped.
pause
