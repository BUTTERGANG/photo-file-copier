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

### 1 — Add source folder(s)

Click **+ Add Folder** to add the folder(s) where your photo files live. You can add multiple — useful when a shoot spans two memory cards or session folders. Added folders persist between sessions.

### 2 — Set the output folder

Click **Browse…** next to Output Folder to choose where copies will be saved. This also persists.

### 3 — Choose copy mode

You can use either mode:

- **From file list** — paste names/numbers/ranges in the Files to Copy box
- **Copy all supported files in source folder(s)** — ignore the list and bulk copy supported media

When using **From file list**, the following input formats are supported on each line:

| Format | Example | What it does |
|---|---|---|
| Shot number | `1765` | Finds any image whose filename contains that number |
| Number range | `1765-1772` | Expands to all shot numbers from 1765 to 1772 inclusive |
| Full filename | `_MG_1765.JPG` | Exact filename match (case-insensitive) |

You can mix all three formats in the same list.

> **Ranges:** Regular hyphens, en-dashes, and em-dashes all work — Apple Notes sometimes auto-converts hyphens to em-dashes and the app handles this transparently.

### 4 — Optional: organize output folders

Enable **Organize by file type (subfolders)** to sort copies into extension folders on the first pass:

- `_MG_1765.JPG` → `JPG/_MG_1765.JPG`
- `_MG_1765.CR3` → `CR3/_MG_1765.CR3`
- `clip_1765.MP4` → `MP4/clip_1765.MP4`
- files with no extension → `NO_EXT/<filename>`

Optional: enable **Prefix date in type folders** to group by modified date first, then file type (`M-D-YY/TYPE`):

- `_MG_1765.JPG` → `1-2-34/JPG/_MG_1765.JPG`
- `_MG_1765.CR3` → `1-2-34/CR3/_MG_1765.CR3`

### 5 — Click Copy Files

The progress bar fills as each file is processed. The status log updates in real time with colour-coded results:

- **Green ✓** — copied successfully
- **Orange –** — not found in any source folder (file-list mode)
- **Gray ↩** — already exists at destination, skipped
- **Red ✗** — file found but copy failed (permissions, disk full, etc.)

### 6 — Option behavior by mode

- **Search subfolders** applies to both modes.
- **Copy all matching formats** applies to **From file list** mode only.
- **Organize by file type (subfolders)** applies to both modes.
- **Prefix date in type folders** applies only when **Organize by file type** is enabled, and uses file modified date.

### 7 — After the run

Two buttons appear in the status log header:

- **Open in Finder** — opens the output folder directly in Finder
- **Copy Missing List** — appears when file-list mode has missing entries

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
