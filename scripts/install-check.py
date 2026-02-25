#!/usr/bin/env python3
"""Validate vault structure for task management plugin."""

import os
import sys
import yaml
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude" / "task-management-config" / "config.yaml"

def load_config():
    """Load configuration from config file."""
    if not CONFIG_PATH.exists():
        return None
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def check_folder(vault_root: Path, folder: str) -> bool:
    """Check if a folder exists."""
    return (vault_root / folder).is_dir()

def check_template(vault_root: Path, template: str, check_tasks_heading: bool = False) -> tuple[bool, bool]:
    """Check if a template exists and optionally contains ## Tasks heading."""
    template_path = vault_root / template
    if not template_path.is_file():
        return False, False

    if check_tasks_heading:
        content = template_path.read_text()
        has_heading = "## Tasks" in content
        return True, has_heading

    return True, True

def main():
    print("Task Management Install Check")
    print("=" * 30)
    print()

    all_passed = True
    missing_folders = []

    # Check config file
    if not CONFIG_PATH.exists():
        print(f"✗ Config file not found: {CONFIG_PATH}")
        print()
        print("Create the config file with:")
        print(f"  mkdir -p {CONFIG_PATH.parent}")
        print(f"  # Then create {CONFIG_PATH} with vault_root path")
        sys.exit(1)
    else:
        print(f"✓ Config file exists")

    config = load_config()
    if not config:
        print("✗ Config file is empty or invalid")
        sys.exit(1)

    # Get vault root
    vault_root_str = config.get('paths', {}).get('vault_root')
    if not vault_root_str:
        print("✗ vault_root not configured in config file")
        sys.exit(1)

    vault_root = Path(vault_root_str).expanduser()

    # Check vault root exists
    if not vault_root.is_dir():
        print(f"✗ Vault root does not exist: {vault_root}")
        all_passed = False
    else:
        print(f"✓ Vault root exists: {vault_root}")

    # Get folder paths from config (with defaults)
    folders_config = config.get('folders', {})
    daily_folder = folders_config.get('daily', 'notes/daily')
    weekly_folder = folders_config.get('weekly', 'notes/weekly')
    tasks_folder = folders_config.get('tasks', 'notes/tasks')
    completed_folder = folders_config.get('completed', 'notes/tasks/completed')
    templates_folder = folders_config.get('templates', 'templates')

    # Check required folders
    required_folders = [
        (daily_folder, "notes/daily/"),
        (weekly_folder, "notes/weekly/"),
        (tasks_folder, "notes/tasks/"),
        (completed_folder, "notes/tasks/completed/"),
    ]

    for folder, display_name in required_folders:
        if check_folder(vault_root, folder):
            print(f"✓ {display_name} exists")
        else:
            print(f"✗ {display_name} does not exist")
            all_passed = False
            missing_folders.append(folder)

    # Check templates
    templates = [
        (f"{templates_folder}/Task.md", "templates/Task.md", False),
        (f"{templates_folder}/Daily.md", "templates/Daily.md", True),
        (f"{templates_folder}/Weekly.md", "templates/Weekly.md", True),
    ]

    for template, display_name, check_heading in templates:
        exists, has_heading = check_template(vault_root, template, check_heading)
        if not exists:
            print(f"✗ {display_name} does not exist")
            all_passed = False
        elif check_heading and not has_heading:
            print(f"✗ {display_name} exists but missing ## Tasks heading")
            all_passed = False
        elif check_heading:
            print(f"✓ {display_name} exists (## Tasks heading found)")
        else:
            print(f"✓ {display_name} exists")

    print()

    if all_passed:
        print("All checks passed. Plugin is ready to use.")
        sys.exit(0)
    else:
        print("Some checks failed.")
        if missing_folders:
            print()
            print("Missing folders can be created with:")
            for folder in missing_folders:
                print(f"  mkdir -p \"{vault_root / folder}\"")
        print()
        print("Note: Templates must be created manually by the user.")
        sys.exit(1)

if __name__ == "__main__":
    main()
