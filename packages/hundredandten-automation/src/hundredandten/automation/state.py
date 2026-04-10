"""Represent the state of a game as observed by a single player"""

from dataclasses import dataclass
from typing import Optional, Self, Union

from hundredandten.engine import Game
from hundredandten.engine.actions import (
    Action,
    Bid,
    Discard,
    Play,
    SelectTrump,
)
from hundredandten.engine.constants import BidAmount, SelectableSuit, Status
from hundredandten.engine.deck import Card, defined_cards
from hundredandten.engine.player import RoundPlayer, player_by_identifier
from hundredandten.engine.round import Round


@dataclass(frozen=True)
class AvailableBid:
    """
    An available bid action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    amount: BidAmount

    @classmethod
    def from_engine(cls, b: Bid) -> Self:
        """Create a player-agnostic Bid representation from a player-aware representation"""
        return cls(b.amount)

    def for_player(self, identifier: str) -> Bid:
        """Create a player-aware Bid representation from a player-agnostic representation"""
        return Bid(identifier=identifier, amount=self.amount)


@dataclass(frozen=True)
class AvailableDiscard:
    """
    An available discard action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    cards: tuple[Card, ...]

    @classmethod
    def from_engine(cls, d: Discard) -> Self:
        """Create a player-agnostic Discard representation from a player-aware representation"""
        return cls(tuple(d.cards))

    def for_player(self, identifier: str) -> Discard:
        """Create a player-aware Discard representation from a player-agnostic representation"""
        return Discard(identifier=identifier, cards=list(self.cards))


@dataclass(frozen=True)
class AvailableSelectTrump:
    """
    An available trump selection action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    suit: SelectableSuit

    @classmethod
    def from_engine(cls, b: SelectTrump) -> Self:
        """Create a player-agnostic SelectTrump representation from a player-aware representation"""
        return cls(b.suit)

    def for_player(self, identifier: str) -> SelectTrump:
        """Create a player-aware SelectTrump representation from a player-agnostic representation"""
        return SelectTrump(identifier=identifier, suit=self.suit)


@dataclass(frozen=True)
class AvailablePlay:
    """
    An available play action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    card: Card

    @classmethod
    def from_engine(cls, b: Play) -> Self:
        """Create a player-agnostic Play representation from a player-aware representation"""
        return cls(b.card)

    def for_player(self, identifier: str) -> Play:
        """Create a player-aware Play representation from a player-agnostic representation"""
        return Play(identifier=identifier, card=self.card)


type AvailableAction = Union[
    AvailableBid, AvailableSelectTrump, AvailableDiscard, AvailablePlay
]


