import ctypes
import os
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

# Auto-elevate to Administrator so mklink and icacls always succeed
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

TARGET_DIR = Path(r"C:\HacknetSaves\Hacknet")
USER_PROFILE = Path(os.environ["USERPROFILE"])
DOC_PATHS = [
    USER_PROFILE / "Documents" / "My Games" / "Hacknet",
    USER_PROFILE / "OneDrive" / "Documents" / "My Games" / "Hacknet",
]

class HacknetManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hacknet Save & Bootloader Recovery Tool")
        self.root.geometry("540x420")
        self.root.resizable(False, False)

        # Header
        header = tk.Label(
            root,
            text="Hacknet Save Redirect & Trap Cleaner",
            font=("Segoe UI", 13, "bold"),
            pady=10,
        )
        header.pack()

        subtitle = tk.Label(
            root,
            text="Close Hacknet and Steam before running any action below.",
            font=("Segoe UI", 9),
            fg="#555555",
        )
        subtitle.pack()

        # Buttons Frame
        btn_frame = tk.Frame(root, pady=12)
        btn_frame.pack(fill="x", padx=20)

        self.btn_clean = tk.Button(
            btn_frame,
            text="1. Purge VMBootloaderTrap.dll (Main + Steam Extensions)",
            font=("Segoe UI", 10, "bold"),
            bg="#d9534f",
            fg="white",
            pady=6,
            command=self.clean_traps_only,
        )
        self.btn_clean.pack(fill="x", pady=4)

        self.btn_redirect = tk.Button(
            btn_frame,
            text="2. Redirect Saves to C:\\HacknetSaves (Bypass OneDrive)",
            font=("Segoe UI", 10, "bold"),
            bg="#0275d8",
            fg="white",
            pady=6,
            command=self.redirect_saves,
        )
        self.btn_redirect.pack(fill="x", pady=4)

        self.btn_reverse = tk.Button(
            btn_frame,
            text="3. Reverse / Restore Saves to Default Documents Folder",
            font=("Segoe UI", 10),
            bg="#5cb85c",
            fg="white",
            pady=6,
            command=self.reverse_redirect,
        )
        self.btn_reverse.pack(fill="x", pady=4)

        # Status Log Box
        log_label = tk.Label(root, text="Activity Log:", font=("Segoe UI", 9, "bold"), anchor="w")
        log_label.pack(fill="x", padx=20)

        self.log_box = scrolledtext.ScrolledText(
            root, height=11, font=("Consolas", 9), state="disabled", bg="#1e1e1e", fg="#00ff66"
        )
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(2, 15))

        self.log("Ready. Select an option above.")

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, f"> {message}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")
        self.root.update_idletasks()

    def purge_dlls_in_path(self, base_path):
        removed = 0
        if base_path.exists():
            for trap_file in base_path.rglob("VMBootloaderTrap.dll"):
                self.log(f"Unlocking & deleting: {trap_file}")
                subprocess.run(["icacls", str(trap_file), "/grant", "USERS:F"], check=False)
                trap_file.unlink(missing_ok=True)
                removed += 1
        return removed

    def clean_traps_only(self):
        self.log("Scanning for VMBootloaderTrap.dll across all folders...")
        total_removed = self.purge_dlls_in_path(TARGET_DIR)
        for path in DOC_PATHS:
            if path.exists() and not path.is_symlink():
                total_removed += self.purge_dlls_in_path(path)

        if total_removed > 0:
            self.log(f"Success! Removed {total_removed} trap file(s).")
            messagebox.showinfo("Trap Cleared", f"Deleted {total_removed} VMBootloaderTrap.dll file(s).")
        else:
            self.log("No VMBootloaderTrap.dll files found. Your game is clean.")
            messagebox.showinfo("All Clean", "No VMBootloaderTrap.dll files were found.")

    def redirect_saves(self):
        try:
            self.log("Starting save redirection to C:\\HacknetSaves\\Hacknet...")
            TARGET_DIR.mkdir(parents=True, exist_ok=True)

            for old_path in DOC_PATHS:
                if not old_path.exists() and not old_path.is_symlink():
                    old_path.parent.mkdir(parents=True, exist_ok=True)
                elif old_path.exists() and not old_path.is_symlink():
                    self.purge_dlls_in_path(old_path)
                    self.log(f"Moving files from {old_path}...")
                    for item in old_path.iterdir():
                        dest = TARGET_DIR / item.name
                        if not dest.exists():
                            shutil.move(str(item), str(dest))
                    shutil.rmtree(old_path, ignore_errors=True)

                if not old_path.exists():
                    self.log(f"Linking {old_path} -> {TARGET_DIR}")
                    subprocess.run(
                        ["cmd", "/c", "mklink", "/J", str(old_path), str(TARGET_DIR)],
                        check=True,
                    )

            self.purge_dlls_in_path(TARGET_DIR)
            self.log("Done! Hacknet is now locked to C:\\HacknetSaves\\Hacknet.")
            messagebox.showinfo(
                "Redirect Complete",
                "Hacknet saves are now redirected to C:\\HacknetSaves\\Hacknet.\n\n"
                "Tip: Disable Steam Cloud for Hacknet so old OneDrive saves don't overwrite them.",
            )
        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", f"Failed to redirect saves:\n{e}")

    def reverse_redirect(self):
        confirm = messagebox.askyesno(
            "Confirm Restore",
            "This will remove the directory junctions and copy your saves back to your standard Documents folder.\n\nContinue?",
        )
        if not confirm:
            return

        try:
            self.log("Reversing junctions and restoring saves...")
            for link_path in DOC_PATHS:
                if link_path.is_symlink():
                    self.log(f"Removing junction: {link_path}")
                    subprocess.run(["cmd", "/c", "rmdir", str(link_path)], check=True)

            # Copy saves back to standard Windows Documents\My Games\Hacknet
            restore_dest = DOC_PATHS[0]
            restore_dest.mkdir(parents=True, exist_ok=True)

            if TARGET_DIR.exists():
                self.log(f"Copying saves back to {restore_dest}...")
                for item in TARGET_DIR.iterdir():
                    dest_item = restore_dest / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest_item)

            self.log("Restore complete! Saves are back in your default Documents folder.")
            messagebox.showinfo(
                "Restore Complete",
                f"Your saves have been restored to:\n{restore_dest}\n\n"
                "A backup copy was kept in C:\\HacknetSaves\\Hacknet just in case.",
            )
        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", f"Failed to restore saves:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HacknetManagerApp(root)
    root.mainloop()
