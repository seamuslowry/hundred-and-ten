'''Test to ensure bidding decisions are made consistently'''
from unittest import TestCase

from hundredandten.constants import BidAmount, CardNumber, SelectableSuit
from hundredandten.decisions import max_bid
from hundredandten.deck import Card


class TestBidDecision(TestCase):
    '''Unit tests for deciding on bids'''

    def test_passes_with_nothing(self):
        '''Decide to pass'''
        self.assertEqual(BidAmount.PASS, max_bid([]))

    def test_goes_fifteen(self):
        '''Decide to go up to fifteen'''
        self.assertEqual(BidAmount.FIFTEEN, max_bid(
            [
                Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 0),
                Card(CardNumber.QUEEN, SelectableSuit.CLUBS, 8, 0)
            ]))

    def test_wont_go_fifteen_without_five(self):
        '''Decide not to go to fifteen without the five'''
        self.assertEqual(BidAmount.PASS, max_bid(
            [
                Card(CardNumber.JACK, SelectableSuit.CLUBS, 13, 0),
                Card(CardNumber.QUEEN, SelectableSuit.CLUBS, 8, 0)
            ]))

    def test_goes_twenty(self):
        '''Decide to go up to twenty'''
        self.assertEqual(BidAmount.TWENTY, max_bid(
            [
                Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 0),
                Card(CardNumber.JACK, SelectableSuit.CLUBS, 13, 0)
            ]))

    def test_goes_twenty_five(self):
        '''Decide to go up to twenty five'''
        self.assertEqual(BidAmount.TWENTY_FIVE, max_bid(
            [
                Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 0),
                Card(CardNumber.JACK, SelectableSuit.CLUBS, 13, 0),
                Card(CardNumber.JOKER, SelectableSuit.CLUBS, 12, 0)
            ]))

    def test_goes_thirty(self):
        '''Decide to go up to thirty'''
        self.assertEqual(BidAmount.THIRTY, max_bid(
            [
                Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 0),
                Card(CardNumber.JACK, SelectableSuit.CLUBS, 13, 0),
                Card(CardNumber.JOKER, SelectableSuit.CLUBS, 12, 0),
                Card(CardNumber.ACE, SelectableSuit.HEARTS, 11, 0, True)
            ]))

    def test_shoots_the_moon(self):
        '''Decide to go up to shooting the moon'''
        self.assertEqual(BidAmount.SHOOT_THE_MOON, max_bid(
            [
                Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 0),
                Card(CardNumber.JACK, SelectableSuit.CLUBS, 13, 0),
                Card(CardNumber.JOKER, SelectableSuit.CLUBS, 12, 0),
                Card(CardNumber.ACE, SelectableSuit.HEARTS, 11, 0, True),
                Card(CardNumber.ACE, SelectableSuit.CLUBS, 10, 0)
            ]))
