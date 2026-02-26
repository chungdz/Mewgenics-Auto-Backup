# Mewgenics Auto Backup

A small Windows GUI tool to back up and restore save files. It is designed for **Mewgenics** save and load so you can avoid in-game punishment: back up your save before a run, then overwrite the save file when you want to restart. You can also use it for other games.

**Mewgenics save file location:**  
`C:\Users\<user name>\AppData\Roaming\Glaiel Games\Mewgenics\<steam id>\saves\steamcampaign01.sav`

**Typical workflow:** First select that target file (or any save file) to back up. When you want to restart, pick a backup file and overwrite the same target file to restore.

## Features

- **Backup:** Choose any file to back up and the backup folder. Create a timestamped backup on demand or turn on “Watch for changes” to auto-backup when the file changes.
- **Restore:** Pick a backup file and the target file to overwrite, then restore with one click (with confirmation).

## Requirements

- **To run the GUI:** Python 3.x with tkinter (tkinter is included with most Python installs).
- **To build the Windows .exe:** See [BUILD.md](BUILD.md) (PyInstaller on Windows, or Docker on Linux).

## Quick start

### Run with Python (Windows or Linux)

```bash
python src/mewgenics_backup_gui.py
```

### Run the built executable (Windows)

After building, run:

```
dist/MewgenicsBackup.exe
```

No Python needed on the machine.

## Building the Windows .exe

| Platform   | Command / action |
|-----------|-------------------|
| **Linux** | `./build.sh` (requires Docker) |
| **Windows** | Double-click `build.bat` or run the PyInstaller command in [BUILD.md](BUILD.md) |

See **[BUILD.md](BUILD.md)** for full steps (installing Python, PyInstaller, Docker, etc.).

## Project layout

```
├── src/
│   ├── mewgenics_backup_gui.py   # Windows GUI (backup + restore)
│   └── check_and_backup.py       # Original CLI watcher script
├── build.sh                       # Build .exe on Linux (Docker)
├── build.bat                      # Build .exe on Windows
├── BUILD.md                       # Detailed build instructions
├── requirements.txt               # PyInstaller for building (optional to run)
└── LICENSE                        # MIT
```

## License

MIT — see [LICENSE](LICENSE).
