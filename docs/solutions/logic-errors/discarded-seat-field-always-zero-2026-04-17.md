---
title: "Discarded dataclass seat field was invariantly zero"
date: 2026-04-17
category: docs/solutions/logic-errors
module: hundredandten-state
problem_type: logic_error
component: service_object
symptoms:
  - Discarded dataclass carried a `seat` field that was always 0
  - Field implied per-player discard visibility but only the requesting player's own discards are ever exposed
  - Misleading public API surface in the state observation layer
root_cause: logic_error
resolution_type: code_fix
severity: low
tags: [discarded, seat, cardstatus, gamestate, dataclass, player-relative, api-cleanup]
---

# Discarded dataclass seat field was invariantly zero

## Problem

`Discarded`, a frozen dataclass in `hundredandten-state`, carried a `seat: int` field that was invariantly `0`. Because `EngineAdapter` only marks cards `Discarded` for the requesting player (who is always seat 0 in the player-relative model), the field conveyed no information but implied it could vary.

## Symptoms

- `Discarded(seat=0)` constructed at every callsite — no callsite ever passed a non-zero value.
- The docstring "Card was discarded by a specific seat" implied per-seat granularity that the design explicitly prevents.
- Consumers inspecting `card_status.seat` would always find `0`, with no way to know whether that was meaningful or accidental.

## What Didn't Work

N/A — this was a proactive API cleanup, not a fix following observable breakage. The field was never incorrect; it was misleading. No downstream code relied on the field carrying variance.

## Solution

**`packages/hundredandten-state/src/hundredandten/state/__init__.py`**

```python
# Before
@dataclass(frozen=True)
class Discarded:
    """Card was discarded by a specific seat"""
    seat: int

# After
@dataclass(frozen=True)
class Discarded:
    """Card was discarded by the requesting player"""
```

**`packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py`**

```python
# Before
card_status_by_card[card] = Discarded(seat=0)

# After
card_status_by_card[card] = Discarded()
```

**`packages/hundredandten-automation-engineadapter/tests/engineadapter/test_engine_adapter.py`**

```python
# Before — in test_own_discards_visible_after_discard
for ck in state.cards:
    if isinstance(ck.status, Discarded):
        self.assertEqual(ck.status.seat, 0)  # removed — field no longer exists
```

**`packages/hundredandten-state/README.md`**

```markdown
<!-- Before -->
| `Discarded` | Card was discarded by relative `seat`. |

<!-- After -->
| `Discarded` | Card was discarded by this player. |
```

## Why This Works

The `GameState` model is player-relative by design: the requesting player is always seat 0, and `EngineAdapter` only marks cards `Discarded` when `discard.identifier == player.identifier`. This means no card belonging to another seat is ever reachable via the `Discarded` path. The `seat` field therefore had a fixed domain of `{0}` — structural noise rather than data. Removing it collapses a one-element set to a unit type, which is the honest representation.

## Prevention

**Design dataclass fields to carry variance.** Before adding a field to a public dataclass, ask: can this field hold more than one distinct value across all construction sites? If the answer is no, the field belongs in a docstring — not in the type.

Specific guidance for this codebase:

- The `GameState` observation is **player-relative and identity-stripped by contract**. Any field that encodes "which player" is suspect — verify it can actually differ before including it.
- Prefer unit dataclasses (no fields) over single-valued dataclasses when the type itself carries the meaning: `Discarded()` is clearer than `Discarded(seat=0)` when `seat` is always `0`.
- When reviewing `EngineAdapter` changes, check that every field on every constructed `CardStatus` subclass can actually vary across the state space it models.

## Related Issues

- See also: [`docs/solutions/best-practices/engineadapter-extraction-test-checklist-2026-04-12.md`](../best-practices/engineadapter-extraction-test-checklist-2026-04-12.md) — seat-field rotation test checklist; `Discarded` intentionally has no seat field and should not appear in that inventory.
