---
status: backlog
priority: P2
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# NAS Storage Consolidation & Cleanup Plan (Epic)

> **Repo:** photo-file-copier / drive-index
> **Description:** The QNAP has hit 80% thresholds on multiple shared folders. Game-plan a large consolidation/cleanup across multiple storage areas, backed by real data from the index and a fresh usage audit.

---

## Context

Prep work for a big reorganization. We already have: the 607 MB server index (1.44M files / 16.28 TB, path + size + mtime + partial hash — an analysis goldmine) and SSH access as BLACKQNAP. What we lack: per-share usage breakdown, duplicate view across shares, and a written plan.

## Phase 1 — Audit (report only, no changes)

- [ ] Per-share/per-volume usage: capacity, used %, largest directories (top 50 by size), file-count and age distribution
- [ ] Cross-share duplicate report using the existing index (same partial_hash + size appearing in 2+ shares, with per-share paths) — the 607 MB DB already has `idx_hash_size` for exactly this
- [ ] "Not on server" intake: what lives on removable drives/laptop but isn't on the server yet (feeds the compare report task)
- [ ] Identify junk by pattern: `@Recycle`, `.Qsync` conflicts, thumbnails/cache dirs, near-empty directories, zero-byte files

## Phase 2 — Game plan (decision doc, no changes)

- [ ] Written consolidation plan: what moves where, what gets archived off-server (cold storage), what gets deleted (with the duplicate evidence attached per item)
- [ ] Migration order that respects the 80% thresholds first (fastest wins: dedupe + trash purge before big moves)
- [ ] Risk rules: anything deleted or moved is hash-verified against the index first; verify-only tooling stays verify-only — moves happen deliberately, per-batch

## Phase 3 — Execute (later, separate tasks)

- [ ] Execute moves in batches with before/after index deltas
- [ ] Re-verify thresholds and close out

---

## Technical Notes

- Phase 1 can run largely off the copied index DB + a `du`-style scan via SSH; no container needed for the audit itself
- Big file counts (1.4M) mean any per-share report must be query-driven from SQLite, not a fresh walk, wherever possible
