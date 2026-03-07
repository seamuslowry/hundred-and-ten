"""Represent the state of a game as observed by a single player"""

from dataclasses import dataclass
from typing import Optional, Union

from hundredandten.actions import Action, Bid, Discard, Play, SelectTrump
from hundredandten.constants import BidAmount, RoundStatus, SelectableSuit
from hundredandten.deck import Card


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


CardStatus = Union[InHand, Played, Discarded, Unknown]


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
    bidder_seat: Optional[int]
    scores: tuple[int, ...]


@dataclass(frozen=True)
class BiddingState:
    """Bidding phase state including the resulting trump"""

    bid_history: tuple[BidEvent, ...]
    active_bid: Optional[BidAmount]
    trump: Optional[SelectableSuit]


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
    status: RoundStatus

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

    # Legal actions for the active player
    available_actions: tuple[Action, ...]

    @property
    def available_bids(self) -> tuple[Bid, ...]:
        """Return only Bid actions from available_actions"""
        return tuple(a for a in self.available_actions if isinstance(a, Bid))

    @property
    def available_trump_selections(self) -> tuple[SelectTrump, ...]:
        """Return only SelectTrump actions from available_actions"""
        return tuple(a for a in self.available_actions if isinstance(a, SelectTrump))

    @property
    def available_discards(self) -> tuple[Discard, ...]:
        """Return only Discard actions from available_actions"""
        return tuple(a for a in self.available_actions if isinstance(a, Discard))

    @property
    def available_plays(self) -> tuple[Play, ...]:
        """Return only Play actions from available_actions"""
        return tuple(a for a in self.available_actions if isinstance(a, Play))

    @property
    def is_bidder(self) -> bool:
        """Return True if the active player is the bidder"""
        return self.table.bidder_seat == 0

    @property
    def is_dealer(self) -> bool:
        """Return True if the active player is the dealer"""
        return self.table.dealer_seat == 0

    @property
    def num_players(self) -> int:
        """Return the number of players at the table"""
        return self.table.num_players

    @property
    def dealer_seat(self) -> int:
        """Return the dealer seat relative to the active player"""
        return self.table.dealer_seat

    @property
    def bidder_seat(self) -> Optional[int]:
        """Return the bidder seat relative to the active player"""
        return self.table.bidder_seat

    @property
    def scores(self) -> tuple[int, ...]:
        """Return scores ordered by relative seat (index 0 = self, increasing clockwise)"""
        return self.table.scores

    @property
    def bid_history(self) -> tuple[BidEvent, ...]:
        """Return bids placed so far in relative-seat order"""
        return self.bidding.bid_history

    @property
    def active_bid(self) -> Optional[BidAmount]:
        """Return the current high bid"""
        return self.bidding.active_bid

    @property
    def trump(self) -> Optional[SelectableSuit]:
        """Return the selected trump suit"""
        return self.bidding.trump

    @property
    def completed_tricks(self) -> tuple[CompletedTrick, ...]:
        """Return completed tricks with relative winner seats"""
        return self.tricks.completed_tricks

    @property
    def current_trick_plays(self) -> tuple[TrickPlay, ...]:
        """Return plays in the current in-progress trick"""
        return self.tricks.current_trick_plays
