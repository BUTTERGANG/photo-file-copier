# Photo File Copier

A lightweight macOS desktop app for photographers to copy selects from a shoot folder to an output folder — either from a pasted file list or by copying all supported media files in the source folder(s).

---

## What It Does

When reviewing a shoot you can either paste keeper shot numbers from Apple Notes (e.g. `1765`, `1772`, `1801`) or copy every supported media file from your source folder(s). The app copies files cleanly to an output folder — no duplicates, no manual dragging.

---

## Requirements

| | |
|---|---|
| **macOS** | 11 Big Sur or later |
| **Python** | 3.11 (with tkinter) |

### Install Python 3.11 with tkinter (one time)

```bash
brew install python-tk@3.11
```

---

## Running the App

**Double-click** `Launch Photo Copier.command` in Finder.

> First launch only: right-click → **Open** to allow macOS Gatekeeper, then click **Open** in the dialog.

Or from Terminal:

```bash
python3.11 photo_copier.py
```

---

## How to Use

The interface is organised as a numbered step-by-step flow:

### ❶ — Add source folder(s)

Click **+ Add Folder** to add the folder(s) where your photo files live. You can add multiple — useful when a shoot spans two memory cards or session folders. Added folders persist between sessions.

A folder summary updates above the Copy button as you add sources.

### ❷ — Set the output folder

Click **Browse…** to choose where copies will be saved. This also persists.

### ❸ — Choose copy mode

Use the segmented control to pick either mode:

| Mode | What it does |
|---|---|
| **From file list** | Paste specific filenames, shot numbers, or ranges |
| **Copy all files in source folder(s)** | Bulk-copy every supported media file, ignoring the file list |

When using **From file list**, the following input formats are supported on each line:

| Format | Example | What it does |
|---|---|---|
| Shot number | `1765` | Finds any image whose filename contains that number |
| Number range | `1765-1772` | Expands to all shot numbers from 1765 to 1772 inclusive |
| Full filename | `_MG_1765.JPG` | Exact filename match (case-insensitive) |

You can mix all three formats in the same list.

> **Ranges:** Regular hyphens, en-dashes, and em-dashes all work — Apple Notes sometimes auto-converts hyphens to em-dashes and the app handles this transparently.

### ❹ — Configure options

| Option | Applies to | What it does |
|---|---|---|
| Search subfolders | Both modes | Searches recursively through subdirectories |
| Copy all matching formats (RAW + JPEG) | File list only | When you enter `1765`, copies both `_MG_1765.CR3` and `_MG_1765.JPG` |
| Organize by file type (subfolders) | Both modes | Sorts copies into extension-based folders (`JPG/`, `CR3/`, etc.) |
| Prefix date in type folders | Organize only | Groups by modified date before type (`1-2-34/JPG/…`) |

### Verify before erasing originals

After copying, click **Verify Transfer**. The app compares every source and destination file by size and SHA-256 checksum. Only when every file matches does it show:

> **The originals are safe to erase from the card.**

If anything is missing, changed, or unreadable, the app clearly says **Do not erase originals** and reports the problem in the status log. The app never deletes files from the card automatically; erase them from the camera only after a successful verification.

### Review before copying

Click **Review** before a large transfer to run a non-destructive preflight check. The review reports:

- Number of files selected
- Estimated total size
- File-type breakdown (`JPG`, `CR3`, `MP4`, etc.)
- Files that already exist at the destination and will be skipped
- Requested files that were not found
- Whether the destination has enough free space

Warnings are shown before copying begins; the review never modifies files. The live status log also records the review summary.

### Click Copy Files

The dominant **Copy Files** button shows a dynamic summary of what will happen (e.g. "2 source folders · output set · copying all files"). As files are processed:

- **Green ✓** — copied successfully
- **Orange –** — not found in any source folder (file-list mode)
- **Gray ↩** — already exists at destination, skipped
- **Red ✗** — file found but copy failed (permissions, disk full, etc.)

After the run, action buttons appear in the status bar:

- **Open in Finder** — opens the output folder directly in Finder
- **Copy Missing List** — appears when file-list mode has entries that weren't found
- **Copy Error Report** — appears when a copy fails; copies the failed file, destination, error category, details, and suggested fix to the clipboard
- **Save Log…** — exports the status log to a text file

### Understanding errors

The app never silently ignores a failed copy. Failed files are marked in red in the live status log and grouped into an error report. Common problems are identified as **Permission denied**, **File no longer exists**, **Disk full**, or **Destination is a folder**, with a suggested next step. Less common failures are reported as **Copy failed** with the original system detail preserved. Missing files are tracked separately because they are not copy errors.

---

## Supported File Types

RAW and processed formats from major camera manufacturers:

`.jpg` `.jpeg` `.cr3` `.cr2` `.raf` `.nef` `.arw` `.dng` `.png` `.tif` `.tiff` `.heic` `.mp4` `.mov`

---

## How Shot Number Matching Works

Canon cameras (like the R7) save files as `_MG_1765.CR3`. When you type just `1765`, the app:

1. Extracts the digit sequence from your input
2. Searches every file in the source folder(s) for a filename whose numeric portion matches exactly — `1765` matches `_MG_1765` but **not** `_MG_17650`
3. Returns the first match across all source folders in the order they were added

---

## Duplicate Handling

If a file with the same destination path already exists it is **skipped** (not overwritten, not renamed). With organization off, this is the output root folder. With type organization on, this is the type subfolder (for example `JPG/_MG_1765.JPG`). With date-prefix enabled, this is the nested date/type path (for example `1-2-34/JPG/_MG_1765.JPG`). This makes it safe to run the same list multiple times — previously copied files are left untouched.

---

## Preferences

Source folders, output folder path, and copy options are saved automatically to `~/.photo_copier.json` and restored the next time you open the app.

---

## UI Design

The interface follows Apple design principles — clean, minimal, with a clear visual hierarchy:

- **Dark theme** with layered backgrounds (`#1C1C1E` cards on `#161618` base) and no visible borders
- **Numbered step cards** guide the user through the workflow (❶ → ❷ → ❸ → ❹)
- **Segmented control** replaces radio buttons for mode selection, with the active state clearly highlighted in Apple blue (`#007AFF`)
- **Dynamic summary** above the primary action shows the current configuration at a glance
- **Context-aware controls** — irrelevant options are dimmed or hidden based on the selected mode
- **System typography** using Helvetica Neue with a clear size/weight hierarchy

---

## Project Files

| File | Purpose |
|---|---|
| `photo_copier.py` | Main application — all logic and UI |
| `Launch Photo Copier.command` | Double-click launcher for Finder |
| `README.md` | This file |

---

## Built With

- **Python 3.11** — standard library only (no third-party dependencies)
- **tkinter** — built-in Python GUI toolkit
- Custom `FlatButton` widget to bypass macOS Aqua native button rendering and maintain correct dark-theme colours at all interaction states
