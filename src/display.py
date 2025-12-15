"""Terminal display and CLI interface."""

import sys
from datetime import datetime


class Colors:
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"


class Display:
    """Clean, minimal CLI output handler."""

    WIDTH = 52

    def __init__(self):
        self.c = Colors

    def _line(self, char: str = "─") -> str:
        return f"{self.c.DIM}{char * self.WIDTH}{self.c.RESET}"

    def banner(self) -> None:
        """Display application banner."""
        print()
        print(self._line())
        print(f"{self.c.BOLD}  HYTALE USERNAME CHECKER{self.c.RESET}")
        print(self._line())
        print()

    def info(self, msg: str) -> None:
        """Info message."""
        print(f"  {self.c.DIM}>{self.c.RESET} {msg}")

    def success(self, msg: str) -> None:
        """Success message."""
        print(f"  {self.c.GREEN}+{self.c.RESET} {msg}")

    def error(self, msg: str) -> None:
        """Error message."""
        print(f"  {self.c.RED}x{self.c.RESET} {msg}")

    def warning(self, msg: str) -> None:
        """Warning message."""
        print(f"  {self.c.YELLOW}!{self.c.RESET} {msg}")

    def progress(
        self,
        checked: int,
        total: int,
        hits: int,
        bad: int,
        errors: int,
        rate: float,
    ) -> None:
        """Update progress bar."""
        pct = (checked / total * 100) if total > 0 else 0
        bar_width = 20
        filled = int(bar_width * checked / total) if total > 0 else 0
        bar = f"{self.c.GREEN}{'█' * filled}{self.c.DIM}{'░' * (bar_width - filled)}{self.c.RESET}"

        line = (
            f"  {bar} {self.c.DIM}{pct:5.1f}%{self.c.RESET}  "
            f"{self.c.GREEN}{hits:>4}{self.c.RESET} hit  "
            f"{self.c.DIM}{bad:>4}{self.c.RESET} bad  "
            f"{self.c.RED}{errors:>3}{self.c.RESET} err  "
            f"{self.c.DIM}{rate:>5.1f}/s{self.c.RESET}"
        )

        sys.stdout.write(f"\r{line}")
        sys.stdout.flush()

    def results(self, hits: int, bad: int, errors: int, elapsed: float) -> None:
        """Display final results."""
        print("\n")
        print(self._line())
        print(f"{self.c.BOLD}  RESULTS{self.c.RESET}")
        print(self._line())
        print()
        print(f"  {self.c.GREEN}{hits:>6}{self.c.RESET}  available")
        print(f"  {self.c.DIM}{bad:>6}{self.c.RESET}  taken")
        print(f"  {self.c.RED}{errors:>6}{self.c.RESET}  errors")
        print()
        print(f"  {self.c.DIM}Completed in {elapsed:.2f}s{self.c.RESET}")
        print(f"  {self.c.DIM}Results saved to result/{self.c.RESET}")
        print()
