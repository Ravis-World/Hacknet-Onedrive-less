# Hacknet Save Redirect & Bootloader Recovery Tool

A lightweight Windows utility (available in both **CLI** and **GUI** versions) designed to rescue *Hacknet* players from the *Labyrinths* `VMBootloaderTrap.dll` crash state and permanently prevent **Microsoft OneDrive** from hijacking or corrupting game save files.

---

## Why This Tool Exists

1. **The `VMBootloaderTrap.dll` Crash:** During *Hacknet Labyrinths* (and several Steam Workshop extensions), a scripted attack drops a permission-locked `VMBootloaderTrap.dll` file into your save folder. Reinstalling the game via Steam does **not** fix this because save files remain untouched inside your `Documents` directory.
2. **OneDrive Sync Conflicts:** Windows frequently redirects `Documents\My Games\Hacknet` into OneDrive. Active syncing can lock files mid-mission, break file permissions, or corrupt saves.

---

## Features

* **Recursive Trap Cleaner:** Scans your base game, *Labyrinths* DLC, and all **Steam Workshop extension** save folders to unlock (`icacls`) and delete `VMBootloaderTrap.dll`.
* **Permanent OneDrive Bypass:** Moves your save files to `C:\HacknetSaves\Hacknet` and creates Windows Directory Junctions (`mklink /J`) so *Hacknet* seamlessly reads and writes offline without OneDrive interference.
* **Safe Restore / Reverse Mode:** Removes directory junctions and restores your save files back to your default Windows `Documents` folder at any time (while preserving a backup in `C:\HacknetSaves\Hacknet`).
* **Auto-Elevation:** Automatically requests Administrator privileges via Windows UAC so permission resets and junction links never fail.

---

## Usage

> **Important:** Completely close **Hacknet** and **Steam** before running any action.

### Option A: Running the Pre-Compiled `.exe`
1. Download or launch `hacknet_cli.exe` (terminal menu) or `hacknet_manager.exe` (windowed GUI).
2. Click **Yes** when Windows asks for Administrator permission.
3. Choose your desired action:
   * **1. Purge `VMBootloaderTrap.dll`:** Removes the bootloader lock file so your game can boot normally again.
   * **2. Redirect Saves to `C:\HacknetSaves`:** Migrates saves out of OneDrive and sets up directory junctions.
   * **3. Reverse / Restore Saves:** Unlinks the junctions and copies saves back to your standard `Documents` folder.

### Option B: Running from Python Source
Requires **Python 3.8+** on Windows (uses only standard library modules; no third-party packages needed).

```bash
# Run the CLI version
python hacknet_cli.py

# Run the GUI version
python hacknet_manager.py
```

---

## Compiling Your Own `.exe`

If you want to build standalone executables yourself using **PyInstaller**:

```bash
pip install pyinstaller

# Build the CLI executable (keeps terminal window open)
pyinstaller --onefile --uac-admin hacknet_cli.py

# Build the GUI executable (hides background terminal window)
pyinstaller --onefile --noconsole --uac-admin hacknet_manager.py
```

Your compiled `.exe` files will appear inside the `dist/` folder.

---

## Recommended: Disable Steam Cloud Sync

After redirecting your saves to `C:\HacknetSaves\Hacknet`, disable Steam Cloud for *Hacknet* so Steam does not re-download old OneDrive-synced files or restore a previously synced `VMBootloaderTrap.dll`:

1. Open **Steam** and right-click **Hacknet** in your Library.
2. Select **Properties** > **General**.
3. Toggle **off** *Keep games saves in the Steam Cloud for Hacknet*.

---

## Disclaimer

This tool modifies local Windows directory junctions (`mklink /J`) and deletes `VMBootloaderTrap.dll` files inside your *Hacknet* user data directories. Always keep a manual backup of your `Accounts` folder before making changes.
