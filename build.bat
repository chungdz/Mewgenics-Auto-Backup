@echo off
REM Run on Windows in the project root to build MewgenicsBackup.exe
pip install pyinstaller
pyinstaller --onefile --windowed --name "MewgenicsBackup" src/mewgenics_backup_gui.py
echo.
echo Done. Executable: dist\MewgenicsBackup.exe
pause
