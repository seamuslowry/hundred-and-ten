"""Test to ensure bidding decisions are made consistently"""

from unittest import TestCase

from hundredandten.automation.naive import _max_bid, action_for
from hundredandten.deck import Card, CardNumber, CardSuit
from hundredandten.state import AvailableBid, BidAmount
from hundredandten.testing import state as build


class TestBidDecision(TestCase):
    """Unit tests for deciding on bids"""

    def test_passes_with_nothing(self):
        """Decide to pass"""
        self.assertEqual(0, _max_bid([]))

    def test_goes_fifteen(self):
        """Decide to go up to fifteen"""
        self.assertEqual(
            15,
            _max_bid(
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
            _max_bid(
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
            _max_bid(
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
            _max_bid(
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
            _max_bid(
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
            _max_bid(
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
            _max_bid(
                [
                    Card(CardNumber.FIVE, CardSuit.CLUBS),
                    Card(CardNumber.JACK, CardSuit.CLUBS),
                    Card(CardNumber.JOKER, CardSuit.JOKER),
                    Card(CardNumber.ACE, CardSuit.HEARTS),
                    Card(CardNumber.ACE, CardSuit.CLUBS),
                ]
            ),
        )


FIVE_CLUBS = Card(CardNumber.FIVE, CardSuit.CLUBS)
JACK_CLUBS = Card(CardNumber.JACK, CardSuit.CLUBS)


class TestSuggestedBidSelection(TestCase):
    """Regression tests for action_for bid selection"""

    def test_bids_minimum_willing_amount(self):
        """When multiple bid amounts are within the willing range, pick the lowest

        Regression: previously used next(iter(...)) on an unsorted list, which
        could return a higher bid than intended when the hand warranted e.g. TWENTY
        but FIFTEEN was also available and preferable.
        """
        # Hand worth exactly TWENTY — both FIFTEEN and TWENTY are willing bids
        hand = (FIVE_CLUBS, JACK_CLUBS)
        state = build.game_state(hand=hand)

        self.assertEqual(_max_bid(state.hand), BidAmount.TWENTY)
        available_amounts = [b.amount for b in state.available_bids]
        self.assertIn(BidAmount.FIFTEEN, available_amounts)
        self.assertIn(BidAmount.TWENTY, available_amounts)

        result = action_for(state)

        # Must pick the minimum willing bid (FIFTEEN), not the higher one (TWENTY)
        assert isinstance(result, AvailableBid)
        self.assertEqual(result.amount, BidAmount.FIFTEEN)
