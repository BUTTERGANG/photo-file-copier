---
status: backlog
priority: P3
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Unified Flow: Scan → Compare → Copy → Verify → Update

> **Repo:** photo-file-copier / drive-index
> **Vision ref:** SCRUM/AGENT_FLEET_VISION.md — F8
> **Description:** Fold the drive-index scan/compare into photo_copier's copy wizard so one app does the whole job end to end.

---

## Context

Today the job spans two apps and a manual JSON hand-off: photo_copier copies + verifies, drive-index scans and compares via dashboard upload. The copy engine already has the hardest parts (date+type organization, shot-number selection, Verify Transfer, progress bars, error reporting). Folding index/compare in makes the copy step informed: it starts by knowing exactly what's missing on the destination.

**Do not start until:** hash_index_builder and hash_compare_report land (their primitives are this task's building blocks).

---

## Acceptance Criteria

- [ ] New step in the wizard: pick destination index (server master or another device) → preflight shows "already on destination / missing" before any copying
- [ ] Copy plan derived from the diff: only missing files queued, respecting existing shot-list/copy-all modes as filters on top
- [ ] After Verify Transfer passes, destination index is updated (post_copy_index_update) and the source index is refreshed for the copied paths
- [ ] Same never-delete guarantee: moves between drives remain deliberate, per-batch, hash-verified
- [ ] Single progress story across phases (scan bar → compare bar → copy bar → verify bar) in the existing step-card UI

---

## Technical Notes

- Reuse copy engine untouched underneath; the diff result is just a pre-filtered file list for it
- This is the "hybrid backup tool" UX the user described — tree-compare-aware, unlike Dropbox-style sync
