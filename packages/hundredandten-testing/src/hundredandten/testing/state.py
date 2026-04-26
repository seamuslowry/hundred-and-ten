"""Builders for constructing GameState objects directly, without the engine.

All builders provide sensible defaults so tests only need to specify the fields
relevant to the behaviour under test.
"""

from hundredandten.deck import Card, SelectableSuit
from hundredandten.state import (
    BidAmount,
    BiddingState,
    BidEvent,
    GameState,
    Status,
    TableInfo,
    TrickState,
)


def table(
    *,
    num_players: int = 4,
    dealer_seat: int = 1,
    bidder_seat: int | None = None,
    scores: tuple[int, ...] | None = None,
) -> TableInfo:
    """Build a TableInfo with sensible defaults."""
    return TableInfo(
        num_players=num_players,
        dealer_seat=dealer_seat,
        bidder_seat=bidder_seat,
        scores=scores if scores is not None else tuple(0 for _ in range(num_players)),
    )


def bidding(
    *,
    bid_history: tuple[BidEvent, ...] = (),
    active_bid: BidAmount | None = None,
    trump: SelectableSuit | None = None,
) -> BiddingState:
    """Build a BiddingState with sensible defaults."""
    return BiddingState(bid_history=bid_history, active_bid=active_bid, trump=trump)


def tricks() -> TrickState:
    """Build an empty TrickState."""
    return TrickState(completed_tricks=(), current_trick_plays=())


def game_state(
    *,
    status: Status = Status.BIDDING,
    table_info: TableInfo | None = None,
    hand: tuple[Card, ...] = (),
    bidding_state: BiddingState | None = None,
    trick_state: TrickState | None = None,
) -> GameState:
    """Build a GameState with sensible defaults.

    Pass only the fields relevant to the behaviour under test; everything else
    defaults to a minimal, valid value.
    """
    return GameState(
        status=status,
        table=table_info if table_info is not None else table(),
        hand=hand,
        bidding=bidding_state if bidding_state is not None else bidding(),
        tricks=trick_state if trick_state is not None else tricks(),
        cards=(),
    )
