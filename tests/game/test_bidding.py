'''Test behavior of the Game while in a round of bidding'''
from unittest import TestCase

from hundredandten.bid import Bid
from hundredandten.constants import BidAmount, GameRole, RoundRole, RoundStatus
from hundredandten.game import Game
from hundredandten.group import Group, Person, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.round import Round


class TestBidding(TestCase):
    '''Unit tests for bidding within a round of Game'''

    def test_error_when_no_active_player(self):
        '''Round must always have an active player'''

        people = Group([Person('1', roles={GameRole.PLAYER}),
                        Person('2', roles={GameRole.PLAYER})])

        game = Game(
            people=people,
            rounds=[Round(Group([]), bids=[Bid('1', BidAmount.FIFTEEN)])])

        self.assertRaises(HundredAndTenError, lambda: game.active_round.active_player)

    def test_error_when_no_dealer(self):
        '''Round must always have a dealer'''

        players = Group([Player('1'),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(players)])

        self.assertRaises(HundredAndTenError, lambda: game.active_round.dealer)

    def test_bid_from_active_player(self):
        '''Active player can place a bid'''

        players = Group([Player('1', roles={RoundRole.DEALER}),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(Group(players))])

        game.bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(1, len(game.active_round.bids))
        self.assertEqual(BidAmount.FIFTEEN, game.active_round.bids[0].amount)

    def test_low_bid_from_active_player(self):
        '''Active player cannot place a bid below the current bid'''

        players = Group([Player('1', roles={RoundRole.DEALER}),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.TWENTY)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_round.active_player.identifier, BidAmount.FIFTEEN)

    def test_equal_bid_from_active_player(self):
        '''Active player cannot place a bid equal to the current bid'''

        players = Group([Player('1', roles={RoundRole.DEALER}),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.FIFTEEN)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_round.active_player.identifier, BidAmount.FIFTEEN)

    def test_low_bid_from_dealer(self):
        '''Dealer cannot place a bid below to the current bid'''

        players = Group([Player('1'),
                         Player('2', roles={RoundRole.DEALER})])

        game = Game(
            people=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.TWENTY)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_round.active_player.identifier, BidAmount.FIFTEEN)

    def test_equal_bid_from_dealer(self):
        '''Dealer can place a bid equal to the current bid'''

        players = Group([Player('1'),
                         Player('2', roles={RoundRole.DEALER})])

        game = Game(
            people=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.FIFTEEN)])])

        pre_len = len(game.active_round.bids)

        game.bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(pre_len+1, len(game.active_round.bids))

    def test_bid_from_passed_player(self):
        '''Inactive player cannot place a bid'''

        players = Group([Player('1', roles={RoundRole.DEALER}),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(players)])

        once_active_player = game.active_round.active_player.identifier
        game.bid(once_active_player, BidAmount.PASS)

        self.assertRaises(HundredAndTenError, game.bid, once_active_player, BidAmount.FIFTEEN)

    def test_bid_from_inactive_player(self):
        '''Inactive player cannot place a bid'''

        players = Group([Player('1', roles={RoundRole.DEALER}),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(players)])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_round.inactive_players[0].identifier, BidAmount.FIFTEEN)

    def test_pass_from_inactive_player(self):
        '''Inactive player can prepass'''

        players = Group([Player('1', roles={RoundRole.DEALER}),
                         Player('2')])

        game = Game(
            people=Group(),
            rounds=[Round(players)])

        game.bid(game.active_round.inactive_players[0].identifier, BidAmount.PASS)

        self.assertEqual(0, len(game.active_round.bids))
        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_unpass_from_prepassed_player(self):
        '''Prepassed player can unpass'''

        players = Group([Player('1'),
                         Player('2', roles={RoundRole.DEALER, RoundRole.PRE_PASSED})])

        game = Game(
            people=Group(),
            rounds=[Round(players)])

        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

        game.unpass(game.active_round.inactive_players[0].identifier)

        self.assertEqual(0, len(game.active_round.bids))
        self.assertNotIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_prepass(self):
        '''When the next player has prepassed, auto pass for them'''
        players = Group([
            Player('1', roles={RoundRole.DEALER}),
            Player('2'),
            Player('3', roles={RoundRole.PRE_PASSED})
        ])

        game = Game(
            people=Group(),
            rounds=[Round(players)])

        self.assertEqual(0, len(game.active_round.bids))

        game.bid(game.active_round.active_player.identifier, BidAmount.PASS)

        self.assertEqual(2, len(game.active_round.bids))
        self.assertEqual(RoundStatus.BIDDING, game.status)
        self.assertEqual(0, len(game.active_round.players.by_role(RoundRole.PRE_PASSED)))
        # with 3 players set up as above, play will have cicled back around to the dealer
        self.assertEqual(game.active_round.active_player, game.active_round.dealer)
        self.assertEqual(1, len(game.active_round.bidders))
        self.assertIn(game.active_round.active_player, game.active_round.bidders)
