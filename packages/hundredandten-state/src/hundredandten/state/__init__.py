"""Represent the state of a game as observed by a single player"""

from dataclasses import dataclass
from enum import Enum, IntEnum
from itertools import combinations

from hundredandten.deck import Card, SelectableSuit


class StateError(Exception):
    """Raised when a state operation cannot be completed"""


class Status(Enum):
    """Game status as observed by a player"""

    BIDDING = "BIDDING"
    TRUMP_SELECTION = "TRUMP_SELECTION"
    TRICKS = "TRICKS"
    DISCARD = "DISCARD"
    WON = "WON"


class BidAmount(IntEnum):
    """Possible bid amounts"""

    SHOOT_THE_MOON = 60
    THIRTY = 30
    TWENTY_FIVE = 25
    TWENTY = 20
    FIFTEEN = 15
    PASS = 0


@dataclass(frozen=True)
class AvailableBid:
    """
    An available bid action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    amount: BidAmount


@dataclass(frozen=True, eq=False)
class AvailableDiscard:
    """
    An available discard action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.

    Equality is order-insensitive: two AvailableDiscard instances are equal
    if they contain the same cards regardless of order.
    """

    cards: tuple[Card, ...]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AvailableDiscard):
            return NotImplemented
        return frozenset(self.cards) == frozenset(other.cards)

    def __hash__(self) -> int:
        return hash(frozenset(self.cards))


@dataclass(frozen=True)
class AvailableSelectTrump:
    """
    An available trump selection action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    suit: SelectableSuit


@dataclass(frozen=True)
class AvailablePlay:
    """
    An available play action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    card: Card


type AvailableAction = AvailableBid | AvailableSelectTrump | AvailableDiscard | AvailablePlay


@dataclass(frozen=True)
class InHand:
    """Card is in this player's hand"""


@dataclass(frozen=True)
class Played:
    """Card was played in a specific trick by a specific seat"""

    trick_index: int
    seat: int


@dataclass(frozen=True)
class Discarded:
    """Card was discarded by a specific seat"""

    seat: int


@dataclass(frozen=True)
class Unknown:
    """Card location is not known to this player"""


type CardStatus = InHand | Played | Discarded | Unknown


@dataclass(frozen=True)
class CardKnowledge:
    """Hold the known information about a card and its status"""

    card: Card
    status: CardStatus


@dataclass(frozen=True)
class BidEvent:
    """A bid placed by a player at a relative seat"""

    seat: int
    amount: BidAmount


@dataclass(frozen=True)
class TrickPlay:
    """A card played in a trick by a player at a relative seat"""

    seat: int
    card: Card


@dataclass(frozen=True)
class CompletedTrick:
    """A completed trick with all plays and the winner"""

    plays: tuple[TrickPlay, ...]
    winner_seat: int


@dataclass(frozen=True)
class TableInfo:
    """Table shape and positions.

    scores is ordered by relative seat (index 0 = self, increasing clockwise).
    """

    num_players: int
    dealer_seat: int
    bidder_seat: int | None
    scores: tuple[int, ...]


@dataclass(frozen=True)
class BiddingState:
    """Bidding phase state including the resulting trump"""

    bid_history: tuple[BidEvent, ...]
    active_bid: BidAmount | None
    trump: SelectableSuit | None


@dataclass(frozen=True)
class TrickState:
    """Trick phase state"""

    completed_tricks: tuple[CompletedTrick, ...]
    current_trick_plays: tuple[TrickPlay, ...]


@dataclass(frozen=True)
class GameState:
    """The game state as observed by the active player at decision time.

    All positions are seat-relative: self is always seat 0,
    and other seats are numbered clockwise.
    """

    # Phase
    status: Status

    # Table shape and relative positions/scores
    table: TableInfo

    # Player's own hand
    hand: tuple[Card, ...]

    # Bidding and trump state
    bidding: BiddingState

    # Trick state
    tricks: TrickState

    # Card knowledge (all 53 cards)
    cards: tuple[CardKnowledge, ...]

    @property
    def available_actions(self) -> tuple[AvailableAction, ...]:
        """Return all available actions"""
        match self.status:
            case Status.BIDDING:
                if any(
                    b == BidEvent(0, BidAmount.PASS) for b in self.bidding.bid_history
                ):
                    return ()

                dealer_steal = (
                    [self.bidding.active_bid]
                    if self.bidding.active_bid and self.table.dealer_seat == 0
                    else []
                )
                higher_bids = [
                    a
                    for a in BidAmount
                    if a.value > (self.bidding.active_bid or BidAmount.PASS).value
                ]

                return tuple(
                    AvailableBid(amount=a)
                    for a in [BidAmount.PASS, *dealer_steal, *higher_bids]
                )
            case Status.TRUMP_SELECTION:
                return (
                    tuple(AvailableSelectTrump(suit=s) for s in SelectableSuit)
                    if self.table.bidder_seat == 0
                    else ()
                )
            case Status.DISCARD:
                hand_list = list(self.hand)
                return tuple(
                    AvailableDiscard(subset)
                    for r in range(len(hand_list) + 1)
                    for subset in combinations(hand_list, r)
                )
            case Status.TRICKS:
                bleeding = bool(self.tricks.current_trick_plays) and (
                    self.tricks.current_trick_plays[0].card.trump_for_selection(
                        self.bidding.trump
                    )
                )
                player_trumps = [
                    c for c in self.hand if c.trump_for_selection(self.bidding.trump)
                ]

                playable = (
                    self.hand if (not bleeding or not player_trumps) else player_trumps
                )

                return tuple(AvailablePlay(card) for card in playable)
            case _:
                return ()

    @property
    def available_bids(self) -> tuple[AvailableBid, ...]:
        """Return only Bid actions from available_actions"""
        return tuple(a for a in self.available_actions if isinstance(a, AvailableBid))

    @property
    def available_trump_selections(self) -> tuple[AvailableSelectTrump, ...]:
        """Return only SelectTrump actions from available_actions"""
        return tuple(
            a for a in self.available_actions if isinstance(a, AvailableSelectTrump)
        )

    @property
    def available_discards(self) -> tuple[AvailableDiscard, ...]:
        """Return only Discard actions from available_actions"""
        return tuple(
            a for a in self.available_actions if isinstance(a, AvailableDiscard)
        )

    @property
    def available_plays(self) -> tuple[AvailablePlay, ...]:
        """Return only Play actions from available_actions"""
        return tuple(a for a in self.available_actions if isinstance(a, AvailablePlay))
