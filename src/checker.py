"""Core username checking engine."""

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Tuple

import urllib3

from .config import Config
from .display import Display
from .logger import Logger
from .validator import Validator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ResultWriter:
    """Thread-safe result file writer."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.hits_file = output_dir / "available.txt"
        self.taken_file = output_dir / "taken.txt"

        self._lock_hits = threading.Lock()
        self._lock_taken = threading.Lock()

        # Initialize empty files
        self.hits_file.write_text("")
        self.taken_file.write_text("")

    def save_hit(self, username: str) -> None:
        """Save available username."""
        with self._lock_hits:
            with open(self.hits_file, "a", encoding="utf-8") as f:
                f.write(f"{username}\n")

    def save_taken(self, username: str) -> None:
        """Save taken username."""
        with self._lock_taken:
            with open(self.taken_file, "a", encoding="utf-8") as f:
                f.write(f"{username}\n")


class UsernameChecker:
    """Multi-threaded Hytale username availability checker."""

    API_URL = "https://api.hytl.tools/check/{}"

    HEADERS = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://hytl.tools",
        "Referer": "https://hytl.tools/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    def __init__(self, config: Config, display: Display, base_dir: Path):
        self.config = config
        self.display = display
        self.base_dir = base_dir

        # Initialize components
        self.logger = Logger(base_dir / "logs", debug=config.debug)
        self.writer = ResultWriter(base_dir / "result")

        # Thread-safe statistics
        self._lock = threading.Lock()
        self.checked = 0
        self.hits = 0
        self.taken = 0
        self.errors = 0

        # HTTP connection pool
        self.http = urllib3.PoolManager(
            num_pools=config.threads,
            maxsize=config.threads,
            timeout=urllib3.Timeout(total=config.timeout),
            retries=False,
        )

    def _check_username(self, username: str) -> Tuple[str, bool, Optional[str]]:
        """
        Check single username availability.

        Returns:
            (username, is_available, error_message)
        """
        url = self.API_URL.format(username)

        for attempt in range(self.config.retries + 1):
            try:
                response = self.http.request("GET", url, headers=self.HEADERS)
                body = response.data.decode("utf-8")

                self.logger.request(username, response.status, body)

                if response.status == 200:
                    data = json.loads(body)
                    available = data.get("available", False)

                    if available:
                        self.logger.hit(username)

                    return (username, available, None)

                elif response.status == 429:
                    # Rate limited - exponential backoff
                    wait = self.config.retry_delay * (2 ** attempt)
                    self.logger.warn(f"Rate limited on {username}, waiting {wait:.1f}s")
                    time.sleep(wait)
                    continue

                else:
                    error = f"HTTP {response.status}"
                    self.logger.error(f"Request failed for {username}", {"status": response.status})
                    return (username, False, error)

            except Exception as e:
                if attempt < self.config.retries:
                    time.sleep(self.config.retry_delay)
                    continue

                error = str(e)
                self.logger.error(f"Exception checking {username}", {"error": error})
                return (username, False, error)

        return (username, False, "Max retries exceeded")

    def _update_stats(self, available: bool, error: Optional[str]) -> None:
        """Update statistics thread-safely."""
        with self._lock:
            self.checked += 1
            if error:
                self.errors += 1
            elif available:
                self.hits += 1
            else:
                self.taken += 1

    def run(self, input_file: Path) -> None:
        """Execute the checker."""
        # Load and validate usernames
        self.display.info(f"Loading usernames from {input_file.name}")
        usernames, dupes, invalid = Validator.load_file(input_file)
        total = len(usernames)

        if total == 0:
            self.display.error("No valid usernames to check")
            return

        self.display.success(f"Loaded {total} usernames")
        if dupes > 0:
            self.display.info(f"Removed {dupes} duplicates")
        if invalid > 0:
            self.display.info(f"Skipped {invalid} invalid")
        self.display.info(f"Using {self.config.threads} threads")
        print()

        self.logger.info("Starting check session", {
            "total": total,
            "threads": self.config.threads,
            "timeout": self.config.timeout,
        })

        start_time = time.time()

        # Process with thread pool
        with ThreadPoolExecutor(max_workers=self.config.threads) as pool:
            futures = {pool.submit(self._check_username, u): u for u in usernames}

            for future in as_completed(futures):
                username, available, error = future.result()

                # Save results
                if error is None:
                    if available:
                        self.writer.save_hit(username)
                    else:
                        self.writer.save_taken(username)

                # Update stats and display
                self._update_stats(available, error)

                elapsed = time.time() - start_time
                rate = self.checked / elapsed if elapsed > 0 else 0

                self.display.progress(
                    self.checked, total,
                    self.hits, self.taken, self.errors,
                    rate
                )

        elapsed = time.time() - start_time

        # Final summary
        self.logger.summary(self.hits, self.taken, self.errors, elapsed, total)
        self.display.results(self.hits, self.taken, self.errors, elapsed)
