"""Test behavior of the Game when selecting trumps"""

from unittest import TestCase

from hundredandten.deck import SelectableSuit
from hundredandten.engine.actions import SelectTrump
from hundredandten.engine.constants import Status
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.testing import arrange


class TestTrumpSelection(TestCase):
    """Unit tests for ending the trump selection stage"""

    def test_selecting_trump_outside_status(self):
        """Can only select trump during the trump selection phase"""

        game = arrange.game(Status.BIDDING)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            SelectTrump(
                game.active_round.active_player.identifier, SelectableSuit.CLUBS
            ),
        )
        self.assertIsNone(game.active_round.trump)

    def test_selecting_trump_as_inactive_player(self):
        """Only the active bidder can select trump"""

        game = arrange.game(Status.TRUMP_SELECTION)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            SelectTrump(
                game.active_round.inactive_players[0].identifier, SelectableSuit.CLUBS
            ),
        )
        self.assertIsNone(game.active_round.trump)

    def test_selecting_trump(self):
        """The active bidder can select trump"""

        game = arrange.game(Status.TRUMP_SELECTION)

        select = SelectTrump(
            game.active_round.active_player.identifier, SelectableSuit.DIAMONDS
        )

        game.act(select)

        self.assertEqual(select.suit, game.active_round.trump)
        self.assertEqual(Status.DISCARD, game.status)
        self.assertEqual(select, game.actions[-1])
