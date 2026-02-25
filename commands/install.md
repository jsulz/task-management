---
description: Validate vault structure for task management plugin
---

# install

Validate that the Obsidian vault is properly configured for the task management plugin.

## Process

Run the install validation script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/install-check.py
```

The script checks:
1. Config file exists at `~/.claude/task-management-config/config.yaml`
2. Vault root path from config exists
3. Required folders exist: `notes/daily/`, `notes/weekly/`, `notes/tasks/`, `notes/tasks/completed/`
4. Required templates exist: `templates/Task.md`, `templates/Daily.md`, `templates/Weekly.md`
5. `Daily.md` and `Weekly.md` contain `## Tasks` heading

## Output

On success:
```
Task Management Install Check
==============================

✓ Config file exists
✓ Vault root exists: /path/to/vault
✓ notes/daily/ exists
✓ notes/weekly/ exists
✓ notes/tasks/ exists
✓ notes/tasks/completed/ exists
✓ templates/Task.md exists
✓ templates/Daily.md exists (## Tasks heading found)
✓ templates/Weekly.md exists (## Tasks heading found)

All checks passed. Plugin is ready to use.
```

On failure, report which checks failed and offer to create missing folders (but not templates).
