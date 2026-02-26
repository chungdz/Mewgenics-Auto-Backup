"""
Mewgenics Backup - Windows GUI
- Select a file to backup (and create backups on demand or watch for changes)
- Select a backup file to restore (overwrite a target file)
"""
import os
import shutil
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk


# Default backup subfolder name next to the source file
BACKUP_SUBDIR = "backup_history"


def _default_backup_dir() -> str:
    """Default backup history folder (Mewgenics-style path)."""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(appdata, "Glaiel Games", "Mewgenics", BACKUP_SUBDIR)
    return os.path.join(os.path.expanduser("~"), ".local", "share", "Glaiel Games", "Mewgenics", BACKUP_SUBDIR)


def get_file_signature(path: str):
    """Return (mtime_ns, size) for change detection."""
    st = os.stat(path)
    return (st.st_mtime_ns, st.st_size)


def backup_file(source_path: str, backup_dir: str) -> str | None:
    """Create a timestamped backup of source_path in backup_dir. Returns path of new backup or None."""
    if not os.path.isfile(source_path):
        return None
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(source_path))[0]
    ext = os.path.splitext(source_path)[1] or ".sav"
    dest_path = os.path.join(backup_dir, f"{base}_{timestamp}{ext}")
    shutil.copy(source_path, dest_path)
    return dest_path


def restore_file(backup_path: str, target_path: str) -> bool:
    """Overwrite target_path with backup_path. Returns True on success."""
    if not os.path.isfile(backup_path):
        return False
    shutil.copy(backup_path, target_path)
    return True


class BackupApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mewgenics Backup")
        self.root.minsize(480, 380)
        self.root.geometry("560x420")

        # Window/taskbar icon: use app.ico (from repo when running as script, from bundle when frozen)
        if getattr(sys, "frozen", False):
            _base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            _icon_path = os.path.join(_base, "icons", "app.ico")
        else:
            _script_dir = os.path.dirname(os.path.abspath(__file__))
            _icon_path = os.path.abspath(os.path.join(_script_dir, "..", "icons", "app.ico"))
        if os.path.isfile(_icon_path):
            try:
                self.root.iconbitmap(_icon_path)
            except Exception:
                pass

        self.source_path = tk.StringVar()
        self.backup_dir = tk.StringVar()
        self.backup_file_path = tk.StringVar()
        self.restore_target_path = tk.StringVar()
        self.watching = False
        self.watch_thread: threading.Thread | None = None
        self.stop_watch = threading.Event()

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}
        # ---- Section: File to backup ----
        f_backup = ttk.LabelFrame(self.root, text="1. File to backup", padding=8)
        f_backup.pack(fill=tk.X, **pad)

        row1 = tk.Frame(f_backup)
        row1.pack(fill=tk.X)
        ttk.Entry(row1, textvariable=self.source_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(row1, text="Browse...", command=self._browse_source).pack(side=tk.RIGHT)

        row2 = tk.Frame(f_backup)
        row2.pack(fill=tk.X)
        ttk.Label(row2, text="Backup folder:").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(row2, textvariable=self.backup_dir, width=45).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(row2, text="Browse...", command=self._browse_backup_dir).pack(side=tk.RIGHT)

        row3 = tk.Frame(f_backup)
        row3.pack(fill=tk.X)
        self.btn_backup_now = ttk.Button(row3, text="Backup now", command=self._backup_now)
        self.btn_backup_now.pack(side=tk.LEFT, padx=(0, 8))
        self.watch_var = tk.BooleanVar(value=True)
        self.cb_watch = ttk.Checkbutton(row3, text="Watch for changes (backup automatically)", variable=self.watch_var, command=self._toggle_watch)
        self.cb_watch.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row3, text="Clean up", command=self._cleanup_backup_folder).pack(side=tk.LEFT)

        # ---- Section: Restore from backup ----
        f_restore = ttk.LabelFrame(self.root, text="2. Restore: overwrite target with a backup", padding=8)
        f_restore.pack(fill=tk.X, **pad)

        row4 = tk.Frame(f_restore)
        row4.pack(fill=tk.X)
        ttk.Label(row4, text="Backup file:").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(row4, textvariable=self.backup_file_path, width=45).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(row4, text="Browse...", command=self._browse_backup_file).pack(side=tk.RIGHT)

        row5 = tk.Frame(f_restore)
        row5.pack(fill=tk.X)
        ttk.Label(row5, text="Target file (to overwrite):").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(row5, textvariable=self.restore_target_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(row5, text="Browse...", command=self._browse_restore_target).pack(side=tk.RIGHT)

        ttk.Button(f_restore, text="Restore (overwrite target with backup)", command=self._restore).pack(anchor=tk.W)

        # ---- Log: each backup printed here ----
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=4)
        log_frame.pack(fill=tk.BOTH, expand=True, **pad)
        self.log_text = tk.Text(log_frame, height=5, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ---- Status ----
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(self.root, textvariable=self.status, foreground="gray").pack(anchor=tk.W, **pad)

        # When source changes, suggest backup dir and default restore target
        self.source_path.trace_add("write", self._on_source_changed)

    def _on_source_changed(self, *_):
        p = self.source_path.get().strip()
        if not p:
            return
        d = os.path.dirname(p)
        if d:
            suggested = os.path.join(d, BACKUP_SUBDIR)
            if not self.backup_dir.get().strip():
                self.backup_dir.set(suggested)
        # Default restore target = same file we back up
        self.restore_target_path.set(p)
        # If watch is on by default, start watching once we have source and backup dir
        if self.watch_var.get() and not self.watching:
            self._toggle_watch()

    def _browse_source(self):
        path = filedialog.askopenfilename(
            title="Select file to backup",
            filetypes=[("Save files", "*.sav"), ("All files", "*.*")],
        )
        if path:
            self.source_path.set(path)
            self._on_source_changed()

    def _browse_backup_dir(self):
        path = filedialog.askdirectory(title="Select backup folder")
        if path:
            self.backup_dir.set(path)

    def _cleanup_backup_folder(self):
        """Delete all files in the current backup folder."""
        bdir = self.backup_dir.get().strip()
        if not bdir:
            messagebox.showwarning("Clean up", "Please set the backup folder first.")
            return
        if not os.path.isdir(bdir):
            messagebox.showerror("Clean up", f"Folder not found:\n{bdir}")
            return
        try:
            names = os.listdir(bdir)
            files = [os.path.join(bdir, n) for n in names if os.path.isfile(os.path.join(bdir, n))]
            if not files:
                self.status.set("Backup folder is already empty.")
                self._log("Clean up: backup folder already empty.")
                return
            if not messagebox.askyesno("Clean up", f"Delete all {len(files)} file(s) in backup folder?\n\n{bdir}\n\nThis cannot be undone."):
                return
            for p in files:
                os.remove(p)
            self.status.set(f"Cleaned up {len(files)} file(s) in backup folder.")
            self._log(f"Clean up: removed {len(files)} file(s) from {bdir}")
        except OSError as e:
            messagebox.showerror("Clean up", str(e))

    def _backup_now(self):
        src = self.source_path.get().strip()
        bdir = self.backup_dir.get().strip()
        if not src:
            messagebox.showwarning("Backup", "Please select a file to backup.")
            return
        if not bdir:
            bdir = os.path.join(os.path.dirname(src), BACKUP_SUBDIR)
            self.backup_dir.set(bdir)
        if not os.path.isfile(src):
            messagebox.showerror("Backup", f"Source file not found:\n{src}")
            return
        out = backup_file(src, bdir)
        if out:
            self.status.set(f"Backup created: {os.path.basename(out)}")
            self._log(f"Backup created: {out}")
        else:
            messagebox.showerror("Backup", "Failed to create backup.")

    def _watch_loop(self):
        src = self.source_path.get().strip()
        bdir = self.backup_dir.get().strip()
        if not src or not bdir or not os.path.isfile(src):
            self.root.after(0, lambda: self._set_watch_ui(False))
            return
        last_sig = get_file_signature(src)
        while not self.stop_watch.is_set():
            time.sleep(2)
            if self.stop_watch.is_set():
                break
            try:
                if not os.path.isfile(src):
                    continue
                sig = get_file_signature(src)
                if sig != last_sig:
                    last_sig = sig
                    new_backup = backup_file(src, bdir)
                    if new_backup:
                        self.root.after(0, lambda n=new_backup: self.status.set(f"Auto-backup: {os.path.basename(n)}"))
                        self.root.after(0, lambda n=new_backup: self._log(f"Auto-backup: {n}"))
            except Exception:
                pass
        self.root.after(0, lambda: self._set_watch_ui(False))

    def _set_watch_ui(self, on: bool):
        self.watching = on
        self.watch_var.set(on)
        if on:
            self.status.set("Watching for changes...")
        else:
            self.status.set("Stopped watching.")

    def _toggle_watch(self):
        if self.watch_var.get():
            src = self.source_path.get().strip()
            bdir = self.backup_dir.get().strip()
            if not src:
                messagebox.showwarning("Watch", "Please select a file to backup first.")
                self.watch_var.set(False)
                return
            if not bdir:
                bdir = os.path.join(os.path.dirname(src), BACKUP_SUBDIR)
                self.backup_dir.set(bdir)
            self.stop_watch.clear()
            self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
            self.watch_thread.start()
            self._set_watch_ui(True)
        else:
            self.stop_watch.set()
            self._set_watch_ui(False)

    def _browse_backup_file(self):
        path = filedialog.askopenfilename(
            title="Select backup file to restore from",
            filetypes=[("Save/backup files", "*.sav *.bak"), ("All files", "*.*")],
        )
        if path:
            self.backup_file_path.set(path)
            # Suggest restore target as same name in parent of backup dir
            bdir = os.path.dirname(path)
            if not self.restore_target_path.get().strip():
                # Default: overwrite a file with same base name in parent of backup dir
                parent = os.path.dirname(bdir)
                base = os.path.basename(path)
                # If backup is like "steamcampaign01_20250101_120000.sav", target might be "steamcampaign01.sav"
                if "_" in base and base.endswith(".sav"):
                    possible = base.rsplit("_", 2)[0] + ".sav"
                    target = os.path.join(parent, possible)
                    if os.path.isfile(target):
                        self.restore_target_path.set(target)

    def _browse_restore_target(self):
        path = filedialog.askopenfilename(
            title="Select target file to overwrite",
            filetypes=[("Save files", "*.sav"), ("All files", "*.*")],
        )
        if path:
            self.restore_target_path.set(path)

    def _restore(self):
        backup = self.backup_file_path.get().strip()
        target = self.restore_target_path.get().strip()
        if not backup:
            messagebox.showwarning("Restore", "Please select a backup file.")
            return
        if not target:
            messagebox.showwarning("Restore", "Please select the target file to overwrite.")
            return
        if not os.path.isfile(backup):
            messagebox.showerror("Restore", f"Backup file not found:\n{backup}")
            return
        if restore_file(backup, target):
            self.status.set(f"Restored: {target}")
            self._log(f"Restored -> {target}")
        else:
            messagebox.showerror("Restore", "Restore failed.")

    def _log(self, msg: str):
        """Append a line to the log panel."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()
        self.stop_watch.set()


def main():
    app = BackupApp()
    app.run()


if __name__ == "__main__":
    main()
