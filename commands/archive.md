---
description: Archive completed one-time tasks to completed/ folder
---

# archive

Archive completed one-time tasks from `notes/tasks/` to `notes/tasks/completed/`.

## Process

Run the archive script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/archive-tasks.py
```

The script will:
1. Find all files in `notes/tasks/` with a `completed:` field
2. Exclude files with a `recurrence:` field (recurring tasks are never archived)
3. Move matching files to `notes/tasks/completed/`

## Output

```
Archived 3 task(s) to completed/:
- [[task-one]]
- [[task-two]]
- [[task-three]]
```

If nothing to archive: `No completed tasks to archive.`
