#!/usr/bin/env python3.11
"""
Photo File Copier
Paste a list of filenames, pick source and output folders, copy the files.
"""

import json
import re
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

# ── Image extensions ───────────────────────────────────────────────────────────
IMAGE_EXTS = {".jpg", ".jpeg", ".cr3", ".cr2", ".raf", ".nef", ".arw",
              ".dng", ".png", ".tif", ".tiff", ".heic", ".mp4", ".mov"}

# ── Preferences file ──────────────────────────────────────────────────────────
PREFS_FILE = Path.home() / ".photo_copier.json"

# ── Dark-theme palette ────────────────────────────────────────────────────────
BG          = "#161618"
CARD        = "#242426"
BORDER      = "#3A3A3C"
HDR_BG      = "#0D0D0F"
HDR_FG      = "#F2F2F7"
TEXT        = "#F2F2F7"
MUTED       = "#AEAEB2"
ENTRY_BG    = "#2C2C2E"
ENTRY_BD    = "#48484A"
BLUE        = "#0A84FF"
BLUE_HOV    = "#3395FF"
BLUE_PR     = "#006FD6"
BTN2_BG     = "#3A3A3C"
BTN2_HOV    = "#4A4A4E"
BTN2_PR     = "#2A2A2C"
LOG_BG      = "#0D0D0F"
LOG_FG      = "#D4D4D4"
LOG_DIM     = "#6E6E73"
LOG_OK      = "#30D158"
LOG_MISS    = "#FF9F0A"
LOG_ERR     = "#FF6B6B"
PROG_TRACK  = "#2C2C2E"
ROW_ALT     = "#1E1E20"
RED         = "#FF453A"
RED_HOV     = "#FF6B61"
RED_PR      = "#D93025"

FONT_TITLE  = ("Helvetica Neue", 17, "bold")
FONT_HINT   = ("Helvetica Neue", 11)
FONT_ENTRY  = ("Helvetica Neue", 12)
FONT_BTN    = ("Helvetica Neue", 13, "bold")
FONT_BTN2   = ("Helvetica Neue", 12)
FONT_CAPS   = ("Helvetica Neue", 10, "bold")
FONT_LOG    = ("Menlo", 11)
FONT_PATH   = ("Helvetica Neue", 11)
FONT_SMALL  = ("Helvetica Neue", 10)

PLACEHOLDER = (
    "Paste filenames here — one per line\n"
    "Full name:  _MG_1765.JPG    Shot number:  1765\n"
    "Range:  1765-1772  (copies all shots in that range)"
)

# Matches regular hyphen, en-dash, em-dash between two digit sequences
RANGE_PAT = re.compile(r"^(\d+)\s*[-\u2013\u2014]\s*(\d+)$")

# Max visible height for the source folder list (~4 rows)
SRC_LIST_MAX_H = 120


# ── Custom button (bypasses macOS Aqua native rendering) ──────────────────────
class FlatButton(tk.Label):
    def __init__(self, parent, text, command,
                 bg_n, bg_h, bg_p, fg=TEXT, **kwargs):
        super().__init__(parent, text=text, fg=fg, bg=bg_n,
                         cursor="hand2", **kwargs)
        self._bg_n, self._bg_h, self._bg_p = bg_n, bg_h, bg_p
        self._cmd = command
        self.bind("<Enter>",           lambda _: self.config(bg=self._bg_h))
        self.bind("<Leave>",           lambda _: self.config(bg=self._bg_n))
        self.bind("<ButtonPress-1>",   lambda _: self.config(bg=self._bg_p))
        self.bind("<ButtonRelease-1>", self._release)

    def _release(self, e):
        self.config(bg=self._bg_h)
        if 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
            self._cmd()

    def reconfigure(self, text=None, command=None,
                    bg_n=None, bg_h=None, bg_p=None, fg=None):
        """Update button text, command, and/or colours in place."""
        if text    is not None: self.config(text=text)
        if command is not None: self._cmd = command
        if fg      is not None: self.config(fg=fg)
        if bg_n    is not None:
            self._bg_n = bg_n
            self.config(bg=bg_n)
        if bg_h    is not None: self._bg_h = bg_h
        if bg_p    is not None: self._bg_p = bg_p


