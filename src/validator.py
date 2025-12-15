"""Username validation utilities."""

import re
from pathlib import Path
from typing import List, Set, Tuple


class Validator:
    """Validates usernames according to Hytale rules."""

    # Hytale rules: 3-16 characters, alphanumeric + underscore
    PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,16}$")
    MIN_LENGTH = 3
    MAX_LENGTH = 16

    @classmethod
    def is_valid(cls, username: str) -> bool:
        """Check if username follows Hytale naming rules."""
        return bool(cls.PATTERN.match(username))

    @classmethod
    def load_file(cls, filepath: Path) -> Tuple[List[str], int, int]:
        """
        Load usernames from file.

        Returns:
            Tuple of (valid_usernames, duplicates_removed, invalid_removed)
        """
        seen: Set[str] = set()
        valid: List[str] = []
        duplicates = 0
        invalid = 0

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                username = line.strip()

                # Skip empty lines and comments
                if not username or username.startswith("#"):
                    continue

                # Check duplicate (case-insensitive)
                lower = username.lower()
                if lower in seen:
                    duplicates += 1
                    continue

                # Validate format
                if not cls.is_valid(username):
                    invalid += 1
                    continue

                seen.add(lower)
                valid.append(username)

        return valid, duplicates, invalid
