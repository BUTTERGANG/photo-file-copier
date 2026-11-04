---
status: backlog
priority: P1
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Lazy Full SHA-256 Verification Column

> **Repo:** photo-file-copier / drive-index
> **Description:** Add true full-file SHA-256 fingerprints where partial hashes fall short — without paying a 2-day full scan.

---

## Context

drive-index uses a 1 MB partial hash (first 1 MB) + size. Good enough to catch renames/copies, but it **cannot detect content corruption** where a file's first 1 MB and size match but the body differs. Index analysis (2026-11-03): 1,442,280 files / 16.28 TB; only 360,808 files exceed 1 MB, so full hashing only matters for those. Full-hash rebuild of everything ≈ +18–29 h of reads (~2 days) — never do it as one pass.

---

## Acceptance Criteria

- [ ] `full_hash` column added to `server_files` (and scanner JSON optionally), nullable, computed lazily
- [ ] Lazy computation strategy: files ≤ 1 MB get full hash for free during incremental runs; files > 1 MB get full hash over multiple nightly batches (budget-limited, e.g. 1 h/night) so the queue drains over weeks without disturbing the Sunday incremental
- [ ] On-demand: before a "safe to erase originals" verdict, any file whose only fingerprint is partial gets a full hash computed first
- [ ] Compare report flags `partial-only` files distinctly from fully-verified ones

---

## Technical Notes

- Keep partial hash as the fast primary fingerprint; full hash is additive
- Budgeted nightly batches make this safe for the Sunday 3 AM cron coexistence
