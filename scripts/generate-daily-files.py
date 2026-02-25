#!/usr/bin/env python3
"""Generate today.md, this-week.md, next-week.md and sync to daily/weekly notes."""

import os
import re
import shutil
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

    # Already in correct format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # Try parsing various formats
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
    # Find Sunday (start of week)
    days_since_sunday = date.weekday() + 1  # Monday=0, so Sunday=6+1=7, but we want 0
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


def normalize_task_dates(tasks: list[dict]) -> int:
    """Normalize dates in task files. Returns count of files updated."""
    updated = 0

    for task in tasks:
        frontmatter = task['frontmatter']
        original_due = frontmatter.get('due')
        normalized_due = task['due']

        if original_due is not None and str(original_due) != normalized_due:
            # Need to update the file
            frontmatter['due'] = normalized_due
            new_content = '---\n' + yaml.dump(frontmatter, default_flow_style=False) + '---\n' + task['body']
            task['path'].write_text(new_content)
            updated += 1

    return updated


def archive_completed_tasks(tasks: list[dict], completed_dir: Path) -> list[str]:
    """Move completed one-time tasks to completed folder. Returns list of archived task names."""
    archived = []

    completed_dir.mkdir(parents=True, exist_ok=True)

    for task in tasks:
        # Only archive if has completed date and no recurrence
        if task['completed'] and not task['recurrence']:
            dest = completed_dir / task['path'].name
            shutil.move(str(task['path']), str(dest))
            archived.append(task['name'])

    return archived


def format_date_heading(date: datetime) -> str:
    """Format date for section heading: 'DayOfWeek, Month Day'."""
    return date.strftime('%A, %B %-d')


def format_date_short(date: datetime) -> str:
    """Format date for title: 'Month Day'."""
    return date.strftime('%B %-d')


def generate_today_md(tasks: list[dict], today: datetime, output_path: Path) -> dict:
    """Generate today.md file. Returns stats."""
    overdue = []
    due_today = []

    today_str = today.strftime('%Y-%m-%d')

    for task in tasks:
        if not task['due'] or task['completed']:
            continue

        if task['due'] < today_str:
            overdue.append(task)
        elif task['due'] == today_str:
            due_today.append(task)

    # Sort by due date, then name
    overdue.sort(key=lambda t: (t['due'], t['name']))
    due_today.sort(key=lambda t: t['name'])

    # Build content
    lines = [
        '---',
        f"date: {today_str}",
        '---',
        f"# Today — {format_date_heading(today)}",
        '',
    ]

    if overdue:
        lines.append('## Overdue')
        for task in overdue:
            lines.append(f"- [ ] [[{task['name']}]] (due: {task['due']})")
        lines.append('')

    if due_today:
        lines.append('## Due Today')
        for task in due_today:
            lines.append(f"- [ ] [[{task['name']}]]")
        lines.append('')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines))

    return {'overdue': len(overdue), 'due_today': len(due_today)}


def generate_this_week_md(tasks: list[dict], today: datetime, output_path: Path) -> dict:
    """Generate this-week.md file. Returns stats."""
    _, saturday = get_week_bounds(today)

    # Find next week's Sunday for week_start (tomorrow through Saturday)
    tomorrow = today + timedelta(days=1)

    # Group tasks by day (tomorrow through this Saturday)
    tasks_by_day = defaultdict(list)
    today_str = today.strftime('%Y-%m-%d')
    saturday_str = saturday.strftime('%Y-%m-%d')

    for task in tasks:
        if not task['due'] or task['completed']:
            continue

        # Only include tasks after today and up to Saturday
        if task['due'] > today_str and task['due'] <= saturday_str:
            tasks_by_day[task['due']].append(task)

    # Build content
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

    # Group tasks by day
    tasks_by_day = defaultdict(list)
    next_sunday_str = next_sunday.strftime('%Y-%m-%d')
    next_saturday_str = next_saturday.strftime('%Y-%m-%d')

    for task in tasks:
        if not task['due'] or task['completed']:
            continue

        if task['due'] >= next_sunday_str and task['due'] <= next_saturday_str:
            tasks_by_day[task['due']].append(task)

    # Build content
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


def extract_task_list(generated_file: Path) -> str:
    """Extract the task list content (without frontmatter/title) from a generated file."""
    if not generated_file.exists():
        return ''

    content = generated_file.read_text()
    _, body = parse_frontmatter(content)

    # Remove the main title line
    lines = body.split('\n')
    result_lines = []
    skip_title = True

    for line in lines:
        if skip_title and line.startswith('# '):
            skip_title = False
            continue
        result_lines.append(line)

    return '\n'.join(result_lines).strip()


