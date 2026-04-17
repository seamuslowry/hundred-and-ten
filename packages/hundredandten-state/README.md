# hundredandten-state

Player observation layer for the card game Hundred and Ten.

`GameState` is a player-agnostic snapshot of the game at decision time. All seat positions are **relative** — the observing player is always seat 0, with other players numbered clockwise. No player identifiers appear in the state. This design makes `GameState` the natural observation space for automation strategies and future ML training.

`GameState` is constructed by [`EngineAdapter`](../hundredandten-automation-engineadapter/) from a live `Game` object, not built directly.

```python
from hundredandten.automation.engineadapter import EngineAdapter

state = EngineAdapter.state_from_engine(game, 'player_1')

print(state.status)            # Status.BIDDING, TRICKS, etc.
print(state.hand)              # tuple[Card, ...] — this player's hand
print(state.available_actions) # tuple of AvailableBid / AvailablePlay / etc.
print(state.table.scores)      # tuple[int, ...] — scores indexed by relative seat
```

## GameState Structure

| Field | Type | Description |
|-------|------|-------------|
| `status` | `Status` | Current game phase. |
| `table` | `TableInfo` | Seat counts, scores, dealer seat, and bidder seat — all relative. |
| `hand` | `tuple[Card, ...]` | This player's current hand. |
| `bidding` | `BiddingState` | Bid history, active bid amount, and selected trump. |
| `tricks` | `TrickState` | Completed tricks and the current in-progress trick. |
| `cards` | `tuple[CardKnowledge, ...]` | All 53 cards with their known status (`InHand`, `Played`, `Discarded`, or `Unknown`). |

`state.available_actions` returns the legal actions for the active player given the current phase. Convenience properties `available_bids`, `available_trump_selections`, `available_discards`, and `available_plays` filter to a specific action type.

## Exports

### Phase and action types

| Symbol | Description |
|--------|-------------|
| `Status` | Enum: `BIDDING`, `TRUMP_SELECTION`, `DISCARD`, `TRICKS`, `WON`. |
| `BidAmount` | IntEnum of bid values: `FIFTEEN` through `SHOOT_THE_MOON` and `PASS`. |
| `AvailableAction` | Union type: `AvailableBid \| AvailableSelectTrump \| AvailableDiscard \| AvailablePlay`. |
| `AvailableBid` | A bid action with an `amount: BidAmount`. |
| `AvailableSelectTrump` | A trump selection action with a `suit: SelectableSuit`. |
| `AvailableDiscard` | A discard action with `cards: tuple[Card, ...]`. Order-insensitive equality. |
| `AvailablePlay` | A play action with a `card: Card`. |

### State structure types

| Symbol | Description |
|--------|-------------|
| `GameState` | Top-level observation. See structure table above. |
| `TableInfo` | `num_players`, `dealer_seat`, `bidder_seat`, `scores` — all relative. |
| `BiddingState` | `bid_history: tuple[BidEvent, ...]`, `active_bid: BidAmount \| None`, `trump: SelectableSuit \| None`. |
| `TrickState` | `completed_tricks: tuple[CompletedTrick, ...]`, `current_trick_plays: tuple[TrickPlay, ...]`. |
| `BidEvent` | A bid in the history: `seat: int`, `amount: BidAmount`. |
| `TrickPlay` | A card played in a trick: `seat: int`, `card: Card`. |
| `CompletedTrick` | A finished trick: `plays: tuple[TrickPlay, ...]`, `winner_seat: int`. |

### Card knowledge types

| Symbol | Description |
|--------|-------------|
| `CardKnowledge` | Pairs a `card: Card` with its `status: CardStatus`. |
| `CardStatus` | Union type: `InHand \| Played \| Discarded \| Unknown`. |
| `InHand` | Card is in this player's hand. |
| `Played` | Card was played in `trick_index` by relative `seat`. |
| `Discarded` | Card was discarded by this player. |
| `Unknown` | Card location is not visible to this player. |
