"""Represent the state of a game as observed by a single player"""

from dataclasses import dataclass
from enum import Enum, IntEnum
from itertools import combinations

from hundredandten.deck import Card, SelectableSuit, defined_cards
from hundredandten.engine import Game
from hundredandten.engine.actions import (
    Action,
    Bid,
    Discard,
    Play,
    SelectTrump,
)
from hundredandten.engine.constants import BidAmount as EngineBidAmount
from hundredandten.engine.player import RoundPlayer, player_by_identifier
from hundredandten.engine.round import Round


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


@dataclass(frozen=True)
class AvailableDiscard:
    """
    An available discard action.
    It is agnostic of the player since available actions are always for
    the active player. And game state is more paramaterizable without
    identifying player data.
    """

    cards: tuple[Card, ...]


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

                bids = [
                    BidAmount.PASS
                    * (
                        [self.bidding.active_bid]
                        if self.bidding.active_bid and self.table.dealer_seat == 0
                        else []
                    ),
                    *(
                        a
                        for a in BidAmount
                        if a.value > (self.bidding.active_bid or BidAmount.PASS).value
                    ),
                ]

                return tuple(AvailableBid(amount=a) for a in bids)
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
                playable = (
                    self.hand
                    if (
                        not self.tricks.current_trick_plays
                        or self.tricks.current_trick_plays[0].card.trump_for_selection(
                            self.bidding.trump
                        )
                    )
                    else tuple(
                        c
                        for c in self.hand
                        if c.trump_for_selection(self.bidding.trump)
                    )
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


class EngineAdapter:
    """Adapter to convert between engine actions and internal available actions"""

    @staticmethod
    def available_action_from_engine(a: Action) -> AvailableAction:
        """Create a player-agnostic Action from a player-aware Action."""
        match a:
            case Bid():
                return AvailableBid(BidAmount(a.amount))
            case SelectTrump():
                return AvailableSelectTrump(a.suit)
            case Discard():
                return AvailableDiscard(tuple(a.cards))
            case Play():
                return AvailablePlay(a.card)
        raise ValueError(
            f"Could not convert engine action {a} to an internal action"
        )  # pragma: no cover

    @staticmethod
    def available_action_for_player(a: AvailableAction, identifier: str) -> Action:
        """Create a player-aware Action from a player-agnostic Action."""
        match a:
            case AvailableBid():
                return Bid(identifier=identifier, amount=EngineBidAmount(a.amount))
            case AvailableSelectTrump():
                return SelectTrump(identifier=identifier, suit=a.suit)
            case AvailableDiscard():
                return Discard(identifier=identifier, cards=list(a.cards))
            case AvailablePlay():
                return Play(identifier=identifier, card=a.card)
        raise ValueError(
            f"Could not convert internal action {a} to an engine action"
        )  # pragma: no cover

    @staticmethod
    def state_from_engine(game: Game, identifier: str) -> GameState:
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
            dealer_seat=EngineAdapter.__relative_seat(
                non_relative_seat_by_identifier,
                player.identifier,
                game_round.dealer.identifier,
                num_players,
            ),
            bidder_seat=(
                EngineAdapter.__relative_seat(
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
                    seat=EngineAdapter.__relative_seat(
                        non_relative_seat_by_identifier,
                        player.identifier,
                        bid.identifier,
                        num_players,
                    ),
                    amount=BidAmount(bid.amount),
                )
                for bid in game_round.bids
            ),
            active_bid=(
                BidAmount(game_round.active_bid)
                if game_round.active_bid is not None
                else None
            ),
            trump=game_round.trump,
        )

        return GameState(
            status=Status(game.status.name),
            table=table,
            hand=tuple(player.hand),
            bidding=bidding,
            tricks=EngineAdapter.__build_trick_state(
                game_round, player, non_relative_seat_by_identifier
            ),
            cards=EngineAdapter.__build_card_knowledge(
                game_round, player, non_relative_seat_by_identifier
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
                    seat=EngineAdapter.__relative_seat(
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
                    seat=EngineAdapter.__relative_seat(
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
                completed_tricks.append(
                    CompletedTrick(
                        plays=trick_plays,
                        winner_seat=EngineAdapter.__relative_seat(
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
