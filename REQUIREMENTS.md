# Task Management Plugin — Requirements

A Claude Code plugin for markdown-based task management inside an Obsidian vault. Generates daily/weekly task views, syncs tasks into daily and weekly notes, archives completed tasks, and handles recurring tasks.

## Project Structure

```
task-management/
├── CLAUDE.md               # Claude Code project instructions
├── REQUIREMENTS.md         # This file — source of truth for what to build
├── README.md               # Plugin documentation (generated as part of build)
├── SKILL.md                # manage-tasks skill definition
├── scripts/                # Python scripts for date calc, file generation, etc.
├── commands/               # Slash command .md files
│   ├── today.md
│   ├── this-week.md
│   ├── next-week.md
│   ├── archive.md
│   ├── install.md
│   └── about.md
└── reference/              # Existing plugin for structural reference (do not deploy)
    ├── README.md
    ├── SKILL.md
    ├── about.md
    ├── archive.md
    ├── today.md
    ├── this-week.md
    ├── next-week.md
    ├── setup.md
    ├── clean-imports.md
    └── ideas.md
```

### Reference files

The `reference/` directory contains an existing Claude Code plugin with a similar architecture. Use it as a **structural reference** for how Claude Code plugins work — slash command `.md` files with YAML frontmatter (`description`, `allowed-tools`), skill files, Python scripts called via `${CLAUDE_PLUGIN_ROOT}`, and config file patterns. Do **not** copy its features directly; follow this requirements doc for the actual spec.

## Build Plan

Build one command at a time in this order:

1. **`/tasks:install`** — Validates vault structure. Everything else depends on this.
2. **`/tasks:today`** — The core command. Generates `today.md`, `this-week.md`, `next-week.md` and syncs to daily/weekly notes.
3. **`/tasks:archive`** — Archives completed one-time tasks.
4. **`/tasks:this-week`** — Standalone regeneration of `this-week.md`.
5. **`/tasks:next-week`** — Standalone regeneration of `next-week.md`.
6. **`/tasks:about`** — Documentation viewer.
7. **`manage-tasks` skill** — Skill file for consistent task creation/modification.
8. **`README.md`** — Plugin documentation.

Test each command before moving to the next.

## Vault Structure

The plugin operates within an Obsidian vault with the following structure:

```
vault/
├── notes/
│   ├── daily/              # Daily notes (YYYY-MM-DD.md)
│   ├── weekly/             # Weekly notes (YYYY-MM-DD.md, dated by Sunday)
│   ├── tasks/              # All task files
│   │   └── completed/      # Archived one-time tasks
│   ├── today.md            # Generated — tasks due today + overdue
│   ├── this-week.md        # Generated — remaining tasks this week
│   └── next-week.md        # Generated — tasks for next week
└── templates/
    ├── Task.md             # Template for new task files
    ├── Daily.md            # Template for daily notes (has ## Tasks heading)
    └── Weekly.md           # Template for weekly notes (has ## Tasks heading)
```

### Key conventions

- All files are Markdown (`.md`).
- All links use Obsidian wiki-link format: `[[task-name]]`.
- The week starts on **Sunday**.
- Weekly note filenames use the **Sunday** date of that week (`YYYY-MM-DD.md`).
- Daily note filenames use the date of that day (`YYYY-MM-DD.md`).

## Task File Format

Each task is a Markdown file in `notes/tasks/` with YAML frontmatter:

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

### Required fields

- `due` — Due date in `YYYY-MM-DD` format.

### Optional fields

- `tags` — List of categorization tags (lowercase, hyphenated for multi-word).
- `completed` — Date the task was completed (`YYYY-MM-DD`). Triggers archival for one-time tasks.
- `recurrence` — One of: `weekly`, `biweekly`, `monthly`, `quarterly`, `yearly`.
- `recurrence_day` — Day of month/week for recurring tasks (numeric).

### Task text formatting

When a user provides task content, preserve their exact text. Do not alter capitalization, punctuation, line breaks, or add formatting they didn't include.

## Recurring Tasks

Recurring tasks stay in `notes/tasks/` permanently and are never archived. They include:

- `recurrence` and `recurrence_day` fields in frontmatter.
- An `## Instructions` section explaining how to update when complete.
- A `## History` section logging completion dates.

When a recurring task is completed:

1. Update the `due:` field to the next occurrence date.
2. Append the completion date to the `## History` section.
3. Do **not** add a `completed:` field.
4. Do **not** move to `completed/`.

Example:

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

## One-Time Tasks

When a one-time task is completed:

1. Add `completed: YYYY-MM-DD` to frontmatter.
2. Move the file from `notes/tasks/` to `notes/tasks/completed/`.

## Commands

### `/tasks:today`

Generate `today.md`, `this-week.md`, and `next-week.md`, then sync tasks into the daily and weekly Obsidian notes.

#### Process

1. **Normalize dates** — Scan all files in `notes/tasks/` and ensure `due:` values use `YYYY-MM-DD` with leading zeros.
2. **Archive completed tasks** — Move any file in `notes/tasks/` that has a `completed:` field (and no `recurrence:` field) to `notes/tasks/completed/`.
3. **Calculate dates** — Determine today's date, this week's Sunday–Saturday range, and next week's Sunday–Saturday range.
4. **Generate `notes/today.md`**:
   - YAML frontmatter: `date: YYYY-MM-DD`
   - Heading: `# Today — [DayOfWeek], [Month Day]`
   - `## Overdue` — Tasks with `due:` before today (show due date in parentheses).
   - `## Due Today` — Tasks with `due:` equal to today.
   - List items as `- [ ] [[task-name]]`.
   - Omit sections that have no tasks.
