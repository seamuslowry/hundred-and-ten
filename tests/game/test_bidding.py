'''Test behavior of the Game while in a round of bidding'''
from unittest import TestCase

from hundredandten.bid import Bid
from hundredandten.constants import (BidAmount, GameRole, RoundRole,
                                     RoundStatus)
from hundredandten.game import Game
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.people import People
from hundredandten.person import Person
from hundredandten.round import Round


class TestBidding(TestCase):
    '''Unit tests for bidding within a round of Game'''

    def test_error_when_no_active_player(self):
        '''Round must always have an active player'''

        people = People([Person('1', roles={GameRole.PLAYER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(People([]), bids=[Bid('1', BidAmount.FIFTEEN)])])

        self.assertRaises(HundredAndTenError, lambda: game.active_player)

    def test_error_when_no_dealer(self):
        '''Round must always have a dealer'''

        people = People([Person('1', roles={GameRole.PLAYER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(People(people))])

        self.assertRaises(HundredAndTenError, lambda: game.active_round.dealer)

    def test_bid_from_active_player(self):
        '''Active player can place a bid'''

        people = People([Person('1', roles={GameRole.PLAYER, RoundRole.DEALER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(1, len(game.active_round.bids))
        self.assertEqual(BidAmount.FIFTEEN, game.active_round.bids[0].amount)

    def test_low_bid_from_active_player(self):
        '''Active player cannot place a bid below the current bid'''

        people = People([Person('1', roles={GameRole.PLAYER, RoundRole.DEALER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(people, bids=[Bid(people[0].identifier, BidAmount.TWENTY)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_player.identifier, BidAmount.FIFTEEN)

    def test_equal_bid_from_active_player(self):
        '''Active player cannot place a bid equal to the current bid'''

        people = People([Person('1', roles={GameRole.PLAYER, RoundRole.DEALER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(people, bids=[Bid(people[0].identifier, BidAmount.FIFTEEN)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_player.identifier, BidAmount.FIFTEEN)

    def test_low_bid_from_dealer(self):
        '''Dealer cannot place a bid below to the current bid'''

        people = People([Person('1', roles={GameRole.PLAYER}), Person(
            '2', roles={GameRole.PLAYER, RoundRole.DEALER})])

        game = Game(
            persons=people,
            rounds=[Round(people, bids=[Bid(people[0].identifier, BidAmount.TWENTY)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_player.identifier, BidAmount.FIFTEEN)

    def test_equal_bid_from_dealer(self):
        '''Dealer can place a bid equal to the current bid'''

        people = People([Person('1', roles={GameRole.PLAYER}), Person(
            '2', roles={GameRole.PLAYER, RoundRole.DEALER})])

        game = Game(
            persons=people,
            rounds=[Round(people, bids=[Bid(people[0].identifier, BidAmount.FIFTEEN)])])

        pre_len = len(game.active_round.bids)

        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(pre_len+1, len(game.active_round.bids))

    def test_bid_from_passed_player(self):
        '''Inactive player cannot place a bid'''

        people = People([Person('1', roles={GameRole.PLAYER, RoundRole.DEALER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        once_active_player = game.active_player.identifier
        game.bid(once_active_player, BidAmount.PASS)

        self.assertRaises(HundredAndTenError, game.bid, once_active_player, BidAmount.FIFTEEN)

    def test_bid_from_inactive_player(self):
        '''Inactive player cannot place a bid'''

        people = People([Person('1', roles={GameRole.PLAYER, RoundRole.DEALER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_round.inactive_players[0].identifier, BidAmount.FIFTEEN)

    def test_pass_from_inactive_player(self):
        '''Inactive player can prepass'''

        people = People([Person('1', roles={GameRole.PLAYER, RoundRole.DEALER}),
                         Person('2', roles={GameRole.PLAYER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        game.bid(game.active_round.inactive_players[0].identifier, BidAmount.PASS)

        self.assertEqual(0, len(game.active_round.bids))
        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_unpass_from_prepassed_player(self):
        '''Prepassed player can unpass'''

        people = People([Person('1', roles={GameRole.PLAYER}), Person(
            '2', roles={GameRole.PLAYER, RoundRole.PRE_PASSED, RoundRole.DEALER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

        game.unpass(game.active_round.inactive_players[0].identifier)

        self.assertEqual(0, len(game.active_round.bids))
        self.assertNotIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_end_bidding_with_bids(self):
        '''Bidding ends when there is only one bidder with an active bid'''

        people = People([Person('1', roles={GameRole.PLAYER}), Person(
            '2', roles={GameRole.PLAYER, RoundRole.DEALER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(game.status, RoundStatus.TRUMP_SELECTION)
        self.assertEqual(game.active_player, game.active_round.active_bidder)

    def test_end_bidding_with_pass(self):
        '''Bidding ends when everyone has passed'''

        people = People([Person('1', roles={GameRole.PLAYER}), Person(
            '2', roles={GameRole.PLAYER, RoundRole.DEALER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(game.status, RoundStatus.COMPLETED_NO_BIDDERS)

    def test_cannot_bid_after_bidding_stage(self):
        '''Bidding ends when everyone has passed'''

        people = People([Person('1', roles={GameRole.PLAYER}), Person(
            '2', roles={GameRole.PLAYER, RoundRole.DEALER})])

        game = Game(
            persons=people,
            rounds=[Round(people)])

        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(game.status, RoundStatus.COMPLETED_NO_BIDDERS)
        self.assertRaises(HundredAndTenError, game.bid, people[0].identifier, BidAmount.FIFTEEN)
