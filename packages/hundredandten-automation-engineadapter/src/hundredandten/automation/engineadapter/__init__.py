"""Engine adapter for wiring automation strategies to the Hundred and Ten game engine"""

from typing import Callable

from hundredandten.deck import Card, ALL_CARDS
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
from hundredandten.state import (
    AvailableAction,
    AvailableBid,
    AvailableDiscard,
    AvailablePlay,
    AvailableSelectTrump,
    BidAmount,
    BiddingState,
    BidEvent,
    CardKnowledge,
    CompletedTrick,
    Discarded,
    GameState,
    InHand,
    Played,
    Status,
    TableInfo,
    TrickPlay,
    TrickState,
    Unknown,
)


class UnavailableActionError(Exception):
    """Raised when the decision function returns an action not available to the player"""


class EngineAdapter:
    """Adapter to convert between engine actions and internal available actions"""

    @staticmethod
    def action_for(
        game: Game,
        identifier: str,
        decision_fn: Callable[[GameState], AvailableAction],
    ) -> Action:
        """
        Return an action for the current player, using the decision function.
        Returns None if the decision function returns None.
        Raises UnavailableActionError if the decision function returns an action
        not available to the player.
        """
        state = EngineAdapter.state_from_engine(game, identifier)
        suggested_action = decision_fn(state)
        if suggested_action not in state.available_actions:
            raise UnavailableActionError(f"""
                decision_fn returned an action {suggested_action}
                not in available_actions: {state.available_actions}
                game state: {state}
                """)
        return EngineAdapter.available_action_for_player(suggested_action, identifier)

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
                    card_status_by_card[card] = Discarded()

        unknown = Unknown()
        return tuple(
            CardKnowledge(
                card=card,
                status=card_status_by_card.get(card, unknown),
            )
            for card in ALL_CARDS
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
