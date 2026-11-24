@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv
) else (
  python -m venv .venv
)
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -c "from PIL import Image, ImageTk; import tkinter"
if errorlevel 1 goto fail
".venv\Scripts\python.exe" verify_assets.py
if errorlevel 1 goto fail
echo Installation complete. Open LAUNCH.bat.
pause
exit /b 0
:fail
echo Setup failed. Read START_HERE.txt and review the error above.
pause
exit /b 1
