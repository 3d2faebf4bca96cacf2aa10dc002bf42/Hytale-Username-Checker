#!/usr/bin/env python3
"""
Hytale Username Checker
=======================

A fast, multi-threaded tool to check Hytale username availability.

Usage:
    python main.py

Author: github.com/yourusername
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src import Display, UsernameChecker, Config


def main() -> int:
    """Main entry point."""
    display = Display()
    base_dir = Path(__file__).parent

    display.banner()

    # Load configuration
    config = Config(base_dir / "config.json")

    # Validate input file
    input_file = base_dir / "data" / "usernames.txt"
    if not input_file.exists() or input_file.stat().st_size == 0:
        display.error("Input file not found or empty")
        display.info("Add usernames to data/usernames.txt")
        input_file.parent.mkdir(exist_ok=True)
        input_file.write_text("# Add usernames here (one per line)\n")
        return 1

    # Run checker
    checker = UsernameChecker(config, display, base_dir)

    try:
        checker.run(input_file)
    except KeyboardInterrupt:
        print()
        display.warning("Interrupted by user")
        return 130
    except Exception as e:
        display.error(str(e))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
