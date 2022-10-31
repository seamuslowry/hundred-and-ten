'''Test behavior of the Game when bidding ends'''
from unittest import TestCase

from hundredandten.constants import BidAmount, GameRole, RoundRole, RoundStatus
from hundredandten.game import Game
from hundredandten.group import Group, Person
from hundredandten.hundred_and_ten_error import HundredAndTenError


class TestEndBidding(TestCase):
    '''Unit tests for ending the bidding stage'''

    def test_end_bidding_with_bids(self):
        '''Bidding ends when there is only one bidder with an active bid'''

        game = Game(
            persons=Group(
                [Person('1', roles={GameRole.PLAYER}),
                 Person('2', roles={GameRole.PLAYER})]))

        game.start_game()
        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertEqual(game.status, RoundStatus.TRUMP_SELECTION)
        self.assertEqual(game.active_player, game.active_round.active_bidder)

    def test_cannot_bid_after_bidding_stage(self):
        '''Bidding can only occur in the bidding stage'''

        game = Game(
            persons=Group(
                [Person('1', roles={GameRole.PLAYER}),
                 Person('2', roles={GameRole.PLAYER})]))

        game.start_game()
        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.FIFTEEN)

        self.assertNotEqual(game.status, RoundStatus.BIDDING)
        self.assertRaises(HundredAndTenError, game.bid,
                          game.players[0].identifier, BidAmount.FIFTEEN)

    def test_end_bidding_with_pass(self):
        '''Bidding ends when everyone has passed'''

        game = Game(
            persons=Group(
                [Person('1', roles={GameRole.PLAYER}),
                 Person('2', roles={GameRole.PLAYER})]))

        game.start_game()
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
        game = Game(
            persons=Group([
                Person('1', roles={GameRole.PLAYER}),
                Person('2', roles={GameRole.PLAYER}),
                Person('3', roles={GameRole.PLAYER}),
                Person('4', roles={GameRole.PLAYER})
            ]))
        game.start_game()

        self.assertEqual(0, len(game.active_round.bids))

        for player in list(filter(lambda p: p != game.active_player, game.players)):
            game.bid(player.identifier, BidAmount.PASS)

        self.assertEqual(0, len(game.active_round.bids))

        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(4, len(game.rounds[-2].bids))
        self.assertEqual(0, len(game.rounds[-2].players.by_role(RoundRole.PRE_PASSED)))
        self.assertEqual(0, len(game.rounds[-2].bidders))
        self.assertEqual(RoundStatus.COMPLETED_NO_BIDDERS, game.rounds[-2].status)
        self.assertRaises(HundredAndTenError, lambda: game.rounds[-2].active_player)

    def test_end_bidding_with_same_dealer(self):
        '''
        The same player is dealer after a round with no bidders
        if they've been dealer less than 3x in a row
        otherwise, it passes to the next player
        '''

        game = Game(
            persons=Group(
                [Person('1', roles={GameRole.PLAYER}),
                 Person('2', roles={GameRole.PLAYER})]))

        game.start_game()

        # first round as dealer
        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(game.rounds[-2].dealer, game.active_round.dealer)

        # second round as dealer
        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(game.rounds[-2].dealer, game.active_round.dealer)

        # third round as dealer
        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertNotEqual(game.rounds[-2].dealer, game.active_round.dealer)

        # first round with new dealer won't swap
        game.bid(game.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_player.identifier, BidAmount.PASS)

        self.assertEqual(game.rounds[-2].dealer, game.active_round.dealer)
