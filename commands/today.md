---
description: Generate today.md, this-week.md, and next-week.md, then sync to daily/weekly notes
---

# today

Generate daily task files and sync to Obsidian daily/weekly notes.

## Process

Run the generate-daily-files script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate-daily-files.py
```

The script will:
1. Normalize dates in all task files (ensure YYYY-MM-DD format)
2. Archive completed one-time tasks (move to completed/ folder)
3. Calculate today's date and week ranges
4. Generate `notes/today.md` with overdue and due-today tasks
5. Generate `notes/this-week.md` with remaining week tasks (excluding today)
6. Generate `notes/next-week.md` with next week's tasks
7. Sync tasks to daily note (create from template if needed, append under ## Tasks)
8. Sync tasks to weekly note (create from template if needed, append under ## Tasks)

## Example Output

```
Generated task files:
- today.md: 2 overdue, 3 due today
- this-week.md: 5 tasks (Mon-Sat)
- next-week.md: 4 tasks

Synced to daily note: notes/daily/2025-02-01.md
Synced to weekly note: notes/weekly/2025-01-26.md
```
