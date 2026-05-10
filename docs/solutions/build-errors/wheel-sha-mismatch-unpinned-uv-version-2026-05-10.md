---
title: "PyPI wheel SHA mismatch caused by unpinned uv version in CI"
date: 2026-05-10
category: build-errors
module: publishing
problem_type: build_error
component: tooling
severity: high
symptoms:
  - "CI publish fails with 'Local file and index file do not match' SHA mismatch error on a .whl file, not a tarball"
  - "Re-running the publish job with no source changes produces a different wheel SHA"
  - "Mismatch only appears for packages whose version already exists on PyPI from a prior CI run"
root_cause: config_error
resolution_type: config_change
related_components:
  - development_workflow
tags:
  - pypi
  - uv
  - wheel
  - sha-mismatch
  - ci-pinning
  - wheel-metadata
  - uv-version
  - monorepo
---

# PyPI wheel SHA mismatch caused by unpinned uv version in CI

## Problem

Wheel builds are not byte-for-byte reproducible when the `uv` version is not pinned in CI. PyPI rejects re-uploads of a wheel filename that already exists with a different SHA, causing publish to fail for unchanged packages.

## Symptoms

```
error: Local file and index file do not match for hundredandten_deck-0.0.3-py3-none-any.whl.
Local: sha256=e4f46428a1d71f0569d0f4e416822f80c5191d2594be037b282ac6f33c348c64,
Remote: sha256=486366409501a1bb6a1a4337fa439c5f5823d4a0c2db0a795ca6628c0041db58
```

The affected package has not changed — same source, same version number — yet the locally-built wheel produces a different SHA than the file already on PyPI.

## What Didn't Work

**`SOURCE_DATE_EPOCH` environment variable** — This clamps zip entry timestamps to a deterministic value, but all zip entries in uv-built wheels are already clamped to `(1980, 1, 1, 0, 0, 0)`. Timestamps were not the source of non-determinism, so this would have had no effect.

## Solution

Pin the `uv` version in the CI publish workflow using `astral-sh/setup-uv`:

```yaml
# .github/workflows/publish.yaml
- uses: astral-sh/setup-uv@v7
  with:
    enable-cache: true
    # Pin uv so the Generator: field in wheel METADATA is stable across
    # runs. Update this together with uv_build requires in each pyproject.toml.
    uv-version: "0.11.12"
```

Additionally, bump the version of any package whose current local version already exists on PyPI. In this case: `hundredandten-deck` 0.0.3→0.0.4, `hundredandten-state` 0.0.6→0.0.7, `hundredandten-automation-naive` 0.0.5→0.0.6. This ensures the first publish run under the newly-pinned `uv` uses filenames that do not yet exist on PyPI, so all uploads proceed cleanly.

## Why This Works

The `WHEEL` metadata file embedded inside every wheel contains a `Generator:` line that records the exact `uv` version used to build it:

```
Wheel-Version: 1.0
Generator: uv 0.11.2
Root-Is-Purelib: true
Tag: py3-none-any
```

When CI installs a newer unpinned `uv` (e.g. 0.11.12 instead of 0.11.2), this line changes. Because the `RECORD` file inside the wheel hashes every other file in the archive — including `WHEEL` itself — the `RECORD` changes too. This causes the wheel's overall SHA256 to differ, even though the package source code is identical. PyPI treats wheel filenames as immutable: once published, any re-upload with a different SHA is rejected. Pinning `uv-version` ensures the `Generator:` line is identical across every build, producing a byte-for-byte reproducible wheel.

## Prevention

- **Pin `uv-version` in all CI workflows that build and publish wheels.** Do not rely on `astral-sh/setup-uv` defaulting to the latest release — every new patch version of `uv` changes the `Generator:` line and breaks reproducibility.

- **Update the CI pin and the build-system floor together.** Each `pyproject.toml` declares a `[build-system]` requirement such as `requires = ["uv_build>=0.11.2,<0.12"]`. When upgrading `uv`, update both the `uv-version` CI pin and the `uv_build` lower bound in every published package's `pyproject.toml` in the same commit.

- **Bump package versions before the first publish under a new `uv` version** if any existing published version was built with the old `uv`.

## Related Issues

- [`docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`](pypi-sha-mismatch-version-bump-required-2026-04-12.md) — companion problem: SHA mismatch caused by sdist embedding `pyproject.toml` verbatim; fixed by switching to `--wheel`-only builds. That fix eliminates the sdist failure mode; this fix eliminates the wheel failure mode. Both are needed.
