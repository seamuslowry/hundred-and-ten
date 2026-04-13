---
title: "fix: Publish wheels only to eliminate sdist SHA mismatch"
type: fix
status: active
date: 2026-04-12
---

# fix: Publish wheels only to eliminate sdist SHA mismatch

## Overview

Change both deploy CI workflows to build and publish wheels only (no sdists). This eliminates the SHA mismatch problem that forces unnecessary version bumps when `pyproject.toml` is edited non-functionally (test groups, linter config, dev tool settings).

## Problem Frame

`uv build` produces both an sdist (`.tar.gz`) and a wheel (`.whl`) by default. The sdist embeds `pyproject.toml` verbatim. Any edit to `pyproject.toml` — regardless of whether it is functional (dependency changes, version bumps) or non-functional (test group additions, ruff/black config tweaks) — produces a different sdist tarball. If the version number is unchanged, `uv publish` tries to upload a file with the same filename but a different SHA, which PyPI rejects.

The sdist is published only because `uv build` produces it by default and `uv publish` uploads everything in `dist/`. There is no functional requirement to publish sdists for this project: all packages are pure-Python and are consumed as wheels.

By building and publishing only wheels, the sdist SHA mismatch problem is eliminated entirely, with no changes to individual package configuration, no version constraint concerns, and full PEP conformance.

See the documented pain point: `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`.

## Requirements Trace

- R1. After the change, non-functional edits to a published package's `pyproject.toml` (test groups, linter config, build constraints) must not require a version bump to successfully publish.
- R2. No changes to individual package `pyproject.toml` files — the fix must live entirely in CI configuration.
- R3. No version bumps required as part of this change.
- R4. Published packages must remain installable via `pip install` with full metadata (dependencies, version, etc.).

## Scope Boundaries

- Individual package `pyproject.toml` files are out of scope — no `source-exclude`, no build backend changes.
- Sdist publication is intentionally stopped; this is the goal, not a limitation.
- No changes to game logic, test structure, or public package APIs.
- The `deploy-test.yaml` workflow firing on every push (not just `main`) is a separate concern; do not address it here.
- The `hundredandten-testing` package is not published in either workflow; no change needed for it.

## Context & Research

### Relevant Code and Patterns

- `.github/workflows/deploy.yaml` — builds and publishes to PyPI on push to `main`; currently uses `uv build --package <name>` (no `--wheel` flag)
- `.github/workflows/deploy-test.yaml` — builds and publishes to Test PyPI on every push; same pattern

Current build commands in both workflows:
```
uv build --package hundredandten-deck
uv build --package hundredandten-engine
uv build --package hundredandten-state
uv build --package hundredandten-automation-naive
uv build --package hundredandten-automation-engineadapter
uv publish
```

The `uv publish` step uploads all files in `dist/` — both `.whl` and `.tar.gz` by default.

### Institutional Learnings

- `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md` — documents the root cause and prior workaround. This plan implements the structural fix described there.

### External References

- uv build docs: `uv build --wheel` produces only the wheel artifact (no sdist). All package metadata (`PKG-INFO`, `.dist-info/METADATA`) is correctly included in the wheel.
- PyPI supports wheel-only packages; pure Python packages do not require sdists.

## Key Technical Decisions

