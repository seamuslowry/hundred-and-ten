'''Test behavior of a trick'''
from unittest import TestCase

from hundredandten.constants import CardNumber, SelectableSuit
from hundredandten.deck import Card
from hundredandten.trick import Play, Trick


class TestTrick(TestCase):
    '''Unit tests for a trick'''

    def test_no_winning_play(self):
        '''With no plays, there is no winning play'''

        trick = Trick()

        self.assertIsNone(trick.winning_play(SelectableSuit.HEARTS))

    def test_no_weak_trump(self):
        '''With no plays, there is no weak trump'''

        trick = Trick()

        self.assertIsNone(trick.weak_trump)

    def test_winning_play_with_one_play(self):
        '''With only one play, that is always the winning play'''

        play = Play('', Card(CardNumber.TWO, SelectableSuit.HEARTS, 0, 0))
        trick = Trick(plays=[play])

        for suit in SelectableSuit:
            self.assertEqual(play, trick.winning_play(suit))

    def test_winning_play_with_strong_trump(self):
        '''When a strong trump is played, it will beat non-trumps'''

        trick = Trick(
            plays=[Play('', Card(CardNumber.TWO, SelectableSuit.HEARTS, 0, 0)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS, 0, 0)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.CLUBS, 0, 0)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.SPADES, 0, 0))])

        for play in trick.plays:
            assert isinstance(play.card.suit, SelectableSuit)
            self.assertEqual(play, trick.winning_play(play.card.suit))

    def test_winning_play_with_weak_trump(self):
        '''When a strong trump is played, it will beat non-trumps'''

        trick = Trick(
            plays=[Play('', Card(CardNumber.TWO, SelectableSuit.HEARTS, 0, 0)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS, 0, 0)),
                   Play('', Card(CardNumber.THREE, SelectableSuit.DIAMONDS, 0, 0)),
                   Play('', Card(CardNumber.FOUR, SelectableSuit.DIAMONDS, 0, 0))])

        self.assertEqual(trick.plays[0], trick.winning_play(SelectableSuit.CLUBS))

    def test_winning_play_with_all_trump(self):
        '''When a strong trump is played, it will beat non-trumps'''

        winning_play = Play('', Card(CardNumber.FIVE, SelectableSuit.DIAMONDS, 3, 0))
        trick = Trick(
            plays=[Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS, 0, 3)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS, 1, 2)),
                   winning_play,
                   Play('', Card(CardNumber.FOUR, SelectableSuit.DIAMONDS, 2, 1))])

        self.assertEqual(winning_play, trick.winning_play(SelectableSuit.DIAMONDS))
