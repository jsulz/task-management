#!/usr/bin/env python3
"""Generate this-week.md file."""

import sys
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from task_utils import load_config, get_paths, scan_tasks, generate_this_week_md


def main():
    config = load_config()
    paths = get_paths(config)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    tasks = scan_tasks(paths['tasks'])
    stats = generate_this_week_md(tasks, today, paths['this_week_file'])

    print(f"Generated this-week.md: {stats['total']} tasks")


if __name__ == "__main__":
    main()
