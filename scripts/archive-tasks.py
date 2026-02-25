#!/usr/bin/env python3
"""Archive completed one-time tasks to completed/ folder."""

import shutil
import yaml
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude" / "task-management-config" / "config.yaml"


def load_config():
    """Load configuration from config file."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_paths(config):
    """Extract paths from config."""
    vault_root = Path(config['paths']['vault_root']).expanduser()
    folders = config.get('folders', {})

    return {
        'vault_root': vault_root,
        'tasks': vault_root / folders.get('tasks', 'notes/tasks'),
        'completed': vault_root / folders.get('completed', 'notes/tasks/completed'),
    }


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def main():
    config = load_config()
    paths = get_paths(config)

    tasks_dir = paths['tasks']
    completed_dir = paths['completed']

    if not tasks_dir.exists():
        print("No tasks folder found.")
        return

    completed_dir.mkdir(parents=True, exist_ok=True)

    archived = []

    for task_file in tasks_dir.glob('*.md'):
        content = task_file.read_text()
        frontmatter = parse_frontmatter(content)

        has_completed = frontmatter.get('completed') is not None
        has_recurrence = frontmatter.get('recurrence') is not None

        # Only archive if completed and NOT recurring
        if has_completed and not has_recurrence:
            dest = completed_dir / task_file.name
            shutil.move(str(task_file), str(dest))
            archived.append(task_file.stem)

    if archived:
        print(f"Archived {len(archived)} task(s) to completed/:")
        for name in archived:
            print(f"- [[{name}]]")
    else:
        print("No completed tasks to archive.")


if __name__ == "__main__":
    main()
