# Task Management Plugin

A Claude Code plugin for Obsidian-based personal task management.

## Source of Truth

**REQUIREMENTS.md** is the definitive spec. Read it fully before writing any code. It contains the vault structure, task format, every command's behavior, configuration schema, and the build plan.

## Reference Architecture

`reference/` contains an existing Claude Code plugin with a similar architecture. Study it to understand:

- How slash command `.md` files are structured (YAML frontmatter with `description`, `allowed-tools`, `model`)
- How `${CLAUDE_PLUGIN_ROOT}` is used to reference scripts
- How Python scripts handle date calculation, file generation, and task parsing
- How skill files (SKILL.md) are written

Follow the **patterns** from the reference plugin but implement the **spec** from REQUIREMENTS.md. These are different systems — the reference has ideas, bugs, memories, import, and research features that this plugin does not.

## Build Order

Build and test one command at a time:

1. `/tasks:install` — prereq validation
2. `/tasks:today` — core command (generates today/this-week/next-week, syncs to daily/weekly notes)
3. `/tasks:archive` — completed task archival
4. `/tasks:this-week` — standalone
5. `/tasks:next-week` — standalone
6. `/tasks:about` — documentation
7. `manage-tasks` skill file
8. `README.md`

## Key Design Constraints

- **Obsidian wiki-links only**: `[[task-name]]`, never markdown-style links.
- **Week starts Sunday**: weekly notes are filed by Sunday date.
- **Append, never replace**: when syncing tasks to daily/weekly notes under `## Tasks`, append to existing content.
- **Templates are user-provided**: `Daily.md`, `Weekly.md`, and `Task.md` templates already exist in the vault. The plugin uses them but never creates or modifies them. `/tasks:install` validates they exist.
- **Preserve user text exactly**: no reformatting of task content — capitalization, punctuation, line breaks stay as-is.
- **Recurring tasks never archive**: only one-time tasks with a `completed:` field and no `recurrence:` field get moved to `completed/`.

## Configuration

The plugin reads config from `~/.claude/task-management-config/config.yaml`. See REQUIREMENTS.md for the full schema. The `/tasks:install` command validates the vault but does not interactively configure it — the config file must already exist or be created manually.

## Testing

Before moving to the next command in the build order, verify the current command works against a real or simulated vault structure. Date-dependent logic (overdue detection, week boundaries, recurring task advancement) is the most likely source of bugs — test edge cases around week transitions and month boundaries.
