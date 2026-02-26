@echo off
REM Run on Windows in the project root to build MewgenicsBackup.exe
cd /d "%~dp0"

pip install pyinstaller

REM Require icons/app.ico (assumed always in repo)
set "ICON_PATH=%~dp0icons\app.ico"
if not exist "%ICON_PATH%" (
  echo.
  echo ERROR: icons\app.ico not found. Add it to the repo and run build.bat again.
  pause
  exit /b 1
)

REM Remove old exe so PyInstaller can overwrite
if exist "dist\MewgenicsBackup.exe" (
  del "dist\MewgenicsBackup.exe" 2>nul
  if exist "dist\MewgenicsBackup.exe" (
    echo.
    echo ERROR: dist\MewgenicsBackup.exe is in use. Close it and run build.bat again.
    pause
    exit /b 1
  )
)

REM Remove old spec so PyInstaller regenerates it with the icon
if exist "MewgenicsBackup.spec" del "MewgenicsBackup.spec"

python -m PyInstaller --onefile --windowed --name "MewgenicsBackup" --icon="%ICON_PATH%" --add-data "%ICON_PATH%;icons" --clean src/mewgenics_backup_gui.py
echo.
if exist "dist\MewgenicsBackup.exe" (
  echo Done. Executable: dist\MewgenicsBackup.exe
  echo.
  echo If icon still looks wrong: Windows caches icons. Try renaming the exe or restart File Explorer.
) else (
  echo Build may have failed. Check messages above.
)
pause
