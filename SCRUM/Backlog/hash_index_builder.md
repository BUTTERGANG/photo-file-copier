---
status: backlog
priority: P1
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Hash Index Builder (Drive / Server)

> **Repo:** photo-file-copier
> **Feature ref:** SCRUM/FEATURE_LIST_HASH_INDEX.md — F1, F2
> **Description:** Build persistent SHA-256 manifests of a removable drive or mounted server tree, with copy-job-grade progress UI.
> **UPDATE 2026-11-03:** A prior tool already exists — `BUTTERGANG/drive-index` (also deployed at NAS `/share/CACHEDEV1_DATA/drive-index`). Scope here is the deltas only: full-file SHA-256 (the existing tool uses a 1-MB partial hash), progress-bar UI inside photo_copier, and incremental re-index parity. Don't rebuild what drive-index already does.

---

## Context

User verifies transfers between removable drives and the QNAP server. Today Verify Transfer only covers a single copy run; we need reusable indexes of both sides so any drift (new files added later, reruns) is detectable. Server indexing "takes a minute" — the progress experience must match the existing copy bars, not freeze the UI.

---

## Acceptance Criteria

- [ ] Walk a chosen source root and record `{relpath, sha256, size, date_created, date_modified}` per media file (same supported-format list as the copier)
- [ ] Progress bar: total count, files/sec, bytes processed, ETA, cancel button — styled like the copy job progress
- [ ] Incremental re-index: unchanged entries (size + mtime match) are carried over without re-hashing; changed/new/removed files detected and re-hashed or dropped
- [ ] Manifest persisted per volume + root path (SQLite beside `~/.photo_copier.json`), never corrupted by a cancelled run
- [ ] User can rebuild an index from scratch on demand ("stale indexes may not be the best — rerun anyway")

---

## Technical Notes

- Python stdlib only (repo rule): `hashlib`, `os.scandir`, `sqlite3`, tkinter threading pattern already used by copy jobs
- Date source: per user, use date created or date modified (whichever the app already uses for date-prefix organization) — keep consistent
- Hash read buffer ~1 MB chunks; skip-zero-copy fast path not required
