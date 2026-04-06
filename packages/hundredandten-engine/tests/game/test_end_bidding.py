"""Test behavior of the Game when bidding ends"""

from unittest import TestCase

from hundredandten.engine.actions import Bid
from hundredandten.engine.constants import BidAmount, Status
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.testing import arrange


class TestEndBidding(TestCase):
    """Unit tests for ending the bidding stage"""

    def test_no_active_player_when_completed_no_bidders(self):
        """Round will have no active player when complete"""

        game = arrange.game(Status.COMPLETED_NO_BIDDERS)

        self.assertRaises(HundredAndTenError, lambda: game.rounds[-2].active_player)

    def test_end_bidding_with_bids(self):
        """Bidding ends when there is only one bidder with an active bid"""

        game = arrange.game(Status.TRUMP_SELECTION)

        self.assertEqual(game.status, Status.TRUMP_SELECTION)
        self.assertEqual(
            game.active_round.active_player, game.active_round.active_bidder
        )

    def test_cannot_bid_after_bidding_stage(self):
        """Bidding can only occur in the bidding stage"""

        game = arrange.game(Status.TRUMP_SELECTION)

        self.assertNotEqual(game.status, Status.BIDDING)
        self.assertRaises(
            HundredAndTenError,
            game.act,
            Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN),
        )

    def test_end_bidding_with_pass(self):
        """Bidding ends when everyone has passed"""

        game = arrange.game(Status.COMPLETED_NO_BIDDERS)

        # old round ended as completed no bidders
        self.assertEqual(game.rounds[-2].status, Status.COMPLETED_NO_BIDDERS)
        self.assertTrue(game.rounds[-2].completed)
        # new round in bidding
        self.assertEqual(game.status, Status.BIDDING)

    def test_end_bidding_with_same_dealer(self):
        """
        The same player is dealer after a round with no bidders
        if they've been dealer less than 3x in a row
        otherwise, it passes to the next player
        """

        game = arrange.game(Status.BIDDING)

        # first round as dealer
        arrange.pass_round(game)

        self.assertEqual(game.rounds[-2].dealer, game.active_round.dealer)

        # second round as dealer
        arrange.pass_round(game)

        self.assertEqual(game.rounds[-2].dealer, game.active_round.dealer)

        # third round as dealer
        arrange.pass_round(game)

        self.assertNotEqual(game.rounds[-2].dealer, game.active_round.dealer)

        # first round with new dealer won't swap
        arrange.pass_round(game)

        self.assertEqual(game.rounds[-2].dealer, game.active_round.dealer)
