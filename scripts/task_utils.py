#!/usr/bin/env python3
"""Shared utilities for task management scripts."""

import re
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

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
    generated = config.get('generated_files', {})

    return {
        'vault_root': vault_root,
        'tasks': vault_root / folders.get('tasks', 'notes/tasks'),
        'completed': vault_root / folders.get('completed', 'notes/tasks/completed'),
        'daily': vault_root / folders.get('daily', 'notes/daily'),
        'weekly': vault_root / folders.get('weekly', 'notes/weekly'),
        'templates': vault_root / folders.get('templates', 'templates'),
        'today_file': vault_root / generated.get('today', 'notes/today.md'),
        'this_week_file': vault_root / generated.get('this_week', 'notes/this-week.md'),
        'next_week_file': vault_root / generated.get('next_week', 'notes/next-week.md'),
    }


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2].lstrip('\n')
        return frontmatter, body
    except yaml.YAMLError:
        return {}, content


def normalize_date(date_val) -> str | None:
    """Normalize a date value to YYYY-MM-DD format."""
    if date_val is None:
        return None

    if isinstance(date_val, datetime):
        return date_val.strftime('%Y-%m-%d')

    date_str = str(date_val).strip()

    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    formats = ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


def get_task_name(file_path: Path) -> str:
    """Get task name (filename without extension) for wiki-link."""
    return file_path.stem


def get_week_bounds(date: datetime) -> tuple[datetime, datetime]:
    """Get Sunday-Saturday bounds for the week containing the given date."""
    days_since_sunday = date.weekday() + 1
    if date.weekday() == 6:  # Sunday
        days_since_sunday = 0
    sunday = date - timedelta(days=days_since_sunday)
    saturday = sunday + timedelta(days=6)
    return sunday, saturday


def scan_tasks(tasks_dir: Path) -> list[dict]:
    """Scan all task files and return task info."""
    tasks = []

    if not tasks_dir.exists():
        return tasks

    for task_file in tasks_dir.glob('*.md'):
        content = task_file.read_text()
        frontmatter, body = parse_frontmatter(content)

        due = normalize_date(frontmatter.get('due'))
        completed = normalize_date(frontmatter.get('completed'))
        recurrence = frontmatter.get('recurrence')

        tasks.append({
            'path': task_file,
            'name': get_task_name(task_file),
            'due': due,
            'completed': completed,
            'recurrence': recurrence,
            'frontmatter': frontmatter,
            'body': body,
            'content': content,
        })

    return tasks


def format_date_heading(date: datetime) -> str:
    """Format date for section heading: 'DayOfWeek, Month Day'."""
    return date.strftime('%A, %B %-d')


def format_date_short(date: datetime) -> str:
    """Format date for title: 'Month Day'."""
    return date.strftime('%B %-d')


def generate_this_week_md(tasks: list[dict], today: datetime, output_path: Path) -> dict:
    """Generate this-week.md file. Returns stats."""
    _, saturday = get_week_bounds(today)
    tomorrow = today + timedelta(days=1)

    tasks_by_day = defaultdict(list)
    today_str = today.strftime('%Y-%m-%d')
    saturday_str = saturday.strftime('%Y-%m-%d')

    for task in tasks:
        if not task['due'] or task['completed']:
            continue

        if task['due'] > today_str and task['due'] <= saturday_str:
            tasks_by_day[task['due']].append(task)

    lines = [
        '---',
        f"week_start: {tomorrow.strftime('%Y-%m-%d')}",
        f"week_end: {saturday_str}",
        '---',
        f"# This Week — Week ending {format_date_short(saturday)}",
        '',
    ]

    total_tasks = 0
    current = tomorrow
    while current <= saturday:
        date_str = current.strftime('%Y-%m-%d')
        if date_str in tasks_by_day:
            day_tasks = sorted(tasks_by_day[date_str], key=lambda t: t['name'])
            lines.append(f"## {format_date_heading(current)}")
            for task in day_tasks:
                lines.append(f"- [ ] [[{task['name']}]]")
            lines.append('')
            total_tasks += len(day_tasks)
        current += timedelta(days=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines))

    return {'total': total_tasks}


def generate_next_week_md(tasks: list[dict], today: datetime, output_path: Path) -> dict:
    """Generate next-week.md file. Returns stats."""
    _, this_saturday = get_week_bounds(today)
    next_sunday = this_saturday + timedelta(days=1)
    next_saturday = next_sunday + timedelta(days=6)

    tasks_by_day = defaultdict(list)
    next_sunday_str = next_sunday.strftime('%Y-%m-%d')
    next_saturday_str = next_saturday.strftime('%Y-%m-%d')

    for task in tasks:
        if not task['due'] or task['completed']:
            continue

        if task['due'] >= next_sunday_str and task['due'] <= next_saturday_str:
            tasks_by_day[task['due']].append(task)

    lines = [
        '---',
        f"week_start: {next_sunday_str}",
        f"week_end: {next_saturday_str}",
        '---',
        f"# Next Week — Week of {format_date_short(next_sunday)}",
        '',
    ]

    total_tasks = 0
    current = next_sunday
    while current <= next_saturday:
        date_str = current.strftime('%Y-%m-%d')
        if date_str in tasks_by_day:
            day_tasks = sorted(tasks_by_day[date_str], key=lambda t: t['name'])
            lines.append(f"## {format_date_heading(current)}")
            for task in day_tasks:
                lines.append(f"- [ ] [[{task['name']}]]")
            lines.append('')
            total_tasks += len(day_tasks)
        current += timedelta(days=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines))

    return {'total': total_tasks}
