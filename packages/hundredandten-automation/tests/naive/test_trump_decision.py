"""Test to ensure trump selection decisions are made consistently"""

from unittest import TestCase

from hundredandten.automation.naive import desired_trump
from hundredandten.deck import CardNumber, CardSuit, SelectableSuit
from hundredandten.engine.deck import Card


class TestTrumpDecision(TestCase):
    """Unit tests for deciding on trump"""

    def test_selects_highest_value(self):
        """Select trump with the highest value"""
        self.assertEqual(
            SelectableSuit.HEARTS,
            desired_trump(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.QUEEN, CardSuit.CLUBS),
                    Card(CardNumber.FIVE, CardSuit.HEARTS),
                    Card(CardNumber.KING, CardSuit.HEARTS),
                ]
            ),
        )