- **`--wheel` flag on `uv build`, not `--no-sdist`:** `uv build --wheel` explicitly requests only a wheel. This is cleaner than a hypothetical negation flag and is the documented form.
- **No package-level config changes:** The fix belongs in CI, not in each package's `pyproject.toml`. There are no version compatibility questions, no conformance concerns, and no per-package decisions.
- **No version bumps required for this change:** Adding `--wheel` does not modify any package's `pyproject.toml`. This change can land on `main` without any version increment for any package.
- **Consumers are unaffected:** `pip install hundredandten-deck` resolves the wheel from PyPI. The sdist was never needed for installation. The `.dist-info/METADATA` in the wheel contains full dependency and version information.
- **`dist/` accumulation is resolved:** Because only wheels are now produced, `dist/` will not accumulate stale sdist files from previous builds. If `dist/` is ever reused across builds (it isn't in CI with a fresh checkout), this reduces confusion.

## Open Questions

### Resolved During Planning

- **Does removing sdist publication break consumers?** No — pure-Python packages consumed via `pip install` use the wheel. PyPI does not require sdists to be present.
- **Will `uv publish` fail if only `.whl` files are in `dist/`?** No — `uv publish` uploads all artifacts present; with `--wheel` builds, only `.whl` files are present.
- **Does `uv build --package X --wheel` work for workspace packages?** Yes — the `--wheel` flag is compatible with `--package` in uv's build command.

### Deferred to Implementation

- **Whether to clear `dist/` between builds in CI:** The current workflows use a clean checkout per run (no artifact caching of `dist/`), so accumulation is not an issue. Confirm during implementation if `dist/` is ever shared across workflow runs.

## Implementation Units

- [ ] **Unit 1: Add `--wheel` flag to both deploy workflows**

**Goal:** Both deploy CI workflows build wheel-only artifacts, eliminating sdist production and ending the SHA mismatch problem for non-functional `pyproject.toml` changes.

**Requirements:** R1, R2, R3, R4

**Dependencies:** None

**Files:**
- Modify: `.github/workflows/deploy.yaml`
- Modify: `.github/workflows/deploy-test.yaml`

**Approach:**
- In each workflow's build step, append `--wheel` to every `uv build --package <name>` call
- No other changes needed — `uv publish` already uploads whatever is in `dist/`

**Patterns to follow:**
- Existing `uv build --package <name>` pattern in both workflow files; add `--wheel` to each line

**Test scenarios:**
- Happy path: After the workflow runs, `dist/` contains exactly five `.whl` files and zero `.tar.gz` files
- Happy path: `uv publish` (or `uv publish --index testpypi`) succeeds without SHA conflict errors for all five packages
- Happy path: `pip install hundredandten-deck` from the published index resolves the new wheel, with correct version, dependencies, and package metadata
- Edge case: If a previously published sdist for the same version exists on PyPI, the wheel-only publish does not conflict with or overwrite it — PyPI allows adding wheel artifacts to a version that already has an sdist
- Integration: Subsequent non-functional edits to any package's `pyproject.toml` (e.g., adding a test dependency group) do not cause the next CI deploy run to fail

**Verification:**
- CI deploy-test workflow completes green without SHA mismatch errors after a non-functional `pyproject.toml` edit
- All five packages are installable from Test PyPI after the run
- `dist/` contains only `.whl` files after a `uv build --package X --wheel` invocation

- [ ] **Unit 2: Update the SHA-mismatch learning to reflect the structural fix**

**Goal:** Update `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md` to document that the wheel-only publish strategy was adopted as the structural fix, and that the version-bump workaround is no longer needed for non-functional changes.

**Requirements:** R1 (keeps institutional knowledge accurate)

**Dependencies:** Unit 1

**Files:**
- Modify: `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`

**Approach:**
- Add a section or note explaining that `--wheel` was added to the deploy workflows and that this resolves the non-functional edit problem entirely
- Preserve the root cause explanation (sdist embeds `pyproject.toml` verbatim)
- Note that the version-bump convention still applies when version increments are genuinely needed (new features, dependency changes, breaking changes)

**Test expectation: none** — documentation update only, no behavioral change.

**Verification:**
- The learning doc accurately reflects the current state: wheel-only publish is in effect; non-functional `pyproject.toml` edits are safe; version bumps are only needed for genuinely functional changes.

## System-Wide Impact

- **Interaction graph:** No callbacks, middleware, or observers affected. The change is purely in CI artifact production.
- **Error propagation:** If `--wheel` is unsupported in the installed uv version (unlikely — it is a core flag), `uv build` would fail at the CI build step with a visible error before publish is attempted.
- **State lifecycle risks:** None — no persistent data, no caches.
- **API surface parity:** No public API changes. Package consumers installing from PyPI see identical behavior (wheel install).
- **Integration coverage:** Artifact-level verification is CI-based (deploy-test workflow green after a non-functional edit). The existing pytest suite tests game logic only; no packaging tests exist or are needed.
- **Unchanged invariants:** All package public APIs, game logic, test suites, inter-package dependencies, and individual `pyproject.toml` files are unchanged. The `uv.lock` is not affected.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| An existing PyPI sdist for a given version prevents a wheel from being added | PyPI allows adding new distribution formats to an existing version; wheel and sdist can coexist for the same version. No conflict expected. |
| A downstream tool or consumer explicitly requires sdist (e.g., for auditing or reproducibility) | Acceptable for this project: packages are utility libraries with no known consumers that require sdists. |
| `--wheel` flag was introduced in a uv version newer than what CI installs | `--wheel` is a core flag present since uv's initial release. Negligible risk. |

## Documentation / Operational Notes

- Update `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md` to reflect the solution (Unit 2).
- `AGENTS.md` does not need updating — it describes the dev workflow, not the CI publish configuration.

## Sources & References

- Related code: `.github/workflows/deploy.yaml`, `.github/workflows/deploy-test.yaml`
- Institutional learning: `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`
- External docs: uv build docs (`uv build --wheel`)
