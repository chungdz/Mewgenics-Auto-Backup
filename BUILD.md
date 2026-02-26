# Build Windows executable

You can build the Windows `.exe` **on Linux** (using Docker) or **on Windows** (using Python + PyInstaller).

---

## Option A: Build on Linux (for use on Windows)

Requires **Docker**. From the project root:

```bash
./build.sh
```

This uses the `cdrx/pyinstaller-windows` image (Wine + PyInstaller inside Docker) to produce a Windows executable. Output:

- `dist/MewgenicsBackup.exe` (and possibly `dist/windows/MewgenicsBackup.exe`)

Copy the `.exe` to a Windows machine and run it. No Python needed on Windows.

If you don’t have Docker: `sudo apt install docker.io` (or your distro’s package), add your user to the `docker` group, then run `./build.sh` again.

---

## Option B: Build on Windows

### 1. Install Python on Windows

- Install Python 3.10+ from [python.org](https://www.python.org/downloads/).
- During setup, enable **"Add Python to PATH"**.

### 2. Install PyInstaller

Open **Command Prompt** or **PowerShell** in this project folder and run:

```cmd
pip install pyinstaller
```

Or install from `requirements.txt`:

```cmd
pip install -r requirements.txt
```

### 3. Build the executable

From the project root (folder containing `src/`):

```cmd
pyinstaller --onefile --windowed --name "MewgenicsBackup" src/mewgenics_backup_gui.py
```

Or double‑click **`build.bat`**.

- `--onefile` – single `.exe` file (no folder of dependencies).
- `--windowed` – no console window (GUI only).
- `--name` – output exe name.

Output exe will be at:

```
dist/MewgenicsBackup.exe
```

### 4. Run

Double-click `dist/MewgenicsBackup.exe` or copy it anywhere and run it.

---

## Optional: custom icon

If you have an `.ico` file:

**Windows:**  
`pyinstaller --onefile --windowed --name "MewgenicsBackup" --icon=app.ico src/mewgenics_backup_gui.py`

**Linux (build.sh):** add `--icon=icons/app.ico` to the `pyinstaller` command in `build.sh`.

`build.bat` and `build.sh` require `icons/app.ico` (build fails with an error if it is missing).

### Exe icon not updating?

1. **Rebuild with a clean run** – `build.bat` now deletes `MewgenicsBackup.spec` and uses `--clean` so the icon is embedded again. Run `build.bat` again.
2. **Icon file** – Ensure `icons/app.ico` exists before building (e.g. run `python icons/png_to_ico.py icons/appicon.png icons/app.ico`).
3. **Windows icon cache** – Explorer caches exe icons. Try: rename the exe (e.g. to `MewgenicsBackup_new.exe`), or restart File Explorer (taskbar → right‑click → Exit Explorer, then run `explorer` from Task Manager or Start).

## Optional: hide console when testing

If you run the script with `python src/mewgenics_backup_gui.py` and see a console, that is normal. The built exe with `--windowed` will not show a console.