def _available_action_from_engine(a: Action) -> AvailableAction:
    """Create a player-agnostic Action from a player-aware Action."""
    match a:
        case Bid():
            return AvailableBid.from_engine(a)
        case SelectTrump():
            return AvailableSelectTrump.from_engine(a)
        case Discard():
            return AvailableDiscard.from_engine(a)
        case Play():
            return AvailablePlay.from_engine(a)
    raise ValueError(
        f"Could not convert engine action {a} to an internal action"
    )  # pragma: no cover


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

    # Legal actions for the active player
    available_actions: tuple[AvailableAction, ...]

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

    @property
    def is_bidder(self) -> bool:
        """Return True if the active player is the bidder"""
        return self.table.bidder_seat == 0

    @property
    def is_dealer(self) -> bool:
        """Return True if the active player is the dealer"""
        return self.table.dealer_seat == 0

    @classmethod
    def from_game(cls, game: Game, identifier: str) -> Self:
        """Build a GameState observation for the identified player.

        All seats are rotated so that the requesting player is seat 0.
        Cards the player cannot see are marked Unknown.
        """
        game_round = game.active_round
        players = game_round.players
        num_players = len(players)
        non_relative_seat_by_identifier = {
            round_player.identifier: index for index, round_player in enumerate(players)
        }
        player = player_by_identifier(players, identifier)
        player_index = non_relative_seat_by_identifier[identifier]

        current_scores = game.scores
        table = TableInfo(
            num_players=num_players,
            dealer_seat=GameState.__relative_seat(
                non_relative_seat_by_identifier,
                player.identifier,
                game_round.dealer.identifier,
                num_players,
            ),
            bidder_seat=(
                GameState.__relative_seat(
                    non_relative_seat_by_identifier,
                    player.identifier,
                    game_round.active_bidder.identifier,
                    num_players,
                )
                if game_round.active_bidder
                else None
            ),
            scores=tuple(
                current_scores.get(
                    players[(player_index + i) % num_players].identifier, 0
                )
                for i in range(num_players)
            ),
        )
        bidding = BiddingState(
            bid_history=tuple(
                BidEvent(
                    seat=GameState.__relative_seat(
                        non_relative_seat_by_identifier,
                        player.identifier,
                        bid.identifier,
                        num_players,
                    ),
                    amount=bid.amount,
                )
                for bid in game_round.bids
            ),
            active_bid=game_round.active_bid,
            trump=game_round.trump,
        )

        return cls(
            status=game.status,
            table=table,
            hand=tuple(player.hand),
            bidding=bidding,
            tricks=GameState.__build_trick_state(
                game_round, player, non_relative_seat_by_identifier
            ),
            cards=GameState.__build_card_knowledge(
                game_round, player, non_relative_seat_by_identifier
            ),
            available_actions=tuple(
                _available_action_from_engine(a)
                for a in game.available_actions(identifier)
            ),
        )

    @staticmethod
    def __build_card_knowledge(
        game_round: Round,
        player: RoundPlayer,
        non_relative_seat_by_identifier: dict[str, int],
    ) -> tuple[CardKnowledge, ...]:
        card_status_by_card: dict[Card, InHand | Played | Discarded] = {}
        num_players = len(game_round.players)

        for card in player.hand:
            card_status_by_card[card] = InHand()

        for trick_index, trick in enumerate(game_round.tricks):
            for play in trick.plays:
                card_status_by_card[play.card] = Played(
                    trick_index=trick_index,
                    seat=GameState.__relative_seat(
                        non_relative_seat_by_identifier,
                        player.identifier,
                        play.identifier,
                        num_players,
                    ),
                )

        for discard in game_round.discards:
            if discard.identifier == player.identifier:
                for card in discard.cards:
                    card_status_by_card[card] = Discarded(seat=0)

        unknown = Unknown()
        return tuple(
            CardKnowledge(
                card=card,
                status=card_status_by_card.get(card, unknown),
            )
            for card in defined_cards
        )

    @staticmethod
    def __build_trick_state(
        game_round: Round,
        player: RoundPlayer,
        non_relative_seat_by_identifier: dict[str, int],
    ) -> TrickState:
        completed_tricks: list[CompletedTrick] = []
        current_trick_plays: tuple[TrickPlay, ...] = ()
        num_players = len(game_round.players)

        for trick in game_round.tricks:
            trick_plays = tuple(
                TrickPlay(
                    seat=GameState.__relative_seat(
                        non_relative_seat_by_identifier,
                        player.identifier,
                        play.identifier,
                        num_players,
                    ),
                    card=play.card,
                )
                for play in trick.plays
            )
            if len(trick.plays) == len(game_round.players):
                winner_play = trick.winning_play
                assert winner_play is not None
                completed_tricks.append(
                    CompletedTrick(
                        plays=trick_plays,
                        winner_seat=GameState.__relative_seat(
                            non_relative_seat_by_identifier,
                            player.identifier,
                            winner_play.identifier,
                            num_players,
                        ),
                    )
                )
            else:
                current_trick_plays = trick_plays

        return TrickState(
            completed_tricks=tuple(completed_tricks),
            current_trick_plays=current_trick_plays,
        )

    @staticmethod
    def __relative_seat(
        non_relative_seat_by_identifier: dict[str, int],
        player_identifier: str,
        other_identifier: str,
        num_players: int,
    ) -> int:
        return (
            non_relative_seat_by_identifier[other_identifier]
            - non_relative_seat_by_identifier[player_identifier]
        ) % num_players
