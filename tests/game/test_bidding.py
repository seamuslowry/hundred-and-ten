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
            persons=people,
            rounds=[Round(Group[Player]([]), bids=[Bid('1', BidAmount.FIFTEEN)])])

        self.assertRaises(HundredAndTenError, lambda: game.active_player)

    def test_error_when_no_dealer(self):
        '''Round must always have a dealer'''

        players = Group([Player('1'),
                         Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        self.assertRaises(HundredAndTenError, lambda: game.active_round.dealer)

    def test_bid_from_active_player(self):
        '''Active player can place a bid'''

        players = Group[Player]([Player('1', roles={RoundRole.DEALER}),
                                 Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(Group[Player](players))])

        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(1, len(game.active_round.bids))
        self.assertEqual(BidAmount.FIFTEEN, game.active_round.bids[0].amount)

    def test_low_bid_from_active_player(self):
        '''Active player cannot place a bid below the current bid'''

        players = Group[Player]([Player('1', roles={RoundRole.DEALER}),
                                 Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.TWENTY)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_player.identifier, BidAmount.FIFTEEN)

    def test_equal_bid_from_active_player(self):
        '''Active player cannot place a bid equal to the current bid'''

        players = Group[Player]([Player('1', roles={RoundRole.DEALER}),
                                 Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.FIFTEEN)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_player.identifier, BidAmount.FIFTEEN)

    def test_low_bid_from_dealer(self):
        '''Dealer cannot place a bid below to the current bid'''

        players = Group[Player]([Player('1'),
                                 Player('2', roles={RoundRole.DEALER})])

        game = Game(
            persons=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.TWENTY)])])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_player.identifier, BidAmount.FIFTEEN)

    def test_equal_bid_from_dealer(self):
        '''Dealer can place a bid equal to the current bid'''

        players = Group[Player]([Player('1'),
                                 Player('2', roles={RoundRole.DEALER})])

        game = Game(
            persons=Group(),
            rounds=[Round(players, bids=[Bid(players[0].identifier, BidAmount.FIFTEEN)])])

        pre_len = len(game.active_round.bids)

        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(pre_len+1, len(game.active_round.bids))

    def test_bid_from_passed_player(self):
        '''Inactive player cannot place a bid'''

        players = Group[Player]([Player('1', roles={RoundRole.DEALER}),
                                 Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        once_active_player = game.active_player.identifier
        game.bid(once_active_player, BidAmount.PASS)

        self.assertRaises(HundredAndTenError, game.bid, once_active_player, BidAmount.FIFTEEN)

    def test_bid_from_inactive_player(self):
        '''Inactive player cannot place a bid'''

        players = Group[Player]([Player('1', roles={RoundRole.DEALER}),
                                 Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        self.assertRaises(HundredAndTenError, game.bid,
                          game.active_round.inactive_players[0].identifier, BidAmount.FIFTEEN)

    def test_pass_from_inactive_player(self):
        '''Inactive player can prepass'''

        players = Group[Player]([Player('1', roles={RoundRole.DEALER}),
                                 Player('2')])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        game.bid(game.active_round.inactive_players[0].identifier, BidAmount.PASS)

        self.assertEqual(0, len(game.active_round.bids))
        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_unpass_from_prepassed_player(self):
        '''Prepassed player can unpass'''

        players = Group[Player]([Player('1'),
                                 Player('2', roles={RoundRole.DEALER, RoundRole.PRE_PASSED})])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

        game.unpass(game.active_round.inactive_players[0].identifier)

        self.assertEqual(0, len(game.active_round.bids))
        self.assertNotIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_prepass(self):
        '''When the next player has prepassed, auto pass for them'''
        players = Group[Player]([
            Player('1', roles={RoundRole.DEALER}),
            Player('2'),
            Player('3', roles={RoundRole.PRE_PASSED})
        ])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        self.assertEqual(0, len(game.active_round.bids))

        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(2, len(game.active_round.bids))
        self.assertEqual(RoundStatus.BIDDING, game.status)
        self.assertEqual(0, len(game.active_round.players.by_role(RoundRole.PRE_PASSED)))
        # with 3 players set up as above, play will have cicled back around to the dealer
        self.assertEqual(game.active_player, game.active_round.dealer)
        self.assertEqual(1, len(game.active_round.bidders))
        self.assertIn(game.active_player, game.active_round.bidders)

    def test_end_bidding_with_bids(self):
        '''Bidding ends when there is only one bidder with an active bid'''

        players = Group[Player]([Player('1'),
                                 Player('2', roles={RoundRole.DEALER})])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(game.status, RoundStatus.TRUMP_SELECTION)
        self.assertEqual(game.active_player, game.active_round.active_bidder)

    def test_cannot_bid_after_bidding_stage(self):
        '''Bidding can only occur in the bidding stage'''

        players = Group[Player]([Player('1'),
                                 Player('2', roles={RoundRole.DEALER})])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertNotEqual(game.status, RoundStatus.BIDDING)
        self.assertRaises(HundredAndTenError, game.bid, players[0].identifier, BidAmount.FIFTEEN)

    def test_end_bidding_with_pass(self):
        '''Bidding ends when everyone has passed'''

        players = Group[Player]([Player('1'),
                                 Player('2', roles={RoundRole.DEALER})])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        # new round created because of passing
        self.assertEqual(2, len(game.rounds))
        # old round ended as completed no bidders
        self.assertEqual(game.rounds[-2].status, RoundStatus.COMPLETED_NO_BIDDERS)
        # new round in bidding
        self.assertEqual(game.status, RoundStatus.BIDDING)

    def test_end_bidding_with_prepass(self):
        '''When all players have prepassed, the round can end'''
        players = Group[Player]([
            Player('1', roles={RoundRole.DEALER, RoundRole.PRE_PASSED}),
            Player('2'),
            Player('3', roles={RoundRole.PRE_PASSED}),
            Player('4', roles={RoundRole.PRE_PASSED})
        ])

        game = Game(
            persons=Group(),
            rounds=[Round(players)])

        self.assertEqual(0, len(game.active_round.bids))

        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(4, len(game.rounds[-2].bids))
        self.assertEqual(0, len(game.rounds[-2].players.by_role(RoundRole.PRE_PASSED)))
        self.assertEqual(0, len(game.rounds[-2].bidders))
        self.assertEqual(RoundStatus.COMPLETED_NO_BIDDERS, game.rounds[-2].status)
        self.assertRaises(HundredAndTenError, lambda: game.rounds[-2].active_player)
