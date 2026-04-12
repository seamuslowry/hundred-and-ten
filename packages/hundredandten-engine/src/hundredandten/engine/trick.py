"""Track a trick"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from hundredandten.deck import Card, CardSuit, SelectableSuit
from hundredandten.engine.errors import HundredAndTenError

from .actions import Play


@dataclass
class Score:
    """Keep track of the score of a single trick"""

    identifier: str
    value: int


@dataclass
class Trick:
    """A class to keep track of one trick"""

    round_trump: SelectableSuit
    plays: list[Play] = field(default_factory=list)

    @property
    def winning_play(self) -> Play:
        """Determine the winner of the trick considering the passed suit as trump"""

        strong_trump_winner = self.__winning_play(
            lambda play: play.card.suit == self.round_trump or play.card.always_trump,
            lambda play: play.card.trump_value,
        )

        weak_trump_winner = self.__winning_play(
            lambda play: play.card.suit == self.weak_trump,
            lambda play: play.card.weak_trump_value,
        )

        play = strong_trump_winner or weak_trump_winner

        if not play:
            raise HundredAndTenError(
                f"Unable to determine winning play in {self.plays}"
            )

        return play

    @property
    def bleeding(self) -> bool:
        """True if the trick should force players to play a trump card (if they have one)"""
        return bool(self.leading_card) and self.leading_card.trump_for_selection(
            self.round_trump
        )

    @property
    def leading_card(self) -> Optional[Card]:
        """The leading card of this trick"""
        if not self.plays:
            return None
        return self.plays[0].card

    @property
    def weak_trump(self) -> Optional[CardSuit]:
        """The leading card of this trick"""
        if self.leading_card and self.leading_card.suit != self.round_trump:
            return self.leading_card.suit
        return None

    def __winning_play(
        self, filter_fn: Callable[[Play], bool], key_fn: Callable[[Play], int]
    ) -> Optional[Play]:
        return max(list(filter(filter_fn, self.plays)), key=key_fn, default=None)
