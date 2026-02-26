@echo off
REM Run on Windows in the project root to build MewgenicsBackup.exe
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "MewgenicsBackup" src/mewgenics_backup_gui.py
echo.
if exist "dist\MewgenicsBackup.exe" (
  echo Done. Executable: dist\MewgenicsBackup.exe
) else (
  echo Build may have failed. Check messages above.
)
pause
