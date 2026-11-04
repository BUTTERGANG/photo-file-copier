---
status: backlog
priority: P3
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Dashboard Report API + Device Agents (Fleet Indexing)

> **Repo:** photo-file-copier / drive-index
> **Vision ref:** SCRUM/AGENT_FLEET_VISION.md — F6, F7, F9
> **Description:** Every Tailscale-connected device periodically reports its media indexes to the dashboard on the server.

---

## Context

All devices (Mac mini, MacBook, QNAP) are on the same tailnet, so the dashboard is reachable from everywhere without exposing anything publicly. Today the dashboard accepts a manually uploaded scan JSON; the fleet phase turns that into automated periodic reporting so indexes stay fresh without anyone remembering to scan.

**Do not start until:** container_recovery_weekly_cron lands (dashboard must be running), hash_index_builder + hash_compare_report land (single-node flow first).

---

## Acceptance Criteria

- [ ] POST /api/report endpoint with per-device API keys (device registers itself, key shown once)
- [ ] Agent on each device: index attached media volumes on a schedule and/or on volume mount; push scan to dashboard; queue-and-retry when offline
- [ ] Dashboard stores one index per device + the server's own master index
- [ ] Compare any pair of indexes from the dashboard UI (not just drive-vs-server)
- [ ] Fleet status page: devices, last-seen, index age, file/byte counts; flags stale indexes
- [ ] Bandwidth-conscious: send deltas (new/changed paths only) once an index baseline exists on the server

---

## Technical Notes

- Keep the manual scan-JSON upload working — the agent is a producer of the same JSON, not a new format (until the delta upgrade)
- Static API keys in an SQLite table are fine at this scale; no OAuth
- MacBook agent should be launchd-based, cheap on battery (hashing only new/changed files)