def sync_to_daily_note(paths: dict, today: datetime):
    """Sync today's tasks to daily note."""
    daily_file = paths['daily'] / f"{today.strftime('%Y-%m-%d')}.md"
    template_file = paths['templates'] / 'Daily.md'

    # Create from template if doesn't exist
    if not daily_file.exists():
        if template_file.exists():
            template_content = template_file.read_text()
            # Replace template date placeholder if present
            template_content = template_content.replace('{{date}}', today.strftime('%Y-%m-%d'))
            daily_file.parent.mkdir(parents=True, exist_ok=True)
            daily_file.write_text(template_content)
        else:
            # Create minimal daily note
            daily_file.parent.mkdir(parents=True, exist_ok=True)
            daily_file.write_text(f"# {today.strftime('%Y-%m-%d')}\n\n## Tasks\n\n")

    # Read current content
    content = daily_file.read_text()

    # Extract task list from today.md
    task_content = extract_task_list(paths['today_file'])

    if not task_content:
        return daily_file

    # Find ## Tasks heading and append
    if '## Tasks' in content:
        # Find the position after ## Tasks
        tasks_idx = content.find('## Tasks')
        # Find the end of that line
        newline_idx = content.find('\n', tasks_idx)
        if newline_idx == -1:
            newline_idx = len(content)

        # Check if task content already exists (avoid duplicates on re-run)
        remaining = content[newline_idx:]
        if task_content.strip() not in remaining:
            # Insert after ## Tasks heading
            new_content = content[:newline_idx + 1] + '\n' + task_content + '\n' + content[newline_idx + 1:]
            daily_file.write_text(new_content)
    else:
        # Append ## Tasks section
        content = content.rstrip() + '\n\n## Tasks\n\n' + task_content + '\n'
        daily_file.write_text(content)

    return daily_file


def sync_to_weekly_note(paths: dict, today: datetime):
    """Sync this week's tasks to weekly note."""
    sunday, _ = get_week_bounds(today)
    weekly_file = paths['weekly'] / f"{sunday.strftime('%Y-%m-%d')}.md"
    template_file = paths['templates'] / 'Weekly.md'

    # Create from template if doesn't exist
    if not weekly_file.exists():
        if template_file.exists():
            template_content = template_file.read_text()
            template_content = template_content.replace('{{date}}', sunday.strftime('%Y-%m-%d'))
            weekly_file.parent.mkdir(parents=True, exist_ok=True)
            weekly_file.write_text(template_content)
        else:
            # Create minimal weekly note
            weekly_file.parent.mkdir(parents=True, exist_ok=True)
            weekly_file.write_text(f"# Week of {sunday.strftime('%Y-%m-%d')}\n\n## Tasks\n\n")

    # Read current content
    content = weekly_file.read_text()

    # Extract task list from this-week.md
    task_content = extract_task_list(paths['this_week_file'])

    if not task_content:
        return weekly_file

    # Find ## Tasks heading and append
    if '## Tasks' in content:
        tasks_idx = content.find('## Tasks')
        newline_idx = content.find('\n', tasks_idx)
        if newline_idx == -1:
            newline_idx = len(content)

        remaining = content[newline_idx:]
        if task_content.strip() not in remaining:
            new_content = content[:newline_idx + 1] + '\n' + task_content + '\n' + content[newline_idx + 1:]
            weekly_file.write_text(new_content)
    else:
        content = content.rstrip() + '\n\n## Tasks\n\n' + task_content + '\n'
        weekly_file.write_text(content)

    return weekly_file


def main():
    config = load_config()
    paths = get_paths(config)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Scan tasks
    tasks = scan_tasks(paths['tasks'])

    # Normalize dates
    normalized = normalize_task_dates(tasks)
    if normalized:
        print(f"Normalized dates in {normalized} file(s)")

    # Archive completed tasks
    archived = archive_completed_tasks(tasks, paths['completed'])
    if archived:
        print(f"Archived {len(archived)} completed task(s)")

    # Re-scan after archiving (to exclude archived tasks)
    tasks = scan_tasks(paths['tasks'])

    # Generate files
    today_stats = generate_today_md(tasks, today, paths['today_file'])
    this_week_stats = generate_this_week_md(tasks, today, paths['this_week_file'])
    next_week_stats = generate_next_week_md(tasks, today, paths['next_week_file'])

    print()
    print("Generated task files:")
    print(f"- today.md: {today_stats['overdue']} overdue, {today_stats['due_today']} due today")
    print(f"- this-week.md: {this_week_stats['total']} tasks")
    print(f"- next-week.md: {next_week_stats['total']} tasks")

    # Sync to daily/weekly notes
    daily_note = sync_to_daily_note(paths, today)
    weekly_note = sync_to_weekly_note(paths, today)

    print()
    print(f"Synced to daily note: {daily_note.relative_to(paths['vault_root'])}")
    print(f"Synced to weekly note: {weekly_note.relative_to(paths['vault_root'])}")


if __name__ == "__main__":
    main()
