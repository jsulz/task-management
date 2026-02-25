# task-management

A Claude Code plugin for markdown-based task management inside an Obsidian vault. Generates daily/weekly task views, syncs tasks into daily and weekly notes, archives completed tasks, and handles recurring tasks.

## Installation

```bash
claude plugins add <plugin-path>/task-management
```

After installation, create the config file and run the install check:

```
/tasks:install
```

## Configuration

Create the config file at `~/.claude/task-management-config/config.yaml`:

```yaml
paths:
  vault_root: "/path/to/your/vault"

folders:
  daily: "notes/daily"
  weekly: "notes/weekly"
  tasks: "notes/tasks"
  completed: "notes/tasks/completed"
  templates: "templates"

generated_files:
  today: "notes/today.md"
  this_week: "notes/this-week.md"
  next_week: "notes/next-week.md"

links:
  format: "obsidian"

week:
  starts_on: "sunday"
```

## Vault Structure

The plugin expects this folder structure in your Obsidian vault:

```
vault/
├── notes/
│   ├── daily/              # Daily notes (YYYY-MM-DD.md)
│   ├── weekly/             # Weekly notes (YYYY-MM-DD.md, dated by Sunday)
│   ├── tasks/              # All task files
│   │   └── completed/      # Archived one-time tasks
│   ├── today.md            # Generated
│   ├── this-week.md        # Generated
│   └── next-week.md        # Generated
└── templates/
    ├── Task.md             # Template for new tasks
    ├── Daily.md            # Template for daily notes (must have ## Tasks heading)
    └── Weekly.md           # Template for weekly notes (must have ## Tasks heading)
```

## Commands

### `/tasks:install`

Validate that the vault is properly configured. Checks:
- Config file exists
- Vault root path exists
- Required folders exist
- Required templates exist
- Templates contain `## Tasks` heading

### `/tasks:today`

Generate daily task files and sync to Obsidian notes:
- `today.md` — Overdue tasks and tasks due today
- `this-week.md` — Tasks for remaining days this week
- `next-week.md` — Tasks for next week

Also:
- Normalizes date formats in task files
- Archives completed one-time tasks
- Creates daily/weekly notes from templates if missing
- Appends task lists under `## Tasks` heading in daily/weekly notes

### `/tasks:this-week`

Regenerate only `this-week.md`.

### `/tasks:next-week`

Regenerate only `next-week.md`.

### `/tasks:archive`

Move completed one-time tasks from `tasks/` to `completed/`. Recurring tasks are never archived.

### `/tasks:about`

Show this documentation.

## Task File Format

Each task is a markdown file with YAML frontmatter:

```yaml
---
due: 2025-02-15
tags:
  - project
  - urgent
---
# Task Title

Task content here.
```

### Fields

**Required:**
- `due` — Due date in `YYYY-MM-DD` format

**Optional:**
- `tags` — List of categorization tags
- `completed` — Completion date (triggers archival)
- `recurrence` — `weekly`, `biweekly`, `monthly`, `quarterly`, or `yearly`
- `recurrence_day` — Day number for recurring tasks

## Recurring Tasks

Recurring tasks stay in `tasks/` permanently and include:
- `recurrence` and `recurrence_day` fields
- An `## Instructions` section
- A `## History` section for logging completions

When completed, update the `due:` date and add to History — do not add `completed:` field.

## Skills

### `manage-tasks`

Task conventions and file organization rules. Use this skill when creating or modifying task files to ensure consistent formatting.

Add to your vault's CLAUDE.md: "Use the manage-tasks skill whenever creating or updating tasks."

## Key Conventions

- **Obsidian wiki-links only**: `[[task-name]]`
- **Week starts Sunday**: Weekly notes filed by Sunday date
- **Append, never replace**: Task lists are appended under `## Tasks`, not replaced
- **Templates are user-provided**: The plugin uses but never creates templates
- **Preserve user text exactly**: No reformatting of task content

## License

MIT
