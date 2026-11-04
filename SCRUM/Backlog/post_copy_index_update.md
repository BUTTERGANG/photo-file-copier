---
status: backlog
priority: P2
agent_claimed: null
claimed_at: null
updated: 2026-11-03
---

# Record Copied Files into the Destination Index

> **Repo:** photo-file-copier
> **Feature ref:** SCRUM/FEATURE_LIST_HASH_INDEX.md — F4, F5
> **Description:** After a verified copy, seed/update the destination (server) index so future compares skip re-hashing everything.

---

## Context

After Copy Files + Verify Transfer succeeds, we already know each file's hash. Recording it into the server index means the next compare starts from known-good state — big win since server-wide indexing is slow.

Also covers F5: detect network mounts (QNAP share) vs local volumes, warn on slow paths, remember last-used server root.

---

## Acceptance Criteria

- [ ] Option (on by default) to append copied files' {path, sha256, size, date} entries into the destination index at the end of a verified copy
- [ ] Only files that passed Verify Transfer get recorded
- [ ] Server-root picker with remembered last-used path; network-mount detection with a gentle warning when indexing a slow share
- [ ] No changes to the never-delete guarantee — index update is additive metadata only

---

## Technical Notes

- Reuses hashes computed during Verify Transfer — no re-reading
- Keep `~/.photo_copier.json` prefs pattern for the server root
