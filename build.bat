@echo off
REM Run on Windows in the project root to build MewgenicsBackup.exe
pip install pyinstaller

REM Remove old exe so PyInstaller can overwrite (avoid "Access denied" if exe is running)
if exist "dist\MewgenicsBackup.exe" (
  del "dist\MewgenicsBackup.exe" 2>nul
  if exist "dist\MewgenicsBackup.exe" (
    echo.
    echo ERROR: dist\MewgenicsBackup.exe is in use. Close it and run build.bat again.
    pause
    exit /b 1
  )
)

python -m PyInstaller --onefile --windowed --name "MewgenicsBackup" --icon=icons\app.ico src/mewgenics_backup_gui.py
echo.
if exist "dist\MewgenicsBackup.exe" (
  echo Done. Executable: dist\MewgenicsBackup.exe
) else (
  echo Build may have failed. Check messages above.
)
pause
