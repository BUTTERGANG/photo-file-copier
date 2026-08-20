---
status: backlog
priority: P2
agent_claimed: null
claimed_at: null
updated: 2026-08-20
---

# Duplicate Detection and Dedup

> **Repo:** photo-file-copier
> **Description:** Find and resolve duplicate photos during import by hash and metadata

---

## Context

Users import photos from multiple sources (SD cards, phones, drives). Need to detect duplicates by file hash, EXIF timestamp, and filename similarity.

---

## Acceptance Criteria

- [ ] SHA-256 hash comparison for exact duplicate detection
- [ ] Fuzzy metadata matching for near-duplicates (same timestamp, similar filename)
- [ ] Interactive dup resolution UI (keep newest, keep largest, keep both, skip all)
- [ ] Batch auto-resolve with configurable rules for known dup patterns

---

## Technical Notes

- Python hashlib for fast SHA-256; EXIF parsing for timestamp comparison; TUI or simple web UI for interactive mode
