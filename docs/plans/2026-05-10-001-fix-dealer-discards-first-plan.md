---
title: "fix: Dealer discards first instead of player after dealer"
type: fix
status: completed
date: 2026-05-10
---

# fix: Dealer discards first instead of player after dealer

## Overview

Issue [#186](https://github.com/seamuslowry/hundred-and-ten/issues/186) ("dealer should discard and take first") reports a turn-order bug in the DISCARD phase. Today, after trump is selected, the player **clockwise of the dealer** is the first active player to discard. Per the rules of 110, the **dealer** should discard first (and, by virtue of being first to discard, take their replacement cards from the deck first as well).

The fix is a one-conditional change in `Round.active_player` for the DISCARD branch. Replacement-card draw order is implicit in discard order — the dealer drawing replacements first comes for free.

Scope is intentionally narrow on the **engine** side: this plan changes **DISCARD only**. First-trick lead (currently "player after the bidder leads") is out of scope per user direction.

The change is a user-observable behavior fix in the engine, so this plan also covers:

- Bumping `hundredandten-engine` 0.0.6 → 0.0.7.
- Raising every consumer's `hundredandten-engine` floor (production *and* test-group dependencies) to `>=0.0.7` so no consumer can be paired with the buggy engine.
- Bumping consumer versions only when their **public contract** changes — by user policy, test dependencies are not part of the public contract. That makes `hundredandten-automation-engineadapter` the only consumer that gets a version bump (its production code orchestrates engine acts whose observable behavior shifts). `hundredandten-automation-naive` and `hundredandten-testing` get floor bumps without version bumps. `hundredandten-state` and `hundredandten-deck` declare no engine dependency and are unaffected.

## Problem Frame

In `Round.active_player` (`packages/hundredandten-engine/src/hundredandten/engine/round.py:117-124`), the DISCARD branch initializes `last_discarder` to the dealer's identifier when no discards have happened yet, then returns `player_after(self.players, last_discarder)`. The result: the seat clockwise of the dealer discards first, the dealer discards last. This violates the standard 110 rule.

Because `Round.__discard` (`round.py:329-334`) draws replacement cards from `self.deck` synchronously when each discard is recorded, the player who discards first also draws their replacements first. Fixing discard order therefore implicitly fixes draw order — there is no separate "draw" step to update.

The state and automation packages do not depend on this behavior:

- `GameState` (`packages/hundredandten-state/src/hundredandten/state/__init__.py`) does not expose an "active discarder" seat. Discard availability is currently advertised to all callers in DISCARD status — a pre-existing leak unrelated to this issue.
- `EngineAdapter` (`packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py`) reads `active_player` indirectly through engine acts; no seat-derived field changes.
- `naive` automation reads only `state.bidding.bidder_seat`, never the discard turn order.

## Requirements Trace

- R1. The dealer is the first active player when the DISCARD phase begins.
- R2. Subsequent discard turns proceed clockwise from the dealer (player after the dealer goes second, etc.).
- R3. Replacement cards are drawn in discard order (dealer draws first), with no behavioral change to the existing inline-draw mechanism in `Round.__discard`.
- R4. The transition DISCARD → TRICKS still triggers when all four players have discarded; status derivation and trick initialization are unchanged.
- R5. First-trick lead behavior is unchanged (still "player after the bidder").
- R6. `hundredandten-engine` is bumped to 0.0.7 to signal the user-observable behavior change.
- R7. Every package that declares a `hundredandten-engine` dependency (production or test-group) raises its floor to `>=0.0.7,<1.0.0`, preventing any consumer from being paired with the buggy engine.
- R8. `hundredandten-automation-engineadapter` is bumped (its production contract changes — `EngineAdapter` orchestrates engine acts whose observable behavior shifts). `hundredandten-automation-naive` and `hundredandten-testing` are not version-bumped because their public contracts are unchanged (the floor change there is a test-dep or internal-helper concern).

## Scope Boundaries

- First-trick lead in `round.py:127-139` is **not** changed. The existing `test_play_first_card_of_round` (`packages/hundredandten-engine/tests/game/test_play_card.py:26-47`) continues to pin the current rule and must keep passing.
- No new field on `GameState`, `TableInfo`, or any state-package dataclass.
- No new gating of `available_actions` for `Status.DISCARD` (the pre-existing "all callers see all discard subsets" behavior is left as-is).
- No change to bidding or trump-selection turn order.
- No change to how dealer rotation works between rounds (`game.py:151-172`).
- No version bump or floor bump for `hundredandten-state` or `hundredandten-deck` — neither declares an engine dependency.
- No version bump for `hundredandten-automation-naive` or `hundredandten-testing` — public contracts unchanged. They receive floor bumps only.

### Deferred to Follow-Up Work

- Adding an `active_seat` field to `TableInfo` and gating `Status.DISCARD` available actions on it (mirroring the `bidder_seat == 0` gate at `state/__init__.py:232-237`). Not introduced by this fix.

---

## Context & Research

### Relevant Code and Patterns

- **DISCARD active-player rule (the change site):** `packages/hundredandten-engine/src/hundredandten/engine/round.py:117-124`.
- **First-trick lead rule (intentionally unchanged):** `packages/hundredandten-engine/src/hundredandten/engine/round.py:127-139`.
- **Dealer accessor:** `Round.dealer` property at `packages/hundredandten-engine/src/hundredandten/engine/round.py:89-95`, backed by `players_by_role(self.players, RoundRole.DEALER)`.
- **Inline replacement-card draw:** `Round.__discard` at `packages/hundredandten-engine/src/hundredandten/engine/round.py:329-334` (`self.active_player.hand.extend(self.deck.draw(len(discard.cards)))`).
- **Helper precedent:** `player_after(players, identifier)` (`packages/hundredandten-engine/src/hundredandten/engine/player.py:27-33`). The codebase has no `player_before`, so the cleanest fix sidesteps that gap.
- **BIDDING active-player parallel structure (`round.py:101-112`):** uses the same "treat dealer as last X when none have happened yet" pattern that is the source of the DISCARD bug. We are deliberately diverging from this pattern in DISCARD because the rule for DISCARD is genuinely different — bidding starts with the player after the dealer (correct), discarding starts with the dealer (the rule we're enforcing).
- **Test arrangement helper:** `arrange.discard` in `packages/hundredandten-testing/src/hundredandten/testing/arrange.py:85-90` iterates `active_player` while `status == Status.DISCARD` and always passes `Discard(..., [])` — an **empty discard**. This means `len(discard.cards) == 0`, `self.deck.draw(0)` returns `[]`, and the deck's `pulled` counter does not advance during the arrange-time discard phase. **Initial hands and deck position at the start of TRICKS are therefore identical regardless of discard order.** The only thing that changes is the order in which `Discard` objects are appended to `_discards`.
- **Consumers of `Round.discards`:** the only consumer outside `Round` itself is `EngineAdapter` at `packages/hundredandten-automation-engineadapter/src/hundredandten/automation/engineadapter/__init__.py:201-204`, which iterates discards order-agnostically and filters by `discard.identifier == player.identifier`. Order does not affect its output.
- **Existing version pattern:** all packages have used `0.0.x` patch increments only. Engine: 0.0.6. State: 0.0.6. Engineadapter: 0.0.5. Naive: 0.0.5. Deck: 0.0.3. Testing: 0.0.0 (internal). Per user direction, this fix continues that cadence with a patch bump on engine (0.0.6 → 0.0.7) rather than introducing a minor-bump precedent.

### Institutional Learnings

- `docs/solutions/logic-errors/discarded-seat-field-always-zero-2026-04-17.md` — confirms that `Discarded` in the state package carries no per-seat information; this fix does not need to touch `CardStatus` subclasses or the engineadapter `card_status_by_card` builder.
- `docs/solutions/best-practices/engineadapter-extraction-test-checklist-2026-04-12.md` — seat-field rotation tests for `bidder_seat` and `dealer_seat` exercise dealer-relative arithmetic but do not pin discard order. They will continue to pass.

### External References

None. Standard 110 turn-order rule; no external documentation needed.

---

## Key Technical Decisions

- **Branch on `not self.discards` rather than introducing a `player_before` helper.** Returning `self.dealer` directly when no discards have occurred is more intent-revealing than computing `player_before(dealer)` so that `player_after(...)` lands back on the dealer. It also avoids adding a new helper for one caller.
- **Diverge from the BIDDING branch's "treat dealer as last X" idiom.** That idiom encodes "start with the player after the dealer", which is correct for bidding and wrong for discarding. Mirroring it caused this bug; we deliberately use a different shape here.
- **Do not touch the inline-draw mechanism.** Drawing replacement cards is already coupled to discard order via `__discard`. No extra change satisfies R3.
- **Leave first-trick lead alone.** Per user direction, "take" in the issue title refers to taking replacement cards from the deck, not leading the first trick. This keeps the change reviewably small.
- **Patch bump engine to 0.0.7, not minor bump.** Honors the project's existing 0.0.x cadence. Pre-1.0 software is not held to strict semver-minor signaling, and the user has explicitly chosen continuity over a precedent-setting minor bump.
- **Floor-bump every package with any engine dep, but version-bump only by public-contract change.** A `>=0.0.7` floor on test-group dependencies is a defensive pin that prevents `uv sync --all-groups` from resolving to an old engine. It is not itself a public-contract change for the package declaring it. Per user policy, that means `engineadapter` is the only consumer that increments its own version; `naive` and `testing` only edit their dependency tables.

### Preseeded-Test Risk Assessment

The user flagged that this change "may alter the preseeded automation tests" because cards are dealt differently. Static analysis suggests this risk is **low**, with one important caveat:

- **Initial hands are unchanged.** `Round.__post_init__` deals each player `HAND_SIZE` cards in `player_info` order before any DISCARD logic runs. The bug is in `active_player`, not in `_deck.draw`. Initial hand contents are identical seed-for-seed.
- **Deck position at start of TRICKS is unchanged for `arrange.discard`.** Because `arrange.discard` always passes `Discard(..., [])`, the deck's `pulled` counter does not advance during the test-time discard phase. Tests starting at `Status.TRICKS` see identical deck state as before.
- **Tests passing non-empty discard cards through `Game.act` directly *would* see different replacement cards** — because the deck position advances differently if a different player goes first. A grep for `Discard(...)` calls in test files shows all production-test invocations use empty lists or are happy-path single-actor cases (`test_discard_whole_hand`, `test_discard_part_of_hand`) where the actor in question is whoever the engine identifies as `active_player` — which is now the dealer rather than the seat after, but those tests don't pin specific card identities.
- **Consumer assertions on `_discards` order:** a code-wide grep finds **no** test asserting `_discards[0].identifier`, `_discards[i]`, or anything else order-dependent on the discard list. Only `engineadapter:201-204` consumes `discards`, and it does so order-agnostically.
- **The one residual risk:** any test (especially `test_round_scoring.py`, `test_game_scoring.py`, naive's `test_automated_play.py`) that runs a *full* round end-to-end and asserts on a final score, winner identity, or specific card play. These tests rely on the trick phase, which runs against unchanged hands and unchanged first-trick lead — so logically they should be unaffected. **But this can only be confirmed empirically by running the suite.** The implementer must verify this and treat any breakage as either (a) a real test that needs a new seed or assertion, or (b) a sign that this static analysis missed something and the implementer should pause and re-investigate.

---

## Open Questions

### Resolved During Planning

- Does "take first" mean "lead the first trick"? — No. Per user clarification, "take" refers to drawing replacement cards from the deck. Drawing is already inline in `__discard`, so fixing discard order fixes draw order.
- Does the state package need an `active_seat` field to gate discard availability properly? — Out of scope for this fix. The pre-existing leak (all callers see discard subsets in DISCARD status) is documented as a known limitation but not addressed here.
- Patch or minor bump on engine? — Patch (0.0.6 → 0.0.7). User direction.
- Which consumers floor-bump and which version-bump? — All packages with an engine dep (production or test-group) floor-bump to `>=0.0.7,<1.0.0`. Only `engineadapter` version-bumps; `naive` and `testing` do not, because their public contracts are unchanged per user policy.

### Deferred to Implementation

- **Does the full test suite still pass after the engine fix?** Static analysis indicates yes — initial hands and TRICKS-start deck state are unchanged for the existing test seeds, and no test asserts `_discards` order. Empirical confirmation via `uv run pytest` is the verification step in U1. If a preseeded scoring or naive-play test breaks, the implementer should (a) inspect the failure to confirm it is a seed-dependent ordering issue rather than a real regression, (b) update seeds or assertions only if the failure is genuinely cosmetic (different card now wins a trick because of a different replacement-card draw), and (c) flag it back to the user if the failure suggests this static analysis was wrong.

---

## Implementation Units

- U1. **Make the dealer the first active player in DISCARD**

**Goal:** When the DISCARD phase begins (no discards have been recorded yet), `Round.active_player` returns the dealer instead of the player clockwise of the dealer. Subsequent discards continue clockwise from the dealer.

**Requirements:** R1, R2, R3, R4, R5.

**Dependencies:** None.

**Files:**
- Modify: `packages/hundredandten-engine/src/hundredandten/engine/round.py`
- Test: `packages/hundredandten-engine/tests/game/test_discard.py`

**Approach:**
- In the `Status.DISCARD` branch of `Round.active_player` (`round.py:117-124`), short-circuit when `self._discards` is empty: return `self.dealer` directly. Otherwise (one or more discards already recorded), return `player_after(self.players, self._discards[-1].identifier)`. This preserves the existing clockwise progression and only changes the seed of that progression.
- Do not introduce a `player_before` helper. The short-circuit is clearer at a single callsite.
- Leave `__discard`, `__end_discard`, `__new_trick`, and `status` derivation untouched.
- Add a brief inline comment on the new branch explaining *why* DISCARD differs from BIDDING — that the dealer is the actual first actor in DISCARD, not a synthetic "last X" placeholder. This prevents future contributors from re-mirroring the BIDDING idiom.

**Patterns to follow:**
- The existing branching style in `Round.active_player` — guard on `self.status`, assert `self.active_bidder`, then derive the next player.

**Test scenarios:**
- Happy path — `Covers R1.` `arrange.game(Status.DISCARD)` produces a game whose `active_round.active_player` equals `active_round.dealer`. Assert by identifier comparison.
- Happy path — `Covers R2.` After the dealer discards an empty list, the next `active_round.active_player` equals `player_after(active_round.players, dealer.identifier)`. Continue: after that player discards, the next active player is two seats clockwise from the dealer. Verify the full clockwise rotation through all four players and that the round transitions to `Status.TRICKS` when the fourth (the player counter-clockwise of the dealer) discards.
- Happy path — `Covers R3.` After the dealer discards `len == 2` cards, the dealer's hand size is back to `HAND_SIZE`, the two original cards are gone, and two new cards are present. (This is essentially `test_discard_part_of_hand` reframed against the dealer specifically; can be merged with the R1 assertion to avoid duplication.)
- Edge case — Discarding zero cards as the dealer is still valid and advances the active player to the next seat clockwise. Mirrors `arrange.discard`'s usage of `Discard(..., [])`.
- Error path — A non-dealer player attempting to discard at the start of DISCARD raises `HundredAndTenError`. Add this alongside the existing `test_cant_discard_when_not_active` (which today picks `inactive_players[0]` without identity-checking against the dealer). The new assertion: pick the player who *was* active under the old rule (i.e., `player_after(players, dealer.identifier)`) and verify they cannot discard yet.
- Integration — `Covers R4.` `arrange.game(Status.TRICKS)`, which calls `arrange.discard` internally, still produces a game in `Status.TRICKS` with one empty active trick and an `active_player` equal to `player_after(players, active_bidder.identifier)`. This guards R5 transitively: `test_play_first_card_of_round` (in `test_play_card.py`) must continue to pass without modification.

**Verification:**
- `uv run pytest packages/hundredandten-engine/tests/game/test_discard.py` passes, including the new dealer-first assertions.
- `uv run pytest packages/hundredandten-engine/tests/game/test_play_card.py::TestPlayCard::test_play_first_card_of_round` passes unchanged — confirming first-trick lead is untouched.
- **Full suite passes empirically:** `uv run pytest`. Particular attention to preseeded tests in `packages/hundredandten-engine/tests/game/test_round_scoring.py`, `test_game_scoring.py`, and `packages/hundredandten-automation-naive/tests/naive/test_automated_play.py`. If any of these break, see "Deferred to Implementation" for diagnostic steps.
- 100% coverage maintained: `uv run coverage run -m pytest && uv run coverage report -m`.
- Lint and types clean: `uv run black .`, `uv run ruff check --fix`, `uv run pyright`.

---

- U2. **Bump `hundredandten-engine` to 0.0.7**

**Goal:** Increment `hundredandten-engine` from 0.0.6 to 0.0.7 to mark the user-observable behavior change in DISCARD turn order.

**Requirements:** R6.

**Dependencies:** U1 (the behavior change must be in place before tagging a new version).

**Files:**
- Modify: `packages/hundredandten-engine/pyproject.toml` (`version` field, line 8).

**Approach:**
- Single-line edit: change `version = "0.0.6"` to `version = "0.0.7"`. No other change to the engine's pyproject.

**Patterns to follow:**
- Existing 0.0.x patch increments throughout the workspace (every package has used patch-level bumps only). See `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md` for the prior pattern of bumping a package version when republishing.

**Test scenarios:**
- Test expectation: none — version-string change only, no behavioral surface.

**Verification:**
- `uv build --all-packages` succeeds and produces a sdist/wheel with `0.0.7` in the filename for the engine package.
- `grep '^version' packages/hundredandten-engine/pyproject.toml` reports `0.0.7`.

---

- U3. **Raise engine floors on every consumer; bump `engineadapter` version**

**Goal:** Every package that depends on `hundredandten-engine` (production or test-group) requires `>=0.0.7,<1.0.0`, so no consumer can be paired with the buggy engine. Bump `hundredandten-automation-engineadapter`'s own version because its public contract — engine orchestration via `EngineAdapter` — produces observably different behavior. Do **not** bump `hundredandten-automation-naive` or `hundredandten-testing` (public contracts unchanged; the floor change there is a test-dep or internal-helper concern only).

**Requirements:** R7, R8.

**Dependencies:** U2 (the engine 0.0.7 must exist as a published version target before consumers can floor on it).

**Files:**
- Modify: `packages/hundredandten-automation-engineadapter/pyproject.toml`
  - Production dep: `hundredandten-engine>=0.0.5,<1.0.0` → `hundredandten-engine>=0.0.7,<1.0.0`.
  - Version: `0.0.5` → `0.0.6`.
- Modify: `packages/hundredandten-automation-naive/pyproject.toml`
  - Test-group dep: `hundredandten-engine>=0.0.0,<1.0.0` → `hundredandten-engine>=0.0.7,<1.0.0`.
  - Test-group dep: `hundredandten-automation-engineadapter>=0.0.0,<1.0.0` → `hundredandten-automation-engineadapter>=0.0.6,<1.0.0` (mirrors the engineadapter bump for consistency, even though it's a test-group floor).
  - Version: unchanged (0.0.5).
- Modify: `packages/hundredandten-testing/pyproject.toml`
  - Production dep: `hundredandten-engine` (unbounded) → `hundredandten-engine>=0.0.7,<1.0.0`.
  - Version: unchanged (0.0.0 — internal package).
- Note: `packages/hundredandten-deck/pyproject.toml` and `packages/hundredandten-state/pyproject.toml` declare no engine dependency. **Do not modify either file.**

**Approach:**
- Per-file edits are mechanical. Run them in the order listed above so the rationale of each change is reviewable independently.
- For `hundredandten-testing`, also tighten the `hundredandten-state` dep at the same time only if it is also unbounded *and* the audit confirms it should match the workspace minimum — otherwise leave it alone. (Today both `hundredandten-engine` and `hundredandten-state` are unbounded in testing. Tighten only `hundredandten-engine` here; leave `hundredandten-state` for a future audit so this change stays focused.)
- After edits, regenerate the workspace lockfile: `uv lock` (no `--upgrade`, so existing pins for unrelated packages are preserved). Confirm the resulting `uv.lock` reflects the new floors and that the workspace still resolves cleanly.

**Patterns to follow:**
- Existing dep-pin format throughout the workspace: `<name>>=<floor>,<1.0.0`. Match exactly — including whitespace and comma placement — for consistency with other packages.

**Test scenarios:**
- Test expectation: none — pyproject metadata edits only, no behavioral surface. The behavioral guarantees these floors enforce are validated by U1's test scenarios.

**Verification:**
- `grep -A 5 dependencies packages/hundredandten-automation-engineadapter/pyproject.toml` shows `hundredandten-engine>=0.0.7,<1.0.0` and version `0.0.6`.
- `grep -A 5 'hundredandten-engine' packages/hundredandten-automation-naive/pyproject.toml` shows the test-group floor at `>=0.0.7,<1.0.0`.
- `grep -A 5 dependencies packages/hundredandten-testing/pyproject.toml` shows the production dep floor at `>=0.0.7,<1.0.0`.
- `uv sync --all-groups --all-packages` succeeds.
- `uv run pytest` passes (workspace-mode resolution should pick up the in-tree engine 0.0.7 from U2 regardless of floor).
- `uv build --all-packages` produces `0.0.6` artifacts for engineadapter, `0.0.5` artifacts for naive (unchanged), `0.0.0` for testing (unchanged).

---

## System-Wide Impact

- **Interaction graph:** `Round.active_player` is read by `Round.act` (validation), `Round.inactive_players`, `arrange.discard` (testing helper), and indirectly by every engineadapter and naive test that walks a game forward via `arrange.game(Status.X)`. None of these consumers pin "the seat after the dealer discards first"; they all key off whatever `active_player` returns. The change is therefore behaviorally local.
- **Error propagation:** Unchanged. `__discard` still raises `HundredAndTenError` when a non-active player attempts to discard; only the identity of "the active player" shifts at the start of the phase.
- **State lifecycle risks:** None. `_discards` is still appended in the same order it was before, just with a different first element. No state-package field encodes discard order externally.
- **API surface parity:** `GameState` does not expose an active-discarder seat, so no observation-layer field needs updating. The `EngineAdapter` test suite (`packages/hundredandten-automation-engineadapter/tests/engineadapter/`) does not pin discard turn order; existing seat-rotation tests for `bidder_seat` and `dealer_seat` continue to hold.
- **Integration coverage:** The full-round walk in `arrange.__get_won_game` (`arrange.py:157-164`) loops `bid → select_trump → discard → play_round` until `Status.WON`. Because `arrange.discard` passes empty-list discards (advancing the deck by 0), the loop converges to identical TRICKS-phase state. Any naive automation test that runs to completion (e.g., `packages/hundredandten-automation-naive/tests/naive/test_automated_play.py`) inherits the new order transparently — but this is a static-analysis claim, not an empirical one. U1's verification step confirms it.
- **Workspace dependency graph:** After U2 and U3, the workspace looks like this for engine-floor purposes:
  - `hundredandten-engine` 0.0.7 (bumped)
  - `hundredandten-automation-engineadapter` 0.0.6 (bumped, floors engine 0.0.7)
  - `hundredandten-automation-naive` 0.0.5 (unchanged version, test-group floors engine 0.0.7 and engineadapter 0.0.6)
  - `hundredandten-testing` 0.0.0 (unchanged version, production floor engine 0.0.7)
  - `hundredandten-state` 0.0.6 (untouched — no engine dep)
  - `hundredandten-deck` 0.0.3 (untouched — no engine dep)
- **Unchanged invariants:** First-trick lead remains `player_after(active_bidder)`. Dealer rotation between rounds remains `player_after(current_dealer)`. Bidding turn order remains "start with the player after the dealer". The DISCARD phase entry condition (trump has been selected and not all players have discarded) and exit condition (`len(discards) == len(players)`) are unchanged. `hundredandten-state` and `hundredandten-deck` are entirely unaffected — their public contracts are preserved bit-for-bit.

---

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| A hidden test elsewhere pins "player after the dealer discards first" | Low likelihood — the research pass found only `test_cant_discard_when_not_active` touching the discard active player, and it uses `inactive_players[0]` without identity-checking. The full-suite run during U1 verification is the safety net. |
| Preseeded full-round tests (`test_round_scoring`, `test_game_scoring`, `test_automated_play`) break because replacement-card order is different | Static analysis says no — `arrange.discard` passes empty discards, so the deck position at TRICKS start is identical. But the only definitive answer is the test run. The U1 "Deferred to Implementation" note covers diagnostic steps if a test does break. |
| A consumer floor is missed and gets paired with engine 0.0.6 from PyPI | U3 covers all three engine consumers (engineadapter production, naive test-group, testing production). The verification step `grep`s each pyproject to confirm. |
| Future contributors mirror the BIDDING branch's "treat dealer as last X" idiom into DISCARD again | U1 includes an inline code comment explaining *why* DISCARD differs from BIDDING. |
| `uv build --all-packages` fails after version bump because of a stale build cache | Documented pattern from `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`. Clean rebuild (`rm -rf dist/ && uv build --all-packages`) resolves it if it occurs. |

---

## Documentation / Operational Notes

- No README, AGENTS.md, or `docs/solutions/` updates required by this fix. If the dealer-first rule is later cited in a learning doc (e.g., a future "discard turn order" reference), update at that point.
- Issue #186 should be referenced in the commit message and closed by the PR.
- Engine 0.0.7, engineadapter 0.0.6, and any new floors will need to be published to PyPI per the project's existing release process. That is an operational follow-up after merge, not part of this plan's implementation.
- Recommended commit shape: keep U1 as one commit (engine fix + tests), U2 as one commit (engine version bump), and U3 as one commit (consumer floors + engineadapter version bump). Three small, reviewable commits make the bisect surface clean if a regression is discovered later.

---

## Sources & References

- Issue: https://github.com/seamuslowry/hundred-and-ten/issues/186
- Change site (engine): `packages/hundredandten-engine/src/hundredandten/engine/round.py:117-124`
- Test site (engine): `packages/hundredandten-engine/tests/game/test_discard.py`
- Untouched but adjacent: `packages/hundredandten-engine/src/hundredandten/engine/round.py:127-139` (first-trick lead), `packages/hundredandten-engine/tests/game/test_play_card.py:26-47` (pins first-trick lead).
- Versioning sites: `packages/hundredandten-engine/pyproject.toml`, `packages/hundredandten-automation-engineadapter/pyproject.toml`, `packages/hundredandten-automation-naive/pyproject.toml`, `packages/hundredandten-testing/pyproject.toml`.
- Related learning: `docs/solutions/logic-errors/discarded-seat-field-always-zero-2026-04-17.md`.
- Related learning (versioning operational pattern): `docs/solutions/build-errors/pypi-sha-mismatch-version-bump-required-2026-04-12.md`.
