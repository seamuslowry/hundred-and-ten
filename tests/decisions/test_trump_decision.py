'''Test to ensure trump selection decisions are made consistently'''
from unittest import TestCase

from hundredandten.constants import CardNumber, SelectableSuit
from hundredandten.decisions import desired_trump
from hundredandten.deck import Card


class TestTrumpDecision(TestCase):
    '''Unit tests for deciding on bids'''

    def test_selects_highest_value(self):
        '''Select trump with the highest value'''
        self.assertEqual(SelectableSuit.HEARTS, desired_trump(
            [
                Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 0),
                Card(CardNumber.QUEEN, SelectableSuit.CLUBS, 8, 0),
                Card(CardNumber.FIVE, SelectableSuit.HEARTS, 14, 0),
                Card(CardNumber.KING, SelectableSuit.HEARTS, 9, 0)
            ]))
