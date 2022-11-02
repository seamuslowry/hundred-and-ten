'''Track a trick'''
from dataclasses import dataclass, field
from typing import Callable, Optional

from hundredandten.constants import CardSuit, SelectableSuit
from hundredandten.deck import Card


@dataclass
class Play:
    '''A class to keep track of one play in a trick'''
    identifier: str
    card: Card


@dataclass
class Trick:
    '''A class to keep track of one trick'''
    plays: list[Play] = field(default_factory=list)

    def winning_play(self, suit: SelectableSuit) -> Optional[Play]:
        '''Determine the winner of the trick considering the passed suit as trump'''

        strong_trump_winner = self.__winning_play(
            lambda play: play.card.suit == suit or play.card.always_trump,
            lambda play: play.card.trump_value
        )

        weak_trump_winner = self.__winning_play(
            lambda play: play.card.suit == self.weak_trump,
            lambda play: play.card.weak_trump_value
        )

        return strong_trump_winner or weak_trump_winner

    def __winning_play(
            self,
            filter_fn: Callable[[Play], bool],
            key_fn: Callable[[Play], int]) -> Optional[Play]:
        return max(list(filter(filter_fn, self.plays)), key=key_fn, default=None)

    @property
    def weak_trump(self) -> Optional[CardSuit]:
        '''The weak trump of this trick'''
        if not self.plays:
            return None
        return self.plays[0].card.suit
