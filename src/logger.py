"""Professional structured logging system."""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class Logger:
    """Thread-safe file logger with structured output."""

    def __init__(self, log_dir: Path, debug: bool = False):
        self.debug_mode = debug
        self.lock = threading.Lock()

        # Setup log directory and file
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = log_dir / f"session_{timestamp}.log"

        self._write_header()

    def _write_header(self) -> None:
        """Write session header."""
        now = datetime.now()
        lines = [
            "=" * 70,
            f"  SESSION STARTED",
            f"  {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
        ]
        self._write_raw("\n".join(lines))

    def _write_raw(self, text: str) -> None:
        """Write raw text to log file."""
        with self.lock:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(text + "\n")

    def _format(self, level: str, msg: str, data: Optional[Dict] = None) -> str:
        """Format log entry."""
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{ts}] [{level:>5}] {msg}"

        if data:
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            indented = "\n".join(f"                {line}" for line in formatted.split("\n"))
            entry += f"\n{indented}"

        return entry

    def debug(self, msg: str, data: Optional[Dict] = None) -> None:
        """Log debug message (only in debug mode)."""
        if self.debug_mode:
            self._write_raw(self._format("DEBUG", msg, data))

    def info(self, msg: str, data: Optional[Dict] = None) -> None:
        """Log info message."""
        self._write_raw(self._format("INFO", msg, data))

    def warn(self, msg: str, data: Optional[Dict] = None) -> None:
        """Log warning message."""
        self._write_raw(self._format("WARN", msg, data))

    def error(self, msg: str, data: Optional[Dict] = None) -> None:
        """Log error message."""
        self._write_raw(self._format("ERROR", msg, data))

    def hit(self, username: str) -> None:
        """Log available username."""
        self._write_raw(self._format("HIT", f"Available: {username}"))

    def request(self, username: str, status: int, body: str) -> None:
        """Log HTTP request/response."""
        level = "DEBUG" if self.debug_mode else "INFO"
        self._write_raw(self._format(level, f"HTTP {status} <- {username}", {
            "response": body[:200] if len(body) > 200 else body,
        }))

    def summary(self, hits: int, bad: int, errors: int, elapsed: float, total: int) -> None:
        """Write session summary."""
        rate = total / elapsed if elapsed > 0 else 0
        lines = [
            "",
            "-" * 70,
            "  SESSION SUMMARY",
            "-" * 70,
            f"  Total checked:  {total}",
            f"  Available:      {hits}",
            f"  Taken:          {bad}",
            f"  Errors:         {errors}",
            f"  Duration:       {elapsed:.2f}s",
            f"  Average rate:   {rate:.1f} checks/s",
            "-" * 70,
            "",
        ]
        self._write_raw("\n".join(lines))
