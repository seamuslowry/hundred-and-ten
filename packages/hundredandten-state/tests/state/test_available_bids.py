"""Regression tests for available_bids ordering"""

from unittest import TestCase

from hundredandten.state import BidAmount
from hundredandten.testing import state as build


class TestAvailableBidsSorted(TestCase):
    """Available bids are always returned in ascending numeric order"""

    def test_sorted_ascending_no_active_bid(self):
        """All bids are sorted when there is no active bid yet"""
        state = build.game_state()
        bid_amounts = [a.amount for a in state.available_bids]
        self.assertEqual(bid_amounts, sorted(bid_amounts))

    def test_sorted_ascending_with_active_bid(self):
        """All bids are sorted when there is an active bid (non-dealer perspective)"""
        state = build.game_state(
            bidding_state=build.bidding(active_bid=BidAmount.FIFTEEN)
        )
        bid_amounts = [a.amount for a in state.available_bids]
        self.assertEqual(bid_amounts, sorted(bid_amounts))

    def test_sorted_ascending_dealer_steal(self):
        """Bids are sorted even when dealer-steal inserts the active bid amount

        Regression: before the fix, higher_bids was built by iterating BidAmount in
        declaration order (60, 30, 25, 20, …), producing an unsorted list like
        [PASS, steal_bid, SHOOT_THE_MOON, THIRTY, …].
        """
        state = build.game_state(
            table_info=build.table(dealer_seat=0),
            bidding_state=build.bidding(active_bid=BidAmount.FIFTEEN),
        )
        bid_amounts = [a.amount for a in state.available_bids]

        # Steal bid must be present
        self.assertIn(BidAmount.FIFTEEN, bid_amounts)
        # And everything must be in ascending order
        self.assertEqual(bid_amounts, sorted(bid_amounts))
