# Vision — Media Fleet: Copy + Index + Verify across Tailscale-connected devices

> **Date:** 2026-11-03
> **Repos:** photo-file-copier (client/copy side) · drive-index (server/dashboard side)
> **Problem:** Consumer sync tools (Dropbox et al.) replicate folders but can't compare file trees by content and can't express our workflow: selective copy from cards/drives → date+type organization → provable verification that everything reached the server. Nothing off the shelf does tree-diff verification on our terms.

---

## Concept

One mental model across the whole fleet:

**Every device is either a SOURCE (has files), a DESTINATION (holds the canonical copy), or both. All devices talk to one dashboard on the server over Tailscale.**

- The **server dashboard** (drive-index, already on the QNAP) becomes the fleet's index hub: it holds per-device indexes, not just the server's own master index.
- Each device runs a small **agent** (evolution of the local scanner) that periodically indexes its attached media volumes and **reports to the dashboard** — pushing its scan JSON (later: SQLite deltas) over HTTPS through the tailnet. No tunnels to expose, no cloud.
- The dashboard renders **tree comparisons between any two indexes** (drive vs server, MacBook vs NAS, card vs drive) — not just drive-vs-server.
- **photo_copier's copy engine folds in as the action layer**: once a compare shows what's missing where, a copy/move job runs with the existing date+type organization, progress bars, and Verify-Transfer-before-erase guarantees — and records the result back into both indexes.

## Why this beats Dropbox-style sync for this use case

| | Sync tools | This |
|---|---|---|
| Compare | live file watch, opaque | periodic full-tree diff, inspectable, reportable |
| Organization | mirrors source layout | date + file-type organization at ingest |
| Copy selection | all-or-nothing | shot-number / file-list selects (photo_copier today) |
| Deletion semantics | syncs deletions (dangerous) | verify-only; deletion is always deliberate |
| Verification | assumed | hash-evidenced, per-file |

## Device roles

- **QNAP (destination):** dashboard + master index + cron re-index (Sunday 3 AM).
- **Mac mini (operator):** photo_copier with integrated scan + compare; the workstation where jobs get driven.
- **MacBook (source, intermittent):** agent scans on wake/connect, reports to dashboard when reachable via Tailscale.
- **Removable drives/cards (sources):** indexed on plug-in, same scan pipeline.

## Feature list (fleet phase)

- **F6 — Dashboard API:** authenticated endpoint (API key per device) to accept index reports; store per-device indexes; serve compare results between any pair.
- **F7 — Device agent:** periodic index + report (configurable interval / on volume-mount), resilient to being offline (queues last scan, reports when back).
- **F8 — Unified flow in photo_copier:** Scan → Compare → Copy (with existing organization) → Verify → Update indexes, one wizard instead of 4 tools.
- **F9 — Fleet dashboard:** device list with last-seen, index freshness, and storage health (per-share capacity feeds the consolidation epic).

## Ordering with existing tasks

Builds on: hash_index_builder, hash_compare_report, full_hash_verification_column, container_recovery_weekly_cron. Fleet work (F6–F9) comes after those land — the single-node flow must be solid before it multiplies across devices.
