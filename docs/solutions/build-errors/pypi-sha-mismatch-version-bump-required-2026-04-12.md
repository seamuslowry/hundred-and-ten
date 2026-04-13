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
root_cause: sdist_embeds_pyproject_toml
resolution_type: ci_configuration
related_components:
  - development_workflow
tags:
  - pypi
  - uv
  - publish
  - sdist
  - wheel
  - sha-mismatch
  - pep-440
  - monorepo
---

# PyPI publish fails with SHA mismatch when pyproject.toml is modified without bumping version

## Problem

After modifying a package's `pyproject.toml` (even a non-functional section like
`[dependency-groups].test` or `[tool.ruff]`) without bumping the version, the CI publish step
fails with a SHA mismatch error. `uv build` (without `--wheel`) produces both an sdist
(`.tar.gz`) and a wheel (`.whl`). The sdist embeds `pyproject.toml` verbatim, so any edit —
however minor — changes the tarball SHA. PyPI treats filenames as immutable and rejects the
re-upload.

## Symptoms

```
error: Local file and index file do not match for hundredandten_automation_naive-0.0.1.dev2.tar.gz.
Local: sha256=c3217edd22d01d13f46233ad3ada68b30b3ae8f5dc5db9be1a783310a41c7dbe
Remote: sha256=9539d56f7bef5999430e426aaec75daf56fe705fa0f07358483235d5e1055dd9
```

Note the filename ends in `.tar.gz` — it is the sdist, not the wheel, that conflicts.

## Root Cause

`uv build` (default) produces both artifacts:

- **sdist** (`.tar.gz`): includes `pyproject.toml` verbatim. Any edit changes its SHA.
- **wheel** (`.whl`): contains only compiled `METADATA` derived from `[project]` fields.
  Non-functional sections (`[dependency-groups]`, `[tool.*]`) are not in wheel `METADATA`.

The sdist is the source of the conflict. Wheels built from the same `[project]` fields produce
identical bytes regardless of edits to test groups or linter config.

## Structural Fix (Active)

The CI workflows (`deploy.yaml`, `deploy-test.yaml`) now pass `--wheel` to every `uv build` call:

```yaml
uv build --wheel --package hundredandten-deck
uv build --wheel --package hundredandten-engine
# ...etc
```

This suppresses sdist generation entirely. Only wheels are uploaded to PyPI. A non-functional
`pyproject.toml` edit produces a byte-for-byte identical wheel, so PyPI treats the re-upload as
a no-op. A functional change (adding a runtime dependency) does change wheel `METADATA`, so
those still correctly fail publish without a version bump.

## When a Version Bump Is Still Required

Functional changes to `[project]` fields always require a version bump:

- New or changed `[project].dependencies`
- Changed `[project].requires-python`
- Changed `[project].name`, `version` itself, `description`, `keywords`, `classifiers`

Non-functional sections that **no longer** require a bump (wheels-only CI):

- `[dependency-groups].*` (test/dev groups)
- `[tool.ruff]`, `[tool.black]`, `[tool.pyright]`, `[tool.pytest.*]`
- `[build-system]` (does not appear in wheel METADATA)

## Version Bump Strategy (When Still Needed)

**Under a dev release (`X.Y.Z.devN`):** increment the dev counter.

```toml
version = "0.0.1.dev3"  # was dev2, functional change made
```

**Under a proper release (`X.Y.Z`):** use the `.postX` suffix (PEP 440 §8.1):

```toml
version = "0.1.0.post1"  # was 0.1.0, functional change made
```

Do not combine the two suffixes — `0.0.1.dev2.post1` is not valid PEP 440.

## Related

- `docs/plans/2026-04-12-002-fix-exclude-pyproject-from-sdist-plan.md` — plan that introduced
  the wheels-only CI fix.
- `docs/solutions/best-practices/uv-test-only-dependencies-and-decoupled-strategy-packages-2026-04-11.md`
  — covers `[dependency-groups]` scoping.
