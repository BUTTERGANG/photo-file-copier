# Feature List — Hash Index & Server Verification

> **Repo:** photo-file-copier
> **Goal:** Index a removable drive and the QNAP server with SHA-256 manifests so we can prove which files made it to the server and which didn't — a verified mirror, not a guess.
> **Date added:** 2026-11-03

---

## Concept

When you target a removable drive to transfer from, the app already tags dates and organizes output by date + file type. We extend that with a **hash index**: every indexed file gets a SHA-256 fingerprint recorded alongside its path, size, and date (created/modified). Comparing the drive index against the server index answers, definitively:

- **Verified on server** — file exists in both indexes with the same hash
- **On drive, not on server** — hasn't been copied yet
- **On server, not on drive** — was moved/deleted from the drive after copy
- **Hash mismatch** — file exists both places but contents differ (corruption, partial copy)

Identity = `(hash, date-bucket)` per the user's direction: date created/modified plus content hash. The hash is the primary key; the date bucket keeps renamed/moved files matchable to their organized destination (`1-2-34/JPG/…` style paths).

## Feature list

### F1 — Index builder (drive or server path)
Walk a target tree and produce a manifest: `{relpath, sha256, size, date_created, date_modified}`.
- **Proper progress bar** like the copy jobs — total file count, files hashed/sec, bytes processed, ETA. Indexing the whole server "takes a minute"; it must feel like the copy flow, not a hang.
- Resumable / incremental: skip unchanged entries on re-index (fast-path by size+mtime, verified by hash only when size or mtime differs).
- Cancel-safe: partial runs never corrupt the stored index.

### F2 — Persistent index storage
Manifests stored per volume/share as a small database (SQLite) beside the app config, keyed by volume identity + root path. Old stale indexes can be rebuilt on demand.

### F3 — Compare report (drive index vs server index)
Step-card UX consistent with existing flow:
- Summary counts (verified / missing-from-server / missing-from-drive / mismatched)
- Drill-down lists per category; export a report (`Save Report…` like `Save Log…`)
- After a compare, a one-line verdict in the same spirit as *"The originals are safe to erase"* — e.g. **"All N selected files verified on the server."**

### F4 — Copy flow integration
After a successful copy + Verify Transfer, optionally record the copied files straight into the destination (server) index so future compares start from known-good state instead of re-hashing everything.

### F5 — Server mount handling
Detect a network mount (QNAP share) vs local volume: warn on slow paths, cap index concurrency sensibly, and remember the last-used server root.

## Deliberately out of scope (first pass)

- Automated deletion/sync — this tool verifies and reports only
- Near-duplicate / perceptual hashing (existing dedup backlog item covers exact-dup UX)
- Non-macOS targets
