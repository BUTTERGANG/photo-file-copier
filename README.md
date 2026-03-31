# Photo File Copier

A lightweight macOS desktop app for photographers to copy selects from a shoot folder to an output folder — using filenames, shot numbers, or number ranges pasted directly from Apple Notes.

---

## What It Does

When reviewing a shoot you typically jot down the keeper shot numbers in Apple Notes (e.g. `1765`, `1772`, `1801`). This app takes that list and finds the matching files anywhere inside your source folder(s), then copies them cleanly to an output folder — no duplicates, no manual dragging.

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

### 1 — Add source folder(s)

Click **+ Add Folder** to add the folder(s) where your photo files live. You can add multiple — useful when a shoot spans two memory cards or session folders. Added folders persist between sessions.

### 2 — Set the output folder

Click **Browse…** next to Output Folder to choose where copies will be saved. This also persists.

### 3 — Paste your file list

Click in the **Files to Copy** box and paste your list from Apple Notes. Three input formats are supported on each line:

| Format | Example | What it does |
|---|---|---|
| Shot number | `1765` | Finds any image whose filename contains that number |
| Number range | `1765-1772` | Expands to all shot numbers from 1765 to 1772 inclusive |
| Full filename | `_MG_1765.JPG` | Exact filename match (case-insensitive) |

You can mix all three formats in the same list.

> **Ranges:** Regular hyphens, en-dashes, and em-dashes all work — Apple Notes sometimes auto-converts hyphens to em-dashes and the app handles this transparently.

### 4 — Click Copy Files

The progress bar fills as each file is processed. The status log updates in real time with colour-coded results:

- **Green ✓** — copied successfully
- **Orange –** — not found in any source folder
- **Gray ↩** — already exists in output folder, skipped
- **Red ✗** — file found but copy failed (permissions, disk full, etc.)

### 5 — After the run

Two buttons appear in the status log header:

- **Open in Finder** — opens the output folder directly in Finder
- **Copy Missing List** — if any files were not found, copies their names to the clipboard so you can paste them back into Notes or investigate in Finder

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

If a file with the same name already exists in the output folder it is **skipped** (not overwritten, not renamed). This makes it safe to run the same list multiple times — previously copied files are left untouched.

---

## Preferences

Source folders and the output folder path are saved automatically to `~/.photo_copier.json` and restored the next time you open the app.

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
