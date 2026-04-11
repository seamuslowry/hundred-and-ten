"""Test to ensure bidding decisions are made consistently"""

from unittest import TestCase

from hundredandten.automation.naive import max_bid
from hundredandten.deck import Card, CardNumber, CardSuit


class TestBidDecision(TestCase):
    """Unit tests for deciding on bids"""

    def test_passes_with_nothing(self):
        """Decide to pass"""
        self.assertEqual(0, max_bid([]))

    def test_goes_fifteen(self):
        """Decide to go up to fifteen"""
        self.assertEqual(
            15,
            max_bid(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.QUEEN, CardSuit.CLUBS),
                ]
            ),
        )

    def test_wont_go_fifteen_without_five(self):
        """Decide not to go to fifteen without the five"""
        self.assertEqual(
            0,
            max_bid(
                [
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                    Card(CardNumber.QUEEN, CardSuit.CLUBS),
                ]
            ),
        )

    def test_will_go_fifteen_without_five(self):
        """Decide not to go to fifteen without the five"""
        self.assertEqual(
            15,
            max_bid(
                [
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                    Card(CardNumber.JOKER, CardSuit.JOKER),
                    Card(CardNumber.QUEEN, CardSuit.CLUBS),
                ]
            ),
        )

    def test_goes_twenty(self):
        """Decide to go up to twenty"""
        self.assertEqual(
            20,
            max_bid(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                ]
            ),
        )

    def test_goes_twenty_five(self):
        """Decide to go up to twenty five"""
        self.assertEqual(
            25,
            max_bid(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                    Card(CardNumber.JOKER, CardSuit.JOKER),
                ]
            ),
        )

    def test_goes_thirty(self):
        """Decide to go up to thirty"""
        self.assertEqual(
            30,
            max_bid(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                    Card(CardNumber.JOKER, CardSuit.JOKER),
                    Card(CardNumber.ACE, CardSuit.HEARTS),
                ]
            ),
        )

    def test_shoots_the_moon(self):
        """Decide to go up to shooting the moon"""
        self.assertEqual(
            60,
            max_bid(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                    Card(CardNumber.JOKER, CardSuit.JOKER),
                    Card(CardNumber.ACE, CardSuit.HEARTS),
                    Card(CardNumber.ACE, CardSuit.CLUBS),
                ]
            ),
        )
