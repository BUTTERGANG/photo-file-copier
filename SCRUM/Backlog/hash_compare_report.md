---
status: backlog
priority: P1
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Index Compare Report (Drive vs Server)

> **Repo:** photo-file-copier
> **Feature ref:** SCRUM/FEATURE_LIST_HASH_INDEX.md — F3
> **Description:** Diff two hash indexes and report exactly what made it to the server and what didn't.
> **UPDATE 2026-11-03:** drive-index dashboard already does drive-scan-JSON vs server-index compare (`server/app.py`). Scope here: do the compare natively in photo_copier (no manual JSON upload round-trip) and add hash-mismatch detection, which drive-index can't do with 1-MB partial hashes.

---

## Context

Core purpose of the Photo-Index feature: prove which files have been moved to the QNAP server and which have not, using SHA-256 content identity plus date buckets. Runs after both sides have indexes built.

---

## Acceptance Criteria

- [ ] Pick drive index and server index; run compare with a progress indicator
- [ ] Categories with counts and drill-down lists: Verified on server / On drive, not on server / On server, not on drive / Hash mismatch (both exist, contents differ)
- [ ] Match on hash as primary identity; fall back to date bucket + size so renamed/moved-but-organized files (`1-2-34/JPG/…`) still match
- [ ] Save Report… export (like Save Log…) and Copy Error Report–style clipboard export
- [ ] Verdict line in status bar mirroring the erase-safety pattern: "All N selected files verified on the server" or a clear warning
- [ ] Read-only: compare never deletes, moves, or copies anything

---

## Technical Notes

- Straightforward in-memory dict compare keyed by sha256; date-bucket fallback pass for leftovers
- Large server indexes: compare itself must stay fast (it's the hash walk that's slow, not the diff)
