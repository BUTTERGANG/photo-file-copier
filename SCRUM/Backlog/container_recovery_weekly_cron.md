---
status: backlog
priority: P1
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Container Station Recovery + Weekly Server Re-index Cron

> **Repo:** photo-file-copier / drive-index
> **Description:** Bring the NAS Docker daemon back up and schedule the incremental server index rebuild for early Sunday morning.

---

## Context

The drive-index dashboard runs as a Docker container on the QNAP, but the Docker daemon is currently down (`Cannot connect to unix:///var/run/docker.sock`; binary at `/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker`). Until it runs, neither the dashboard nor any scheduled index rebuild works. The server index is stale (last built Sep 5; ~2 months of new files missing).

User wants a recurring early-Sunday (3–4 AM) incremental re-index that only hashes new/changed files. Incremental cost is small (typical weekly delta reads in minutes); the Sep 5 full pass took ~17.3 h, so never schedule full rebuilds.

---

## Acceptance Criteria

- [ ] Container Station service started and verified (`docker ps` works over SSH)
- [ ] drive-index container running and dashboard reachable on the tailnet
- [ ] Weekly cron inside the container (or QTS scheduler) runs `build_index.py` Sunday ~3 AM against the media roots
- [ ] Cron logs to a file with the standard completion line (new/changed, reused, removed) and survives reboots
- [ ] One-off catch-up: first run rebuilds the 2 months of drift (mostly incremental over 1.44M known files — should stay well under the 17 h baseline)

---

## Technical Notes

- `docker-compose.yml` mounts placeholders for media paths — verify they match actual roots before first cron run
- Do not schedule anything that competes with the Sunday 2 AM backup job the user already runs
