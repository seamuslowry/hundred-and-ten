"""Represent a game of Hundred and Ten"""

import hashlib
from dataclasses import dataclass, field
from itertools import combinations
from random import Random
from typing import Optional, Sequence
from uuid import UUID, uuid4

from .actions import Action, Bid, Discard, Play, SelectTrump
from .constants import (
    WINNING_SCORE,
    AnyStatus,
    GameStatus,
    RoundStatus,
    SelectableSuit,
)
from .errors import HundredAndTenError
from .player import (
    Player,
    player_after,
    player_by_identifier,
)
from .round import Round
from .trick import Score
from .trumps import trumps


@dataclass
class Game:
    """A game of Hundred and Ten"""

    players: list[Player] = field(default_factory=list)
    seed: str = field(default_factory=lambda: str(uuid4()))
    _rounds: list[Round] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        if len(self.players) < 2:
            raise HundredAndTenError("Cannot have a game with less than 2 players")
        if len(self.players) > 4:
            raise HundredAndTenError("Cannot have a game with more than 4 players")

        # manually create the first round
        self.__new_round(self.players[0].identifier)

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
    def actions(self) -> list[Action]:
        """All actions that have been taken in the game."""
        return [action for r in self.rounds for action in r.actions]

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

    def available_actions(
        self,
        identifier: str,
    ) -> tuple[Action, ...]:
        """Return all actions available to the player currently"""
        game_round = self.active_round
        player = player_by_identifier(game_round.players, identifier)
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
