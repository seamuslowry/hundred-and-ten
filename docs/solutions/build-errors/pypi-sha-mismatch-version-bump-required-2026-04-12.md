---
title: "PyPI publish fails with SHA mismatch when pyproject.toml is modified without bumping version"
date: 2026-04-12
category: build-errors
module: publishing
problem_type: build_error
component: tooling
severity: high
symptoms:
  - "CI publish fails with 'Local file and index file do not match' SHA mismatch error"
  - "PyPI/Test PyPI rejects re-upload of same filename with different tarball hash"
root_cause: missing_workflow_step
resolution_type: workflow_improvement
related_components:
  - development_workflow
tags:
  - pypi
  - uv
  - publish
  - version-bump
  - sdist
  - sha-mismatch
  - pep-440
  - monorepo
---

# PyPI publish fails with SHA mismatch when pyproject.toml is modified without bumping version

## Problem

After modifying a package's `pyproject.toml` (even a test-only section like `[dependency-groups].test`)
without bumping the version, the CI publish step fails with a SHA mismatch error because `uv build`
produces a tarball with different content than the one already on PyPI under that version.

## Symptoms

```
error: Local file and index file do not match for hundredandten_automation_naive-0.0.1.dev2.tar.gz.
Local: sha256=c3217edd22d01d13f46233ad3ada68b30b3ae8f5dc5db9be1a783310a41c7dbe
Remote: sha256=9539d56f7bef5999430e426aaec75daf56fe705fa0f07358483235d5e1055dd9
```

## What Didn't Work

- Treating `[dependency-groups].test` changes as "safe" (non-publishing) changes that don't
  require a version bump. Even though test dependency groups are not part of the installed package
  metadata, they are part of `pyproject.toml`, which `uv build` includes verbatim in the sdist
  tarball — changing any section changes the tarball SHA.

## Solution

Bump the package version before pushing to CI. The correct bump strategy depends on the current
version's release stage:

**Under a dev release (`X.Y.Z.devN`):** increment the dev counter — stay in the dev series.

```toml
# Before (published at this version, then pyproject.toml edited → publish fails)
[project]
name = "hundredandten-automation-naive"
version = "0.0.1.dev2"

[dependency-groups]
test = [
    "hundredandten-testing>=0.0.0,<1.0.0",
]
```

```toml
# After (increment dev counter → new filename, PyPI accepts it)
[project]
name = "hundredandten-automation-naive"
version = "0.0.1.dev3"

[dependency-groups]
test = [
    "hundredandten-automation-engineadapter>=0.0.0,<1.0.0",
    "hundredandten-testing>=0.0.0,<1.0.0",
]
```

**Under a proper release (`X.Y.Z`):** use the **`.postX` suffix** (PEP 440 §8.1) to signal
"same functional code, administrative correction":

```toml
# 0.1.0 already on PyPI, pyproject.toml edited for non-functional reason
version = "0.1.0.post1"  # correct

# Do NOT combine .dev and .post — "0.0.1.dev2.post1" is not valid PEP 440
```

Subsequent administrative fixes increment the appropriate counter:
`0.0.1.dev3` → `0.0.1.dev4`, or `0.1.0.post1` → `0.1.0.post2`.

**Functional changes** (new features, bug fixes) always follow normal semver conventions
regardless of release stage.

## Why This Works

PyPI treats filenames as immutable: once `...-0.0.1.dev2.tar.gz` is accepted at a given SHA,
no other content can be uploaded under that filename. `uv build` packages `pyproject.toml`
verbatim into the sdist, so any edit — no matter how minor — produces a different tarball with
a different SHA. Bumping the version creates a new, distinct filename that PyPI will accept.

## Prevention

- **Rule:** Any commit that modifies a package's `pyproject.toml` requires a version bump
  before the next publish — no exceptions, regardless of which section changed.
- **Dev release** (`X.Y.Z.devN`): increment `N`. **Proper release** (`X.Y.Z`): append `.postX`.
  Do not combine the two suffixes (`X.Y.Z.devN.postX` is not valid PEP 440).
- Non-obvious sections that still require a bump: `[dependency-groups].test`,
  `[project].description`/`keywords`/`classifiers`, `[tool.*]` config blocks (ruff, black,
  pyright, pytest), and `[build-system]` requires.
- In a uv workspace monorepo, each package in the publish workflow must be checked independently —
  only packages whose `pyproject.toml` changed need a bump, but one unbumped package fails
  the entire `uv publish` run.

## Related Issues

- `docs/solutions/best-practices/uv-test-only-dependencies-and-decoupled-strategy-packages-2026-04-11.md`
  — covers `[dependency-groups]` scoping; note that test deps not being in installed metadata
  does not exempt `pyproject.toml` from the version-bump rule.
