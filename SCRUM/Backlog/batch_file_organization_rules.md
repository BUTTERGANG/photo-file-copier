---
status: backlog
priority: P2
agent_claimed: null
claimed_at: null
updated: 2026-08-20
---

# Batch File Organization Rules

> **Repo:** photo-file-copier
> **Description:** Configure camera import with auto-sort rules by date, event, and camera

---

## Context

Core feature — define rules for how imported photos are organized: by date taken, by event folder, by camera model, with custom naming conventions.

---

## Acceptance Criteria

- [ ] Rule editor UI with drag-and-drop priority ordering
- [ ] Date-based folder structure (YYYY/MM-DD or YYYY-MM-DD_Event)
- [ ] Camera model auto-detection from EXIF for subfolder sorting
- [ ] Dry-run preview showing where files would land before copying

---

## Technical Notes

- EXIF parsing with Pillow/exiftool; file system operations with conflict resolution; YAML rule config file
