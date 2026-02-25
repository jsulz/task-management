---
name: manage-tasks
description: Task conventions and file organization for Obsidian-based task management. Use when creating or modifying task files.
allowed-tools: Read, Edit, Write, Glob, Grep
---

# Task Management Skill

## File Structure

```
vault/
├── notes/
│   ├── daily/              # Daily notes (YYYY-MM-DD.md)
│   ├── weekly/             # Weekly notes (YYYY-MM-DD.md, dated by Sunday)
│   ├── tasks/              # All active task files
│   │   └── completed/      # Archived one-time tasks
│   ├── today.md            # Generated — tasks due today + overdue
│   ├── this-week.md        # Generated — remaining tasks this week
│   └── next-week.md        # Generated — tasks for next week
└── templates/
    ├── Task.md             # Template for new tasks
    ├── Daily.md            # Template for daily notes
    └── Weekly.md           # Template for weekly notes
```

## Task File Format

Each task is a markdown file in `notes/tasks/` with YAML frontmatter:

```yaml
---
due: YYYY-MM-DD
tags:
  - tag1
  - tag2
---
# Task Title

Task content here.
```

### Required Fields

- `due` — Due date in `YYYY-MM-DD` format (with leading zeros)

### Optional Fields

- `tags` — List of categorization tags
- `completed` — Date completed (`YYYY-MM-DD`). Triggers archival for one-time tasks.
- `recurrence` — One of: `weekly`, `biweekly`, `monthly`, `quarterly`, `yearly`
- `recurrence_day` — Day of month/week for recurring tasks (numeric)

## File Organization Rules

### notes/tasks/
- Contains all active tasks (one-time and recurring)
- One-time tasks: When completed, add `completed:` date — they will be archived to `completed/` on next `/tasks:today` run
- Recurring tasks: Stay here permanently, never archived

### notes/tasks/completed/
- Contains finished one-time tasks with `completed:` date
- Keeps active tasks folder clean
- Never put recurring tasks here

## One-Time Tasks

When a one-time task is completed:
1. Add `completed: YYYY-MM-DD` to frontmatter
2. The task will be moved to `notes/tasks/completed/` automatically

## Recurring Tasks

Recurring tasks include:
- `recurrence` and `recurrence_day` fields in frontmatter
- An `## Instructions` section explaining how to update when complete
- A `## History` section to log completion dates
- Never move to `completed/` — stay in `tasks/` permanently

When a recurring task is completed:
1. Update the `due:` date to the next occurrence
2. Add the completion date to the `## History` section
3. Do NOT add a `completed:` field
4. Do NOT move to `completed/`

Example recurring task:
```yaml
---
due: 2025-02-15
recurrence: monthly
recurrence_day: 15
tags:
  - admin
---
# Monthly Report

## Instructions
When completing this task:
1. Update the `due:` date to next month
2. Add completion date to History section

## History
- 2025-01-15: Completed
- 2024-12-15: Completed
```

## Task Creation Guidelines

**CRITICAL: Preserve user's exact text formatting**

When the user provides notes, content, or task details:
- Use their EXACT text — preserve capitalization, punctuation, line breaks exactly as given
- Do NOT capitalize the first letter if they didn't
- Do NOT add periods at the end if they didn't include them
- Do NOT add section headers unless they provided them
- Do NOT reformat or "clean up" their text in any way

### Simple tasks
Just the essentials:
- `due` date (required)
- `tags` (optional)
- Minimal notes

### Complex tasks
Include:
- Checklist section
- Notes section
- Resources/links section (if needed)

### Recurring tasks
Include:
- `recurrence` field
- `recurrence_day` field
- `## Instructions` section
- `## History` section

## Tagging Conventions

- Use semantic tags that describe the task category, context, or project
- Keep tags lowercase
- Use hyphens for multi-word tags (e.g., `home-improvement`)
- Be consistent with existing tags in the vault

## Link Format

Always use Obsidian wiki-link format: `[[task-name]]`

Never use markdown-style links.
