"""Represent a game of Hundred and Ten"""

import hashlib
from dataclasses import InitVar, dataclass, field
from itertools import chain, combinations
from random import Random
from typing import Optional, Sequence
from uuid import UUID, uuid4

from hundredandten.actions import Action, Bid, Discard, Play, SelectTrump
from hundredandten.constants import (
    WINNING_SCORE,
    AnyStatus,
    GameStatus,
    RoundStatus,
    SelectableSuit,
)
from hundredandten.decisions import trumps
from hundredandten.deck import Card, defined_cards
from hundredandten.events import Event, GameEnd, GameStart, Score
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.player import (
    AutomatedPlayer,
    Player,
    RoundPlayer,
    player_after,
    player_by_identifier,
)
from hundredandten.round import Round
from hundredandten.state import (
    BiddingState,
    BidEvent,
    CardKnowledge,
    CompletedTrick,
    Discarded,
    GameState,
    InHand,
    Played,
    TableInfo,
    TrickPlay,
    TrickState,
    Unknown,
)


@dataclass
class Game:
    """A game of Hundred and Ten"""

    players: list[Player] = field(default_factory=list)
    seed: str = field(default_factory=lambda: str(uuid4()))
    initial_moves: InitVar[Optional[list[Action]]] = field(default=None)

    _rounds: list[Round] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self, initial_moves: Optional[list[Action]]):
        if len(self.players) < 2:
            raise HundredAndTenError("Cannot have a game with less than 2 players")
        if len(self.players) > 4:
            raise HundredAndTenError("Cannot have a game with more than 4 players")

        # manually create the first round
        self.__new_round(self.players[0].identifier)

        for move in initial_moves or []:
            self.__act(move)  # don't trigger automation for already made moves

        self.__automated_act()

    @property
    def status(self) -> AnyStatus:
        """The status property."""
        if self.winner:
            return GameStatus.WON
        return self.active_round.status

    @property
    def rounds(self) -> Sequence[Round]:
        """All the rounds in the game, ordered"""
        return tuple(self._rounds)

    @property
    def active_round(self) -> Round:
        """The active round"""
        assert self._rounds
        return self._rounds[-1]

    @property
    def active_player(self) -> Player:
        """The active player"""
        return next(
            p
            for p in self.players
            if p.identifier == self.active_round.active_player.identifier
        )

    @property
    def winner(self) -> Optional[Player]:
        """
        The winner of the game
        """
        # if a round is in progress, don't attempt the computation
        if not self._rounds or self.active_round.status != RoundStatus.COMPLETED:
            return None

        winning_scores = [
            score for score in self.score_history if score.value >= WINNING_SCORE
        ]
        ordered_winning_players = list(
            map(
                lambda score: player_by_identifier(
                    self.active_round.players, score.identifier
                ),
                winning_scores,
            )
        )

        winner = (
            self.active_round.active_bidder
            if (self.active_round.active_bidder in ordered_winning_players)
            else next(iter(ordered_winning_players), None)
        )

        return next(
            (p for p in self.players if winner and p.identifier == winner.identifier),
            None,
        )

    @property
    def moves(self) -> list[Action]:
        """All moves that have been played in the game."""
        return [move for move in self.events if isinstance(move, Action)]

    @property
    def events(self) -> list[Event]:
        """The events that occurred in the game."""

        return [
            GameStart(),
            *chain.from_iterable(r.events for r in self._rounds),
            *([] if not self.winner else [GameEnd(self.winner.identifier)]),
        ]

    @property
    def score_history(self) -> list[Score]:
        """A list of all players' scores over time"""

        return self.__score_history(len(self._rounds))

    @property
    def scores_by_round(self) -> list[dict[str, int]]:
        """
        The scores each player earned for this game
        A dictionary in the form
        key: player identifier
        value: the player's score
        """
        return [
            self.__scores(round_num)
            for round_num in range(
                len(self._rounds)
                # get the score "after" the round if it is completed
                + (self.active_round.status == RoundStatus.COMPLETED)
            )
        ]

    @property
    def scores(self) -> dict[str, int]:
        """
        The scores each player earned for this game
        A dictionary in the form
        key: player identifier
        value: the player's score
        """
        return self.__scores(len(self._rounds))

    def act(self, action: Action) -> None:
        """Perform an action as a player of the game"""
        self.__act(action)
        self.__automated_act()

    def game_state_for(self, identifier: str) -> GameState:
        """Build a GameState observation for the identified player.

        All seats are rotated so that the requesting player is seat 0.
        Cards the player cannot see are marked Unknown.
        """
        game_round = self.active_round
        players = game_round.players
        num_players = len(players)
        non_relative_seat_by_identifier = {
            round_player.identifier: index for index, round_player in enumerate(players)
        }
        player = player_by_identifier(players, identifier)
        player_index = non_relative_seat_by_identifier[identifier]

        current_scores = self.scores
        table = TableInfo(
            num_players=num_players,
            dealer_seat=self.__relative_seat(
                non_relative_seat_by_identifier,
                player.identifier,
                game_round.dealer.identifier,
                num_players,
            ),
            bidder_seat=(
                self.__relative_seat(
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
                    seat=self.__relative_seat(
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

        return GameState(
            status=game_round.status,
            table=table,
            hand=tuple(player.hand),
            bidding=bidding,
            tricks=self.__build_trick_state(
                game_round, player, non_relative_seat_by_identifier
            ),
            cards=self.__build_card_knowledge(
                game_round, player, non_relative_seat_by_identifier
            ),
            available_actions=self.__build_available_actions(game_round, player),
        )

    def __build_card_knowledge(
        self,
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
                    seat=self.__relative_seat(
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

    def __build_trick_state(
        self,
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
                    seat=self.__relative_seat(
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
                        winner_seat=self.__relative_seat(
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

    def __build_available_actions(
        self,
        game_round: Round,
        player: RoundPlayer,
    ) -> tuple[Action, ...]:
        if (
            self.status == GameStatus.WON
            or game_round.active_player.identifier != player.identifier
        ):
            return ()

        if game_round.status == RoundStatus.BIDDING:
            return tuple(
                Bid(player.identifier, amount)
                for amount in game_round.available_bids(player.identifier)
            )

        if game_round.status == RoundStatus.TRUMP_SELECTION:
            return tuple(
                SelectTrump(player.identifier, suit) for suit in SelectableSuit
            )

        if game_round.status == RoundStatus.DISCARD:
            hand_list = list(player.hand)
            return tuple(
                Discard(player.identifier, list(subset))
                for r in range(len(hand_list) + 1)
                for subset in combinations(hand_list, r)
            )

        active_player_trumps = trumps(player.hand, game_round.trump)
        playable = (
            active_player_trumps
            if game_round.active_trick.bleeding and active_player_trumps
            else list(player.hand)
        )
        return tuple(Play(player.identifier, card) for card in playable)

    def __automated_act(self):
        while (
            isinstance(self.status, RoundStatus)
            and isinstance(self.active_player, AutomatedPlayer)
            and (
                action := self.active_player.act(
                    self.game_state_for(self.active_player.identifier)
                )
            )
            is not None
        ):
            self.__act(action)

    def __act(self, action: Action) -> None:
        """Perform an action as a player of the game"""
        self.active_round.act(action)
        # handle creation of new round if appropriate
        if isinstance(action, Bid):
            self.__end_bid()
        if isinstance(action, Play):
            self.__end_play()

    def __end_bid(self):
        if self.status == RoundStatus.COMPLETED_NO_BIDDERS:
            current_dealer = self.active_round.dealer.identifier
            # dealer doesn't rotate on a round with no bidders
            # unless the current dealer has been dealer 3x in a row
            keep_same_dealer = len(self._rounds) < 3 or any(
                r.dealer.identifier != current_dealer for r in self._rounds[-3:]
            )
            next_dealer = (
                current_dealer
                if keep_same_dealer
                else player_after(self.active_round.players, current_dealer).identifier
            )
            self.__new_round(next_dealer)

    def __end_play(self):
        if self.status == RoundStatus.COMPLETED:
            self.__new_round(
                player_after(
                    self.active_round.players, self.active_round.dealer.identifier
                ).identifier
            )

    def __new_round(self, dealer: str) -> None:
        r_deck_seed = hashlib.sha256(
            f"deck-seed|{self.seed}|round:{len(self._rounds)}".encode()
        ).hexdigest()

        deck_seed = str(UUID(int=Random(r_deck_seed).getrandbits(128), version=4))

        self._rounds.append(
            Round(
                game_players=self.players,
                dealer_identifier=dealer,
                seed=deck_seed,
            )
        )

    def __score_history(self, to_round: int) -> list[Score]:
        """A list of all players' scores up to the provided round"""

        scores = {}
        score_history = []

        all_final_scores = [
            score
            for game_round in self._rounds[:to_round]
            for score in game_round.scores
            if game_round.status == RoundStatus.COMPLETED
        ]

        for score in all_final_scores:
            new_score = scores.get(score.identifier, 0) + score.value
            scores[score.identifier] = new_score
            score_history.append(Score(score.identifier, new_score))

        return score_history

    def __scores(self, to_round) -> dict[str, int]:
        """
        The scores each player earned for this game up to the provided round
        A dictionary in the form
        key: player identifier
        value: the player's score
        """

        scores = {player.identifier: 0 for player in self.players}

        for game_round in self._rounds[:to_round]:
            if game_round.status != RoundStatus.COMPLETED:
                continue

            for score in game_round.scores:
                scores[score.identifier] = scores.get(score.identifier, 0) + score.value

        return scores

    def __relative_seat(
        self,
        non_relative_seat_by_identifier: dict[str, int],
        player_identifier: str,
        other_identifier: str,
        num_players: int,
    ) -> int:
        return (
            non_relative_seat_by_identifier[other_identifier]
            - non_relative_seat_by_identifier[player_identifier]
        ) % num_players
