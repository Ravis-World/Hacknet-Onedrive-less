import ctypes
import os
import shutil
import subprocess
import sys
from pathlib import Path

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

def purge_dlls_in_path(base_path):
    removed = 0
    if base_path.exists():
        for trap_file in base_path.rglob("VMBootloaderTrap.dll"):
            print(f"  [!] Unlocking & deleting: {trap_file}")
            subprocess.run(["icacls", str(trap_file), "/grant", "USERS:F"], check=False, stdout=subprocess.DEVNULL)
            trap_file.unlink(missing_ok=True)
            removed += 1
    return removed

def clean_traps_only():
    print("\n[*] Scanning for VMBootloaderTrap.dll across main game & Steam extensions...")
    total_removed = purge_dlls_in_path(TARGET_DIR)
    for path in DOC_PATHS:
        if path.exists() and not path.is_symlink():
            total_removed += purge_dlls_in_path(path)

    if total_removed > 0:
        print(f"[+] Success! Removed {total_removed} trap file(s).")
    else:
        print("[+] All clean! No VMBootloaderTrap.dll files found.")

def redirect_saves():
    try:
        print("\n[*] Starting save redirection to C:\\HacknetSaves\\Hacknet...")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

        for old_path in DOC_PATHS:
            if not old_path.exists() and not old_path.is_symlink():
                old_path.parent.mkdir(parents=True, exist_ok=True)
            elif old_path.exists() and not old_path.is_symlink():
                purge_dlls_in_path(old_path)
                print(f"[*] Moving files from {old_path}...")
                for item in old_path.iterdir():
                    dest = TARGET_DIR / item.name
                    if not dest.exists():
                        shutil.move(str(item), str(dest))
                shutil.rmtree(old_path, ignore_errors=True)

            if not old_path.exists():
                print(f"[*] Linking {old_path} -> {TARGET_DIR}")
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(old_path), str(TARGET_DIR)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )

        purge_dlls_in_path(TARGET_DIR)
        print("[+] Done! Hacknet is now locked to C:\\HacknetSaves\\Hacknet.")
        print("[i] Tip: Turn off Steam Cloud for Hacknet so old OneDrive saves don't overwrite yours.")
    except Exception as e:
        print(f"[-] ERROR: {e}")

def reverse_redirect():
    confirm = input("\n[?] Remove junctions and copy saves back to default Documents? (y/n): ").strip().lower()
    if confirm != "y":
        print("[*] Cancelled.")
        return

    try:
        print("\n[*] Reversing junctions and restoring saves...")
        for link_path in DOC_PATHS:
            if link_path.is_symlink():
                print(f"[*] Removing junction: {link_path}")
                subprocess.run(["cmd", "/c", "rmdir", str(link_path)], check=True)

        restore_dest = DOC_PATHS[0]
        restore_dest.mkdir(parents=True, exist_ok=True)

        if TARGET_DIR.exists():
            print(f"[*] Copying saves back to {restore_dest}...")
            for item in TARGET_DIR.iterdir():
                dest_item = restore_dest / item.name
                if item.is_dir():
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest_item)

        print(f"[+] Restore complete! Saves are back in {restore_dest}.")
        print("[i] A backup copy was kept in C:\\HacknetSaves\\Hacknet just in case.")
    except Exception as e:
        print(f"[-] ERROR: {e}")

def main_menu():
    os.system("color 0A")  # Gives the terminal a classic Hacknet green-on-black look
    while True:
        print("\n=======================================================")
        print("      HACKNET SAVE REDIRECT & BOOTLOADER RECOVERY      ")
        print("=======================================================")
        print("  [1] Purge VMBootloaderTrap.dll (Main + Extensions)")
        print("  [2] Redirect Saves to C:\\HacknetSaves (Bypass OneDrive)")
        print("  [3] Reverse / Restore Saves to Default Documents")
        print("  [4] Exit")
        print("=======================================================")

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            clean_traps_only()
        elif choice == "2":
            redirect_saves()
        elif choice == "3":
            reverse_redirect()
        elif choice == "4":
            print("\nExiting...")
            break
        else:
            print("\n[-] Invalid selection. Enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()