5. **Generate `notes/this-week.md`**:
   - YAML frontmatter: `week_start` and `week_end` dates.
   - Heading: `# This Week — Week ending [Month Day]`
   - Tasks grouped by day (tomorrow through this Saturday): `## DayOfWeek, [Month Day]`
   - List items as `- [ ] [[task-name]]`.
   - Skip days with no tasks.
   - Exclude today's tasks (those are in `today.md`).
6. **Generate `notes/next-week.md`**:
   - YAML frontmatter: `week_start` and `week_end` dates.
   - Heading: `# Next Week — Week of [Month Day]`
   - Tasks grouped by day (Sunday through Saturday): `## DayOfWeek, [Month Day]`
   - List items as `- [ ] [[task-name]]`.
   - Skip days with no tasks.
7. **Sync to daily note**:
   - Look for `notes/daily/YYYY-MM-DD.md` (today's date).
   - If it doesn't exist, create it using `vault/templates/Daily.md` as the template.
   - Find the `## Tasks` heading in the daily note.
   - **Append** the task list from `today.md` (the Overdue and Due Today items) under `## Tasks`. Do not replace existing content under that heading.
8. **Sync to weekly note**:
   - Determine the current week's Sunday date.
   - Look for `notes/weekly/YYYY-MM-DD.md` (that Sunday's date).
   - If it doesn't exist, create it using `vault/templates/Weekly.md` as the template.
   - Find the `## Tasks` heading in the weekly note.
   - **Append** the task list from `this-week.md` (all remaining-week tasks, grouped by day) under `## Tasks`. Do not replace existing content under that heading.

#### Example `today.md`

```markdown
---
date: 2025-02-01
---
# Today — Saturday, February 1

## Overdue
- [ ] [[old-task]] (due: 2025-01-28)

## Due Today
- [ ] [[submit-report]]
- [ ] [[call-insurance]]
```

#### Example `this-week.md`

```markdown
---
week_start: 2025-02-02
week_end: 2025-02-08
---
# This Week — Week ending February 8

## Monday, February 3
- [ ] [[team-standup]]

## Wednesday, February 5
- [ ] [[quarterly-review]]
```

#### Example `next-week.md`

```markdown
---
week_start: 2025-02-09
week_end: 2025-02-15
---
# Next Week — Week of February 9

## Sunday, February 9
- [ ] [[meal-prep]]

## Tuesday, February 11
- [ ] [[dentist-appointment]]
```

### `/tasks:this-week`

Regenerate only `notes/this-week.md`. Same logic as step 5 of `/tasks:today` but standalone.

### `/tasks:next-week`

Regenerate only `notes/next-week.md`. Same logic as step 6 of `/tasks:today` but standalone.

### `/tasks:archive`

Archive completed one-time tasks from `notes/tasks/` to `notes/tasks/completed/`.

- Find all files in `notes/tasks/` with a `completed:` field and no `recurrence:` field.
- Move them to `notes/tasks/completed/`.
- Summarize what was archived:

```
Archived 3 task(s) to completed/:
- [[task-one]]
- [[task-two]]
- [[task-three]]
```

If nothing to archive: `No completed tasks to archive.`

### `/tasks:install`

Validate that the vault is properly set up for the plugin. This is not an interactive wizard — it checks prerequisites and reports pass/fail.

#### Validation checks

1. **Vault root** — Confirm the configured vault root path exists.
2. **Required folders exist**:
   - `notes/daily/`
   - `notes/weekly/`
   - `notes/tasks/`
   - `notes/tasks/completed/`
3. **Required templates exist**:
   - `templates/Task.md`
   - `templates/Daily.md`
   - `templates/Weekly.md`
4. **Templates contain `## Tasks` heading** — Verify `Daily.md` and `Weekly.md` each contain a `## Tasks` heading.

#### Output

```
Task Management Install Check
==============================

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

If any check fails, report the failure clearly and offer to create missing folders (but not missing templates — the user must provide those).

### `/tasks:about`

Show plugin documentation and usage. Read the plugin's README and present an overview of available commands, task format, and configuration.

## Configuration

Configuration is stored in `~/.claude/task-management-config/config.yaml`:

```yaml
paths:
  vault_root: "/path/to/vault"

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

## Skill: `manage-tasks`

A skill file for Claude Code to reference when creating or modifying task files. Ensures consistent formatting, correct frontmatter fields, and proper file placement.

The skill should encode:

- Task file format (frontmatter fields, required vs. optional).
- File organization rules (where tasks go, when to archive, recurring vs. one-time).
- Recurring task conventions (Instructions section, History section, never archive).
- Text formatting rule: preserve user's exact text, do not reformat.
- Tagging conventions: lowercase, hyphenated, consistent with existing tags.

## Out of Scope

The following features from the reference plugin are explicitly **not** included:

- Ideas tracking (no `ideas/` folder, no `status` field, no `/tasks:ideas` command).
- Bugs tracking (no `bugs/` folder).
- Memories/reference items (no `memories/` folder).
- Import/triage workflow (no `import/` folder, no `/tasks:clean-imports` command).
- Research system integration.
- Interactive setup wizard (replaced by `/tasks:install` validation).
- Markdown link format option (Obsidian wiki-links only).
