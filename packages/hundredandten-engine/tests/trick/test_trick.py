"""Test behavior of a trick"""

from unittest import TestCase

from hundredandten.deck import Card, CardNumber, CardSuit, SelectableSuit
from hundredandten.engine.actions import Play
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.trick import Trick


class TestTrick(TestCase):
    """Unit tests for a trick"""

    def test_no_winning_play(self):
        """With no plays, there is no winning play"""

        trick = Trick(SelectableSuit.HEARTS)

        self.assertRaises(HundredAndTenError, lambda: trick.winning_play)

    def test_no_weak_trump(self):
        """With no plays, there is no weak trump"""

        trick = Trick(SelectableSuit.CLUBS)

        self.assertIsNone(trick.weak_trump)

    def test_winning_play_with_one_play(self):
        """With only one play, that is always the winning play"""

        play = Play("", Card(CardNumber.TWO, CardSuit.HEARTS))

        for suit in SelectableSuit:
            self.assertEqual(play, Trick(suit, plays=[play]).winning_play)

    def test_winning_play_with_strong_trump(self):
        """When a strong trump is played, it will beat non-trumps"""

        plays = [
            Play("", Card(CardNumber.TWO, CardSuit.HEARTS)),
            Play("", Card(CardNumber.TWO, CardSuit.DIAMONDS)),
            Play("", Card(CardNumber.TWO, CardSuit.CLUBS)),
            Play("", Card(CardNumber.TWO, CardSuit.SPADES)),
        ]

        for play in plays:
            self.assertEqual(
                play, Trick(SelectableSuit[play.card.suit.value], plays).winning_play
            )

    def test_winning_play_with_weak_trump(self):
        """When no strong trump is played, the weak trump will win"""

        trick = Trick(
            SelectableSuit.CLUBS,
            plays=[
                Play("", Card(CardNumber.TWO, CardSuit.HEARTS)),
                Play("", Card(CardNumber.TWO, CardSuit.DIAMONDS)),
                Play("", Card(CardNumber.THREE, CardSuit.DIAMONDS)),
                Play("", Card(CardNumber.FOUR, CardSuit.DIAMONDS)),
            ],
        )

        self.assertEqual(trick.plays[0], trick.winning_play)

    def test_winning_play_with_all_trump(self):
        """When all strong trumps are played, the highest trump value wins"""

        winning_play = Play("", Card(CardNumber.FIVE, CardSuit.DIAMONDS))
        trick = Trick(
            SelectableSuit.DIAMONDS,
            plays=[
                Play("", Card(CardNumber.TWO, CardSuit.DIAMONDS)),
                Play("", Card(CardNumber.TWO, CardSuit.DIAMONDS)),
                winning_play,
                Play("", Card(CardNumber.FOUR, CardSuit.DIAMONDS)),
            ],
        )

        self.assertEqual(winning_play, trick.winning_play)
