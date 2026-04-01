"""Test behavior of the Game while in a round of bidding"""

from unittest import TestCase

from hundredandten.actions import Bid
from hundredandten.constants import BidAmount, RoundRole, RoundStatus
from hundredandten.errors import HundredAndTenError
from hundredandten.player import remove_player_role
from tests import arrange


class TestBidding(TestCase):
    """Unit tests for bidding within a round of Game"""

    def test_error_when_no_dealer(self):
        """Round must always have a dealer"""

        game = arrange.game(RoundStatus.BIDDING)

        # remove dealer role to put game in invalid state to verify error
        remove_player_role(
            game.active_round.players,
            game.active_round.dealer.identifier,
            RoundRole.DEALER,
        )

        self.assertRaises(HundredAndTenError, lambda: game.active_round.dealer)

    def test_bid_from_active_player(self):
        """Active player can place a bid"""

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertEqual(1, len(game.active_round.bids))
        self.assertEqual(BidAmount.FIFTEEN, game.active_round.bids[0].amount)

    def test_low_bid_from_active_player(self):
        """Active player cannot place a bid below the current bid"""

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.TWENTY))

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN),
        )

    def test_equal_bid_from_active_player(self):
        """Active player cannot place a bid equal to the current bid"""

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN),
        )

    def test_low_bid_from_dealer(self):
        """Dealer cannot place a bid below to the current bid"""

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.TWENTY))
        arrange.pass_to_dealer(game)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN),
        )

    def test_equal_bid_from_dealer(self):
        """Dealer can place a bid equal to the current bid"""

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertNotEqual(game.active_round.active_bidder, game.active_round.dealer)

        arrange.pass_to_dealer(game)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertIsNone(game.active_round.active_bidder)  # competing bids

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.PASS))

        self.assertEqual(game.active_round.active_bidder, game.active_round.dealer)

    def test_bid_from_passed_player(self):
        """Inactive player cannot place a bid"""

        game = arrange.game(RoundStatus.BIDDING)

        once_active_player = game.active_round.active_player.identifier
        game.act(Bid(once_active_player, BidAmount.PASS))

        self.assertRaises(
            HundredAndTenError, game.act, Bid(once_active_player, BidAmount.FIFTEEN)
        )

    def test_bid_from_inactive_player(self):
        """Inactive player cannot place a bid"""

        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Bid(game.active_round.inactive_players[0].identifier, BidAmount.FIFTEEN),
        )
