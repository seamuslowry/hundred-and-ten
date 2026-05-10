---
title: "Raise consumer dependency floors on breaking changes in pre-1.0 packages"
date: 2026-05-10
category: conventions
module: hundredandten
problem_type: convention
component: development_workflow
severity: medium
applies_when:
  - A package in the monorepo bumps its version
  - The bump includes a breaking or user-observable behavioral change
  - The bumped package is a dependency of one or more other packages in the workspace
tags:
  - versioning
  - uv-workspace
  - monorepo
  - pre-1.0
  - dependency-floor
  - breaking-changes
---

# Raise consumer dependency floors on breaking changes in pre-1.0 packages

## Context

This monorepo manages several interdependent packages, all currently in the `0.x` version range. During development, multiple packages are often bumped in the same PR or release cycle for different reasons — some bumps carry genuine behavioral changes, others are purely mechanical (e.g. getting a new filename for PyPI reproducibility). The question that arises: after a bump, which of a package's consumers within this repo need their `>=` lower bound raised to match?

Without a clear policy, the dependency floors drift out of sync with the actual minimum-compatible version, allowing `uv` to resolve consumers against an older, incompatible package version.

## Guidance

**Raise a consumer's `>=` floor when the upstream bump includes a breaking change. Leave the floor alone otherwise.**

### What counts as a breaking change in 0.x

In semantic versioning, pre-1.0 (`0.x`) versions carry no stability guarantee at the patch level — any change can technically be breaking. Treat the following as breaking changes that require a floor bump in all direct consumers:

- Any user-observable behavior change (e.g. a different player becomes the active player during a game phase)
- New required fields or changed signatures on public APIs
- Removed or renamed public symbols
- Changes to game logic, state representation, or action semantics

Because breaking changes will be frequent throughout the `0.x` lifecycle, assume a behavior-changing bump requires consumer floor bumps unless you can confirm otherwise.

### What does NOT require a floor bump

- Pure internal refactors with identical public behavior
- Packaging or metadata-only bumps (e.g. bumping a version to get a new wheel filename for uv/PyPI reproducibility — see related build-errors docs)
- Test-only or CI-only changes

### Test-group dependencies

Test-group deps (the `test` key under `[dependency-groups]`) should have their floors raised alongside production deps when the behavior change would affect how tests are written or run — to prevent CI from resolving to a broken version. Exception: `hundredandten-testing` keeps both its `hundredandten-engine` and `hundredandten-state` deps completely unbounded (no version specifier at all), because it is an internal, unpublished package.

### Public contract, not dep graph position

The question to ask is: "Does a consumer that stays on the old version see incorrect or different behavior?" If yes, raise the floor. The policy applies equally to production and test-group dependencies; the dep graph position does not change the obligation.

## Why This Matters

If a breaking change lands in `0.0.7` but a consumer still specifies `>=0.0.6`, a fresh `uv sync` may resolve to `0.0.6` and produce quietly wrong behavior — or, if the lockfile pins to `0.0.7`, the declared constraint is now inconsistent with the actual minimum requirement. The floor is the only machine-readable record of which version introduced behavior this consumer depends on.

Conversely, raising a floor when nothing broke creates noise and makes it harder to distinguish meaningful constraints from housekeeping. A floor should mean: *"this version introduced something I require."*

## Examples

### Required floor bump: engine 0.0.6 → 0.0.7

The engine's `active_player` logic during the `DISCARD` phase changed — the dealer now discards first instead of the player after the dealer. Any consumer that walks a game through `DISCARD` and observes `active_player` would produce different results against the old engine.

**Before** (`hundredandten-automation-engineadapter/pyproject.toml`):
```toml
dependencies = [
    "hundredandten-engine>=0.0.5,<1.0.0",
    "hundredandten-state>=0.0.6,<1.0.0",
    "hundredandten-deck>=0.0.3,<1.0.0",
]
```

**After** — engine floor raised, others unchanged:
```toml
dependencies = [
    "hundredandten-engine>=0.0.7,<1.0.0",   # floor raised: DISCARD turn order changed
    "hundredandten-state>=0.0.6,<1.0.0",
    "hundredandten-deck>=0.0.3,<1.0.0",
]
```

### Floor bump not required: deck 0.0.3 → 0.0.4, state 0.0.6 → 0.0.7, naive 0.0.5 → 0.0.6

These were bumped solely to produce new wheel filenames for uv/PyPI reproducibility (the `Generator: uv X.Y.Z` field in wheel METADATA changes when the uv version changes). No public API, behavior, or logic changed.

Consumer floors for all three were left at their existing values.

## Related

- [`docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`](../build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md) — when to bump a package's *own* version (sdist SHA mismatch problem)
- [`docs/solutions/build-errors/wheel-sha-mismatch-unpinned-uv-version-2026-05-10.md`](../build-errors/wheel-sha-mismatch-unpinned-uv-version-2026-05-10.md) — when to bump a package's *own* version (wheel SHA mismatch from unpinned uv)
- [`docs/solutions/best-practices/uv-workspace-namespace-package-extraction-2026-04-11.md`](../best-practices/uv-workspace-namespace-package-extraction-2026-04-11.md) — shows `>=0.0.0` as the starting floor pattern; this convention governs when to raise it