# ── Main application ──────────────────────────────────────────────────────────
class PhotoCopier(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo File Copier")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(640, 700)
        self._src_paths          = []
        self._missing_names      = []
        self._last_out_path      = None
        self._last_status        = ""
        self._copy_thread        = None
        self._stop_event         = threading.Event()
        self._clip_job           = None
        self._placeholder_active = False
        self._build_ui()
        self.update_idletasks()
        self._center_window(760, 820)
        self._load_prefs()

    def _center_window(self, w, h):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Preferences ───────────────────────────────────────────────────────────
    def _load_prefs(self):
        try:
            prefs = json.loads(PREFS_FILE.read_text())
            sources = prefs.get("sources") or (
                [prefs["source"]] if prefs.get("source") else []
            )
            for s in sources:
                if s and s not in self._src_paths:
                    self._src_paths.append(s)
            self._render_source_list()
            if out := prefs.get("output"):
                self.out_var.set(out)
            if prefs.get("all_formats") is not None:
                self.all_formats_var.set(prefs["all_formats"])
        except Exception:
            pass

    def _save_prefs(self):
        try:
            prefs = {
                "sources":     self._src_paths,
                "output":      self.out_var.get(),
                "all_formats": self.all_formats_var.get(),
            }
            PREFS_FILE.write_text(json.dumps(prefs))
        except Exception:
            pass

    # ── Card / entry helpers ──────────────────────────────────────────────────
    def _card(self, parent, padx=16, pady=14):
        outer = tk.Frame(parent, bg=BORDER)
        outer.pack(fill="x", padx=20, pady=(0, 10))
        inner = tk.Frame(outer, bg=CARD, padx=padx, pady=pady)
        inner.pack(fill="x", padx=1, pady=1)
        return inner

    def _entry(self, parent, textvariable):
        border = tk.Frame(parent, bg=ENTRY_BD)
        tk.Entry(
            border,
            textvariable=textvariable,
            font=FONT_ENTRY,
            bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT,
            relief="flat", bd=6,
            highlightthickness=0,
        ).pack(padx=1, pady=1, fill="x")
        return border

    def _log_hdr_btn(self, parent, text, command, fg):
        return FlatButton(
            parent, text, command,
            bg_n="#1A1A1C", bg_h="#2C2C2E", bg_p="#111113",
            fg=fg, font=FONT_SMALL, padx=0, pady=5,
        )

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):

        # ── Header ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=HDR_BG, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📷", font=("Helvetica Neue", 26),
                 bg=HDR_BG, fg=BLUE).pack(side="left", padx=(18, 10))
        col = tk.Frame(hdr, bg=HDR_BG)
        col.pack(side="left")
        tk.Label(col, text="Photo File Copier",
                 font=FONT_TITLE, bg=HDR_BG, fg=HDR_FG, anchor="w").pack(anchor="w")
        tk.Label(col, text="Copy selected images to an output folder",
                 font=FONT_HINT, bg=HDR_BG, fg=MUTED, anchor="w").pack(anchor="w")

        tk.Frame(self, bg=BG, height=14).pack(fill="x")

        # ── Source folders card ────────────────────────────────────────────
        src_card = self._card(self, pady=14)

        src_hdr = tk.Frame(src_card, bg=CARD)
        src_hdr.pack(fill="x", pady=(0, 8))
        tk.Label(src_hdr, text="SOURCE FOLDERS",
                 font=FONT_CAPS, bg=CARD, fg=MUTED).pack(side="left")
        FlatButton(src_hdr, " + Add Folder ", self._add_source,
                   bg_n=BTN2_BG, bg_h=BTN2_HOV, bg_p=BTN2_PR,
                   font=FONT_SMALL, padx=4, pady=4).pack(side="right")

        # Scrollable source list — canvas + optional scrollbar
        src_scroll_outer = tk.Frame(src_card, bg=CARD)
        src_scroll_outer.pack(fill="x")

        self._src_scrollbar = tk.Scrollbar(
            src_scroll_outer, orient="vertical",
            troughcolor=CARD, relief="flat", bd=0, width=10)
        self._src_canvas = tk.Canvas(
            src_scroll_outer, bg=CARD, highlightthickness=0, height=1, bd=0)
        self._src_canvas.configure(yscrollcommand=self._src_scrollbar.set)
        self._src_scrollbar.configure(command=self._src_canvas.yview)

        self._src_list_frame = tk.Frame(self._src_canvas, bg=CARD)
        self._src_canvas_win = self._src_canvas.create_window(
            (0, 0), window=self._src_list_frame, anchor="nw")

        self._src_list_frame.bind("<Configure>", self._on_src_list_configure)
        self._src_canvas.bind("<Configure>", self._on_src_canvas_configure)
        self._src_canvas.bind(
            "<MouseWheel>",
            lambda e: self._src_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"))
        self._src_canvas.pack(side="left", fill="x", expand=True)

        # ── Output folder card ─────────────────────────────────────────────
        out_card = self._card(self, pady=14)
        tk.Label(out_card, text="OUTPUT FOLDER",
                 font=FONT_CAPS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 5))
        out_row = tk.Frame(out_card, bg=CARD)
        out_row.pack(fill="x")
        self.out_var = tk.StringVar()
        self._entry(out_row, self.out_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        FlatButton(out_row, " Browse… ", self._pick_output,
                   bg_n=BTN2_BG, bg_h=BTN2_HOV, bg_p=BTN2_PR,
                   font=FONT_BTN2, padx=4, pady=6).pack(side="left")

        # ── File list card ─────────────────────────────────────────────────
        list_card = self._card(self, pady=14)

        list_hdr = tk.Frame(list_card, bg=CARD)
        list_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(list_hdr, text="FILES TO COPY",
                 font=FONT_CAPS, bg=CARD, fg=MUTED).pack(side="left")
        clear_btn = tk.Label(list_hdr, text="Clear", font=FONT_HINT,
                             bg=CARD, fg=BLUE, cursor="hand2")
        clear_btn.pack(side="right")
        clear_btn.bind("<ButtonRelease-1>", lambda _: (
            self.file_box.delete("1.0", "end"), self._show_placeholder()))
        clear_btn.bind("<Enter>", lambda _: clear_btn.config(fg=BLUE_HOV))
        clear_btn.bind("<Leave>", lambda _: clear_btn.config(fg=BLUE))
        tk.Label(list_hdr,
                 text="name, number, or range  e.g. 1765-1772",
                 font=FONT_SMALL, bg=CARD, fg=MUTED).pack(side="right", padx=(0, 12))

        txt_border = tk.Frame(list_card, bg=ENTRY_BD)
        txt_border.pack(fill="both", expand=True)
        txt_inner = tk.Frame(txt_border, bg=ENTRY_BG)
        txt_inner.pack(fill="both", expand=True, padx=1, pady=1)
        scroll = tk.Scrollbar(txt_inner, width=10,
                              troughcolor=ENTRY_BG, relief="flat", bd=0)
        scroll.pack(side="right", fill="y")
        self.file_box = tk.Text(
            txt_inner, height=8,
            font=FONT_ENTRY,
            bg=ENTRY_BG, fg=MUTED,
            insertbackground=TEXT,
            relief="flat", bd=0,
            padx=10, pady=8,
            yscrollcommand=scroll.set,
            wrap="none",
        )
        self.file_box.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.file_box.yview)
        self._show_placeholder()
        self.file_box.bind("<FocusIn>",  self._clear_placeholder)
        self.file_box.bind("<FocusOut>", self._maybe_placeholder)

        # ── Options row ────────────────────────────────────────────────────
        opt_row = tk.Frame(self, bg=BG)
        opt_row.pack(fill="x", padx=21, pady=(0, 10))
        self.recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            opt_row,
            text="  Search subfolders",
            variable=self.recursive_var,
            font=FONT_HINT,
            bg=BG, fg=MUTED,
            activebackground=BG, activeforeground=TEXT,
            selectcolor=CARD,
            relief="flat", cursor="hand2",
        ).pack(side="left")

        self.all_formats_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opt_row,
            text="  Copy all matching formats",
            variable=self.all_formats_var,
            font=FONT_HINT,
            bg=BG, fg=MUTED,
            activebackground=BG, activeforeground=TEXT,
            selectcolor=CARD,
            relief="flat", cursor="hand2",
            command=self._save_prefs,
        ).pack(side="left", padx=(16, 0))

        # ── Copy Files button ──────────────────────────────────────────────
        btn_wrap = tk.Frame(self, bg=BG)
        btn_wrap.pack(fill="x", padx=20, pady=(0, 8))
        self._copy_btn = FlatButton(
            btn_wrap, "  Copy Files  ", self._copy_files,
            bg_n=BLUE, bg_h=BLUE_HOV, bg_p=BLUE_PR,
            fg="white", font=FONT_BTN, padx=0, pady=12,
        )
        self._copy_btn.pack(fill="x")

        # ── Progress bar ───────────────────────────────────────────────────
        prog_wrap = tk.Frame(self, bg=BG)
        prog_wrap.pack(fill="x", padx=20, pady=(0, 10))
        self._prog_track = tk.Canvas(prog_wrap, bg=PROG_TRACK,
                                     height=6, highlightthickness=0)
        self._prog_track.pack(fill="x")
        self._prog_fill = self._prog_track.create_rectangle(
            0, 0, 0, 6, fill=BLUE, width=0)
        self._prog_total = 1

        # ── Status log ────────────────────────────────────────────────────
        log_outer = tk.Frame(self, bg=BORDER)
        log_outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        log_hdr = tk.Frame(log_outer, bg="#1A1A1C", height=28)
        log_hdr.pack(fill="x")
        log_hdr.pack_propagate(False)
        tk.Label(log_hdr, text="STATUS LOG",
                 font=FONT_CAPS, bg="#1A1A1C", fg=MUTED).pack(
            side="left", padx=12, pady=5)

        # Action buttons in log header — hidden until relevant
        self._finder_btn       = self._log_hdr_btn(log_hdr, "  Open in Finder  ",     self._open_in_finder,             BLUE)
        self._copy_missing_btn = self._log_hdr_btn(log_hdr, "  Copy Missing List  ",  self._copy_missing_to_clipboard,  LOG_MISS)
        self._save_log_btn     = self._log_hdr_btn(log_hdr, "  Save Log…  ",           self._save_log,                   MUTED)

        self.status_label = tk.Label(log_hdr, text="",
                                     font=FONT_HINT, bg="#1A1A1C", fg=MUTED)
        self.status_label.pack(side="right", padx=12)

        log_body = tk.Frame(log_outer, bg=LOG_BG)
        log_body.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        log_scroll = tk.Scrollbar(log_body, width=10,
                                  troughcolor=LOG_BG, relief="flat", bd=0)
        log_scroll.pack(side="right", fill="y")
        self.log_box = tk.Text(
            log_body,
            font=FONT_LOG,
            bg=LOG_BG, fg=LOG_FG,
            relief="flat", bd=0,
            padx=12, pady=8,
            state="disabled",
            yscrollcommand=log_scroll.set,
        )
        self.log_box.pack(side="left", fill="both", expand=True)
        log_scroll.config(command=self.log_box.yview)
        self.log_box.tag_config("ok",   foreground=LOG_OK)
        self.log_box.tag_config("miss", foreground=LOG_MISS)
        self.log_box.tag_config("err",  foreground=LOG_ERR)
        self.log_box.tag_config("skip", foreground="#636366")
        self.log_box.tag_config("dim",  foreground=LOG_DIM)

    # ── Scrollable source list callbacks ──────────────────────────────────────
    def _on_src_list_configure(self, _=None):
        """Resize canvas and show/hide scrollbar whenever the list changes."""
        self._src_canvas.configure(scrollregion=self._src_canvas.bbox("all"))
        content_h = max(self._src_list_frame.winfo_reqheight(), 30)
        capped_h  = min(content_h, SRC_LIST_MAX_H)
        self._src_canvas.config(height=capped_h)
        if content_h > SRC_LIST_MAX_H:
            self._src_scrollbar.pack(side="right", fill="y")
        else:
            self._src_scrollbar.pack_forget()

    def _on_src_canvas_configure(self, event):
        """Keep inner frame width in sync with canvas width."""
        self._src_canvas.itemconfig(self._src_canvas_win, width=event.width)

    # ── Source folder list ────────────────────────────────────────────────────
    def _render_source_list(self):
        for w in self._src_list_frame.winfo_children():
            w.destroy()

        if not self._src_paths:
            tk.Label(self._src_list_frame,
                     text="No folders added — click  + Add Folder",
                     font=FONT_HINT, bg=CARD, fg=MUTED).pack(
                anchor="w", pady=4)
            return

        for i, path_str in enumerate(self._src_paths):
            p = Path(path_str)
            display = f"{p.parent.name}/{p.name}" if p.parent.name else p.name
            row_bg = ROW_ALT if i % 2 else CARD

            row = tk.Frame(self._src_list_frame, bg=row_bg)
            row.pack(fill="x", pady=(0, 1))

            tk.Label(row, text="📁", font=FONT_SMALL,
                     bg=row_bg, fg=MUTED).pack(side="left", padx=(0, 6), pady=4)
            tk.Label(row, text=display, font=FONT_PATH,
                     bg=row_bg, fg=TEXT, anchor="w").pack(
                side="left", fill="x", expand=True)

            rm = tk.Label(row, text="  ×  ", font=FONT_BTN2,
                          bg=row_bg, fg=MUTED, cursor="hand2")
            rm.pack(side="right", padx=4)
            rm.bind("<Enter>", lambda e, w=rm: w.config(fg=LOG_ERR))
            rm.bind("<Leave>", lambda e, w=rm, bg=row_bg: w.config(fg=MUTED, bg=bg))
            rm.bind("<ButtonRelease-1>",
                    lambda e, s=path_str: self._remove_source(s))

    def _add_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder and folder not in self._src_paths:
            self._src_paths.append(folder)
            self._render_source_list()
            self._save_prefs()

    def _remove_source(self, path_str):
        if path_str in self._src_paths:
            self._src_paths.remove(path_str)
            self._render_source_list()
            self._save_prefs()

    # ── Output folder picker ──────────────────────────────────────────────────
    def _pick_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.out_var.set(folder)
            self._save_prefs()

    # ── Range expansion ───────────────────────────────────────────────────────
    def _expand_names(self, names):
        """Expand range tokens like '1765-1772' into individual number strings."""
        result = []
        for name in names:
            m = RANGE_PAT.match(name.strip())
            if m:
                a, b = m.group(1), m.group(2)
                start, end = int(a), int(b)
                if start > end:
                    result.append(name)
                    continue
                pad = len(a) if a.startswith("0") else 0
                for n in range(start, end + 1):
                    result.append(str(n).zfill(pad) if pad else str(n))
            else:
                result.append(name)
        return result

    # ── File finders ──────────────────────────────────────────────────────────
    def _parse_search_name(self, name):
        """Pre-process name into (has_ext, name_lower, pattern).
        Called once per name so the regex is compiled only once regardless of
        how many source folders are searched.
        """
        has_ext = Path(name).suffix.lower() in IMAGE_EXTS
        if has_ext:
            return True, name.lower(), None
        digits = re.sub(r"\D", "", name)
        if not digits:
            return False, None, None
        return False, None, re.compile(r"(?<!\d)" + re.escape(digits) + r"(?!\d)")

    def _find_in_sources(self, name):
        """Return the first matching file across all source folders."""
        params = self._parse_search_name(name)
        for src_str in self._src_paths:
            result = self._find_file(Path(src_str), name, params)
            if result:
                return result
        return None

    def _find_all_in_sources(self, name):
        """Return every matching file across all source folders (all formats)."""
        params  = self._parse_search_name(name)
        results = []
        seen    = set()
        for src_str in self._src_paths:
            for f in self._find_all_files(Path(src_str), name, params):
                if f not in seen:
                    seen.add(f)
                    results.append(f)
        return results

    def _find_file(self, root: Path, name: str, params=None):
        """Return the first file matching `name` under `root`.

        `name` can be a full filename with extension or just a shot number.
        Pass pre-built `params` from `_parse_search_name` to avoid recompiling
        the regex when searching multiple source folders for the same name.
        """
        has_ext, name_lower, pattern = params or self._parse_search_name(name)
        if has_ext:
            if self.recursive_var.get():
                for f in root.rglob("*"):
                    if f.is_file() and f.name.lower() == name_lower:
                        return f
            else:
                candidate = root / name
                if candidate.is_file():
                    return candidate
        else:
            if not pattern:
                return None
            files = root.rglob("*") if self.recursive_var.get() else root.iterdir()
            for f in files:
                if f.is_file() and f.suffix.lower() in IMAGE_EXTS and pattern.search(f.stem):
                    return f
        return None

    def _find_all_files(self, root: Path, name: str, params=None):
        """Return ALL files matching `name` under `root` (for all-formats mode)."""
        has_ext, name_lower, pattern = params or self._parse_search_name(name)
        if has_ext:
            if self.recursive_var.get():
                return [f for f in root.rglob("*")
                        if f.is_file() and f.name.lower() == name_lower]
            candidate = root / name
            return [candidate] if candidate.is_file() else []
        else:
            if not pattern:
                return []
            files = root.rglob("*") if self.recursive_var.get() else root.iterdir()
            return [f for f in files
                    if f.is_file()
                    and f.suffix.lower() in IMAGE_EXTS
                    and pattern.search(f.stem)]

    # ── Progress helpers ──────────────────────────────────────────────────────
    def _progress_reset(self, total):
        self._prog_total = max(total, 1)
        self._prog_track.coords(self._prog_fill, 0, 0, 0, 6)
        self._prog_track.itemconfig(self._prog_fill, fill=BLUE)
        self.update_idletasks()

    def _progress_step(self, done):
        w = self._prog_track.winfo_width()
        self._prog_track.coords(self._prog_fill, 0, 0,
                                int(w * done / self._prog_total), 6)
        self.update_idletasks()

    def _progress_complete(self, success=True):
        w = self._prog_track.winfo_width()
        self._prog_track.coords(self._prog_fill, 0, 0, w, 6)
        self._prog_track.itemconfig(self._prog_fill,
                                    fill=LOG_OK if success else LOG_ERR)
        self.update_idletasks()

    # ── Placeholder helpers ───────────────────────────────────────────────────
    def _show_placeholder(self):
        self.file_box.delete("1.0", "end")
        self.file_box.insert("1.0", PLACEHOLDER)
        self.file_box.config(fg=MUTED)
        self._placeholder_active = True

    def _clear_placeholder(self, _=None):
        if self._placeholder_active:
            self.file_box.delete("1.0", "end")
            self.file_box.config(fg=TEXT)
            self._placeholder_active = False

    def _maybe_placeholder(self, _=None):
        if not self.file_box.get("1.0", "end").strip():
            self._show_placeholder()

    # ── Open in Finder ────────────────────────────────────────────────────────
    def _open_in_finder(self):
        if self._last_out_path and self._last_out_path.is_dir():
            subprocess.run(["open", str(self._last_out_path)])

    # ── Timed status label helper ─────────────────────────────────────────────
    def _flash_status(self, msg, restore_after_ms=2000):
        """Show `msg` in the status label then restore the run summary."""
        if self._clip_job:
            self.after_cancel(self._clip_job)
        self.status_label.config(text=msg)
        self._clip_job = self.after(
            restore_after_ms,
            lambda: self.status_label.config(text=self._last_status))

    # ── Copy missing list to clipboard ────────────────────────────────────────
    def _copy_missing_to_clipboard(self):
        if not self._missing_names:
            return
        self.clipboard_clear()
        self.clipboard_append("\n".join(self._missing_names))
        self._flash_status("Copied to clipboard!")

    # ── Save log to file ──────────────────────────────────────────────────────
    def _save_log(self):
        path = filedialog.asksaveasfilename(
            title="Save Status Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="photo_copier_log.txt",
        )
        if not path:
            return
        try:
            text = self.log_box.get("1.0", "end-1c")
            Path(path).write_text(text, encoding="utf-8")
            self._flash_status("Log saved!")
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))

    # ── Logging ───────────────────────────────────────────────────────────────
    def _log(self, msg, tag=None):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n", tag or "")
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        self.update_idletasks()

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    # ── Copy button state ─────────────────────────────────────────────────────
    def _set_copy_btn_state(self, running: bool):
        if running:
            self._copy_btn.reconfigure(
                text="  Cancel  ", command=self._cancel_copy,
                bg_n=RED, bg_h=RED_HOV, bg_p=RED_PR,
            )
        else:
            self._copy_btn.reconfigure(
                text="  Copy Files  ", command=self._copy_files,
                bg_n=BLUE, bg_h=BLUE_HOV, bg_p=BLUE_PR,
            )

    def _cancel_copy(self):
        self._stop_event.set()
        self._copy_btn.reconfigure(text="  Cancelling…  ")

    # ── Core copy logic ───────────────────────────────────────────────────────
    def _copy_files(self):
        if self._copy_thread and self._copy_thread.is_alive():
            return  # guard — shouldn't happen since button swaps to Cancel

        out = self.out_var.get().strip()
        raw = "" if self._placeholder_active else self.file_box.get("1.0", "end").strip()

        if not self._src_paths:
            messagebox.showwarning("No Source Folders",
                                   "Please add at least one source folder.")
            return
        if not out:
            messagebox.showwarning("Missing Output", "Please select an output folder.")
            return
        if not raw:
            messagebox.showwarning("No Files", "Please paste at least one file name.")
            return

        raw_names = [line.strip() for line in raw.splitlines() if line.strip()]
        names     = self._expand_names(raw_names)
        out_path  = Path(out)

        bad = [s for s in self._src_paths if not Path(s).is_dir()]
        if bad:
            messagebox.showerror("Bad Source",
                                 "These source folders were not found:\n" +
                                 "\n".join(bad))
            return

        out_path.mkdir(parents=True, exist_ok=True)
        self._last_out_path = out_path
        self._missing_names = []
        self._last_status   = ""

        self._clear_log()
        self._progress_reset(len(names))
        self._finder_btn.pack_forget()
        self._copy_missing_btn.pack_forget()
        self._save_log_btn.pack_forget()
        self.status_label.config(text="Running…")
        self._set_copy_btn_state(True)

        expanded_count = len(names) - len(raw_names)
        for src_str in self._src_paths:
            self._log(f"Source  {src_str}", "dim")
        self._log(f"Output  {out_path}", "dim")
        if self.all_formats_var.get():
            self._log("Mode    copy all matching formats (RAW + JPEG)", "dim")
        if expanded_count > 0:
            self._log(f"Expanded {expanded_count} range entries  →  "
                      f"{len(names)} total files", "dim")
        self._log(f"{'─' * 60}", "dim")

        self._stop_event.clear()
        self._copy_thread = threading.Thread(
            target=self._run_copy,
            args=(names, out_path, self.all_formats_var.get()),
            daemon=True,
        )
        self._copy_thread.start()

    def _run_copy(self, names, out_path, all_formats):
        """Background thread — copies files and posts UI updates via after()."""
        def ui(fn, *args, **kw):
            self.after(0, lambda: fn(*args, **kw))

        copied = missing = skipped = errors = 0
        cancelled = False

        for i, name in enumerate(names, 1):
            if self._stop_event.is_set():
                cancelled = True
                ui(self._log, f"{'─' * 60}", "dim")
                ui(self._log, "  ⊘  Cancelled", "err")
                break

            bare = Path(name).name

            if all_formats:
                found_files = self._find_all_in_sources(bare)
            else:
                f = self._find_in_sources(bare)
                found_files = [f] if f else []

            if not found_files:
                ui(self._log, f"  – NOT FOUND   {bare}", "miss")
                self._missing_names.append(bare)
                missing += 1
            else:
                for found in found_files:
                    dest = out_path / found.name
                    if dest.exists():
                        ui(self._log, f"  ↩  ALREADY EXISTS   {found.name}", "skip")
                        skipped += 1
                    else:
                        try:
                            shutil.copy2(found, dest)
                            label = found.name if found.name != bare else bare
                            ui(self._log, f"  ✓  {label}", "ok")
                            copied += 1
                        except Exception as e:
                            ui(self._log, f"  ✗  {found.name}  ({e})", "err")
                            errors += 1

            ui(self._progress_step, i)

        self.after(0, lambda: self._finish_copy(
            copied, skipped, missing, errors, cancelled))

    def _finish_copy(self, copied, skipped, missing, errors, cancelled):
        """Called on the main thread when the copy thread finishes or is cancelled."""
        self._set_copy_btn_state(False)

        if not cancelled:
            self._log(f"{'─' * 60}", "dim")
            self._log(
                f"  Copied {copied}   Skipped {skipped}   "
                f"Not found {missing}   Errors {errors}", "dim")

        self._progress_complete(
            success=(errors == 0 and missing == 0 and not cancelled))

        parts = []
        if cancelled:
            parts.append("Cancelled")
        else:
            parts.append(f"✓ {copied} copied")
        if skipped: parts.append(f"{skipped} skipped")
        if missing: parts.append(f"{missing} missing")
        if errors:  parts.append(f"{errors} errors")
        self._last_status = "  ·  ".join(parts)
        self.status_label.config(text=self._last_status)

        self._finder_btn.pack(side="right", padx=(0, 4))
        self._save_log_btn.pack(side="right", padx=(0, 4))
        if self._missing_names:
            self._copy_missing_btn.pack(side="right", padx=(0, 4))

        if cancelled:
            return

        if missing == 0 and errors == 0:
            msg = f"Copied {copied} file(s) to:\n{self._last_out_path}"
            if skipped:
                msg += f"\n\n{skipped} file(s) already existed and were skipped."
            messagebox.showinfo("Done!", msg)
        else:
            messagebox.showwarning(
                "Done with issues",
                f"Copied: {copied}\nSkipped (already exists): {skipped}\n"
                f"Not found: {missing}\nErrors: {errors}\n\n"
                "Check the status log for details.",
            )


if __name__ == "__main__":
    app = PhotoCopier()
    app.mainloop()
