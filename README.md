# Hundred and Ten

Python packages used for playing the game Hundred and Ten, organized as a uv workspace monorepo.

## Packages

- [`hundredandten-engine`](packages/hundredandten-engine/): The core game engine package. See its README for game rules and API usage.
- [`hundredandten-automation`](packages/hundredandten-automation/): Automated decision making built upon the engine package. See its README for API usage.
- [`hundredandten-testing`](packages/hundredandten-testing/): An internal testing package used to share testing code.

## Development

This project uses [uv](https://github.com/astral-sh/uv) for workspace management.

### Installation

```bash
uv sync --all-groups --all-packages
```

### Run tests

```bash
uv run pytest
```

### Coverage

```bash
uv run coverage run -m pytest && uv run coverage report -m
```

### Linting

```bash
uv run ruff check .
uv run black --check .
```

### Type checking

```bash
uv run pyright
```

### Build

```bash
uv build --all-packages
```

## Project Structure

```text
/
├── packages/
│   └── hundredandten-automation/  (automation package)
│   └── hundredandten-engine/   (game engine package)
│   └── hundredandten-testing/  (internal; shared testing package)
├── pyproject.toml             (workspace root)
├── uv.lock                    (workspace lockfile)
└── README.md                  (this file)
```
