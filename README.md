[![Code Quality](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/lint.yaml/badge.svg?branch=main)](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/lint.yaml)
[![100% Coverage](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/coverage.yaml/badge.svg?branch=main)](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/coverage.yaml)

# Hundred and Ten

A python engine for playing the game Hundred and Ten, organized as a uv workspace monorepo.

## Packages

- [`hundredandten-engine`](packages/hundredandten-engine/): The core game engine package. See its README for game rules and API usage.

## Development

This project uses [uv](https://github.com/astral-sh/uv) for workspace management.

### Installation

```bash
uv sync --group lint --group test
```

### Run tests

```bash
uv run --package hundredandten-engine pytest
```

### Coverage

```bash
uv run --package hundredandten-engine coverage run --branch --source=hundredandten.engine -m pytest && uv run coverage report
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
uv build --package hundredandten-engine
```

## Project Structure

```text
/
├── packages/
│   └── hundredandten-engine/  (game engine package)
├── pyproject.toml             (workspace root)
├── uv.lock                    (workspace lockfile)
└── README.md                  (this file)
```
