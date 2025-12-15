"""Configuration management."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class Config:
    """Application configuration with defaults."""

    threads: int = 3
    timeout: int = 10
    retries: int = 5
    retry_delay: float = 10.0
    debug: bool = False

    def __init__(self, path: Path = None):
        """Load configuration from file if exists."""
        defaults = {
            "threads": 3,
            "timeout": 10,
            "retries": 5,
            "retry_delay": 10.0,
            "debug": False,
        }

        if path and path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    defaults.update(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass

        for key, value in defaults.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "threads": self.threads,
            "timeout": self.timeout,
            "retries": self.retries,
            "retry_delay": self.retry_delay,
            "debug": self.debug,
        }
