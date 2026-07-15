@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [StockPilot] Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

python run.py
if errorlevel 1 goto :error

echo.
echo [StockPilot] Completed.
pause
exit /b 0

:error
echo.
echo [StockPilot] Execution failed.
pause
exit /b 1
