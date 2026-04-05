"""Test behavior of the Game while in a round of bidding"""

from unittest import TestCase

from hundredandten.engine.actions import Bid
from hundredandten.engine.constants import BidAmount, RoundRole, RoundStatus
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.player import remove_player_role
from hundredandten.testing import arrange


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

        bid = Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)

        game.act(bid)

        self.assertEqual(1, len(game.active_round.bids))
        self.assertEqual(BidAmount.FIFTEEN, game.active_round.bids[0].amount)
        self.assertEqual(bid, game.actions[-1])

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

        self.assertRaises(HundredAndTenError, game.act, Bid(once_active_player, BidAmount.FIFTEEN))

    def test_bid_from_inactive_player(self):
        """Inactive player cannot place a bid"""

        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Bid(game.active_round.inactive_players[0].identifier, BidAmount.FIFTEEN),
        )

    def test_all_bids_available_at_start(self):
        """All bids can be made before anyone bids"""

        game = arrange.game(RoundStatus.BIDDING)

        self.assertEqual(6, len(game.available_actions(game.active_player.identifier)))
        self.assertTrue(
            all(isinstance(a, Bid) for a in game.available_actions(game.active_player.identifier))
        )

    def test_no_bids_available_when_not_your_turn(self):
        """No bids available when not your turn"""

        game = arrange.game(RoundStatus.BIDDING)

        self.assertEqual(
            0, len(game.available_actions(game.active_round.inactive_players[0].identifier))
        )

    def test_only_pass_available_when_cant_take(self):
        """Only pass is available when you cant take the bid"""

        game = arrange.game(RoundStatus.BIDDING)

        first = game.active_player.identifier
        game.act(Bid(first, BidAmount.SHOOT_THE_MOON))

        second = game.active_player.identifier

        # player has changed
        self.assertNotEqual(first, second)

        self.assertEqual((Bid(second, BidAmount.PASS),), game.available_actions(second))
