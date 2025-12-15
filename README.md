# Hytale Username Checker

![Preview](https://i.ibb.co/mVfmVmWw/preview.png)

A fast, multi-threaded tool to check Hytale username availability.

## Features

- Multi-threaded checking with connection pooling
- Real-time progress bar with statistics
- Automatic rate limit handling with exponential backoff
- Username validation (3-16 chars, alphanumeric + underscore)
- Duplicate detection and removal
- Structured session logging
- Clean, minimal CLI interface

## Project Structure

```
hytale-checker/
├── main.py              # Entry point
├── config.json          # Configuration
├── src/
│   ├── __init__.py      # Package exports
│   ├── checker.py       # Core checking engine
│   ├── config.py        # Configuration management
│   ├── display.py       # CLI interface
│   ├── logger.py        # Structured logging
│   └── validator.py     # Username validation
├── data/
│   └── usernames.txt    # Input usernames
├── result/              # Results (generated)
│   ├── available.txt    # Available usernames
│   └── taken.txt        # Taken usernames
└── logs/                # Session logs (generated)
```

## Quick Start

1. Add usernames to `data/usernames.txt` (one per line)
2. Run the checker:

```bash
python main.py
```

3. Check results in `result/available.txt`

## Configuration

Edit `config.json` to customize behavior:

| Option        | Default | Description                           |
|---------------|---------|---------------------------------------|
| `threads`     | 3      | Number of concurrent threads          |
| `timeout`     | 10      | HTTP request timeout (seconds)        |
| `retries`     | 5       | Max retry attempts on failure         |
| `retry_delay` | 10.0     | Base delay between retries (seconds)  |
| `debug`       | false   | Enable verbose logging                |

## Username Rules

Hytale usernames must:
- Be 3-16 characters long
- Contain only letters, numbers, and underscores
- Be unique (case-insensitive)

Invalid usernames are automatically filtered during loading.

## Requirements

- Python 3.9+
- urllib3

## License

MIT
