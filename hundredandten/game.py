"""Represent a game of Hundred and Ten"""

import hashlib
from dataclasses import InitVar, dataclass, field
from functools import reduce
from itertools import chain
from random import Random
from typing import Optional, Sequence
from uuid import UUID, uuid4

from hundredandten.actions import Action, Bid, Play
from hundredandten.constants import (
    WINNING_SCORE,
    AnyStatus,
    GameStatus,
    RoundStatus,
)
from hundredandten.events import Event, GameEnd, GameStart, Score
from hundredandten.group import Group, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.round import Round


@dataclass
class Game:
    """A game of Hundred and Ten"""

    players: Group = field(default_factory=Group)
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
                lambda score: self.active_round.players.by_identifier(score.identifier),
                winning_scores,
            )
        )

        winner = (
            self.active_round.active_bidder
            if (self.active_round.active_bidder in ordered_winning_players)
            else next(iter(ordered_winning_players), None)
        )

        return winner

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

    def suggestion(self) -> Action:
        """Return the suggested action given the state of the game"""
        return self.active_round.suggestion()

    def __automated_act(self):
        while (
            isinstance(self.status, RoundStatus)
            and self.active_round.active_player.automate
        ):
            self.__act(self.__automated_action())

    def __automated_action(self) -> Action:
        return self.suggestion()

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
                else self.players.after(current_dealer).identifier
            )
            self.__new_round(next_dealer)

    def __end_play(self):
        if self.status == RoundStatus.COMPLETED:
            self.__new_round(
                self.players.after(self.active_round.dealer.identifier).identifier
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

        return reduce(
            lambda acc, player: {
                **acc,
                player.identifier: self.__score_at_round(player.identifier, to_round),
            },
            self.players,
            {player.identifier: 0 for player in self.players},
        )

    def __score_at_round(self, identifier: str, to_round: int) -> int:
        """Return the most recent score for the provided player at the provided round"""

        most_recent_score = next(
            (
                score
                for score in reversed(self.__score_history(to_round))
                if score.identifier == identifier
            ),
            None,
        )

        return most_recent_score.value if most_recent_score else 0
