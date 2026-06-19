# LogSimple-Py

> A lightweight, dependency-free Python tool for parsing and analyzing HTTP access log files.

## Table of Contents
- [Description](#description)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage / Quick Start](#usage--quick-start)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Author](#contact--author)

## Description
LogSimple-Py is a minimal Python tool for parsing raw web server access log files (e.g. Apache/Nginx-style combined logs) and extracting structured data from them — client IP address, request timestamp, HTTP method, and response status code — using a single regular expression. It is aimed at developers and DevOps engineers who need a quick, no-dependency way to inspect access logs or compute simple statistics (such as how many requests returned a given status code) without setting up a full log-analysis stack. The core functionality is exposed through a single class, `LogAnalyzer`, which can be used as a library or run directly as a script.

## Key Features
- **Structured parsing** — extracts `ip`, `date`, `method`, and `status` from raw log lines using one regular expression, no external parsing library required.
- **Fault-tolerant** — malformed or unrecognized lines are skipped and logged as warnings instead of crashing the program.
- **Built-in aggregation** — count requests by HTTP status code out of the box with `count_by_status()`.
- **Zero third-party dependencies** — uses only the Python standard library (`re`, `logging`, `typing`).
- **Traceable execution** — parsing warnings and errors are reported via the standard `logging` module.

## Tech Stack
- **Language:** Python 3
- **Standard library modules:** `re` (pattern matching), `logging` (diagnostics), `typing` (type hints)
- **Frameworks / databases:** none

## Requirements
- Python 3.7 or higher
- No external Python packages (see [`requirements.txt`](requirements.txt))
- No OS-specific dependencies

## Installation
```bash
git clone https://github.com/eryks23/LogSimple-Py.git
cd LogSimple-Py
```

Although the project has no third-party dependencies, using a virtual environment is recommended for isolation:
```bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
LogSimple-Py does not use environment variables or `.env` files. The only configurable input is the **path to the log file**, which is passed directly to the `LogAnalyzer` constructor.

When the script is run directly (`python log_analyzer.py`), the input file path is currently **hardcoded to `server.log`** inside the `if __name__ == "__main__":` block. To analyze a different file, either:
- edit the hardcoded path in `log_analyzer.py`, or
- import `LogAnalyzer` in your own script and pass any path you need (see [Usage](#usage--quick-start) below).

## Usage / Quick Start

### As a script
Place a log file named `server.log` in the project root (a sample file is already included) and run:
```bash
python log_analyzer.py
```
This parses `server.log` and logs how many requests returned HTTP status `200`.

### As a library
```python
from log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("server.log")

# Parse the file into a list of dicts: {"ip": ..., "date": ..., "method": ..., "status": ...}
entries = analyzer.parse()
print(f"Parsed {len(entries)} valid entries")

# Aggregate by HTTP status code
ok_count = analyzer.count_by_status("200")
not_found_count = analyzer.count_by_status("404")

print(f"200 OK: {ok_count}")
print(f"404 Not Found: {not_found_count}")
```

Output using the bundled `server.log` sample (timestamps will vary):
```
2026-06-20 12:00:00,000 - WARNING - Błąd w linii 7: invalid-log-line-here
2026-06-20 12:00:00,000 - INFO - Status 200: 2
200 OK: 2
404 Not Found: 1
```

## API Reference

### `class LogAnalyzer(file_path: str)`
Parses an HTTP access log file and provides basic aggregation over the parsed entries.

**Constructor parameters**

| Parameter   | Type  | Description                       |
|-------------|-------|------------------------------------|
| `file_path` | `str` | Path to the log file to be parsed. |

**Attributes**

| Attribute     | Type                   | Description                                                              |
|---------------|------------------------|----------------------------------------------------------------------------|
| `file_path`   | `str`                  | Path passed at construction.                                              |
| `log_pattern` | `str`                  | Regex used to extract `ip`, `date`, `method`, and `status` from a line.   |
| `parsed_data` | `List[Dict[str, str]]` | Populated after calling `parse()`.                                        |

#### `parse() -> List[Dict[str, str]]`
Reads `file_path` line by line. Empty lines are skipped. Each remaining line is matched against an internal regex that captures four named groups: `ip`, `date`, `method`, `status`. Matching lines are appended to `parsed_data`; non-matching lines are skipped and reported with `logger.warning`. If the file cannot be opened or read, the exception is reported with `logger.error` and an empty list is returned.

- **Returns:** `List[Dict[str, str]]` — one dictionary per successfully parsed line, with keys `ip`, `date`, `method`, `status`.

#### `count_by_status(status_code: str) -> int`
Counts how many entries in `parsed_data` have a `status` equal to `status_code`. Must be called after `parse()` — if `parse()` was not called first, `parsed_data` is empty and the result is `0`. The result is reported with `logger.info`.

- **Parameters:** `status_code` (`str`) — HTTP status code to count, e.g. `"200"`, `"404"`.
- **Returns:** `int` — number of matching entries.

**Expected log line format**

The regex expects a line containing, in order: an IPv4 address, a date in square brackets, an HTTP method and request target in quotes followed by the HTTP version, and a three-digit status code, e.g.:
```
127.0.0.1 - - [10/Oct/2025:13:55:36] "GET /index.html HTTP/1.1" 200 1024
```
Note: the response size (`1024` in the example above) appears in standard access logs but is **not** captured by the current regex.

## Project Structure
```
LogSimple-Py/
├── log_analyzer.py     # LogAnalyzer class + script entry point
├── server.log          # Sample access log used for manual testing/demo
├── requirements.txt    # Dependency list (empty - standard library only)
├── LICENSE             # MIT License
└── README.md           # Project documentation
```

## Testing
This project does not currently include an automated test suite (e.g. `pytest`). You can verify behavior manually with the bundled sample log file:
```bash
python log_analyzer.py
```
With the included `server.log`, this should report **2** requests with status `200` and log **1** warning for the malformed line (`invalid-log-line-here`).

Contributions that add automated unit tests — e.g. covering `parse()` against malformed input, empty files, and missing files — are welcome. See [Contributing](#contributing).

## Known Limitations
- The script entry point hardcodes the input filename to `server.log`; there is no command-line argument parsing (e.g. via `argparse`) for selecting a different file without editing the code.
- The regex only captures `ip`, `date`, `method`, and `status`. It does not capture the requested path, HTTP version, or response size, even though they appear in the log line.
- Log/warning messages inside `parse()` and `count_by_status()` are currently written in Polish (e.g. `"Błąd w linii..."`), while the rest of the codebase is in English. Consider localizing these strings for a consistent, English-speaking audience.
- No automated test suite is included yet.

## Contributing
Contributions are welcome:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`.
3. Follow [PEP 8](https://peps.python.org/pep-0008/) and keep functions small and type-hinted.
4. Add or update tests where relevant.
5. Commit with a clear message and open a pull request describing the change and motivation.

For significant changes (e.g. modifying the public API of `LogAnalyzer`), please open an issue first to discuss the approach.

## License
This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Contact / Author
- GitHub: [@eryks23](https://github.com/eryks23)
- Repository: [github.com/eryks23/LogSimple-Py](https://github.com/eryks23/LogSimple-Py)
- Maintainer name / contact email: [DO UZUPEŁNIENIA: pełne imię i nazwisko oraz adres kontaktowy]
