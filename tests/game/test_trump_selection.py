'''Test behavior of the Game when selecting trumps'''
from unittest import TestCase

from hundredandten.constants import RoundStatus, SelectableSuit
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests.game_setup import setup_game


class TestTrumpSelection(TestCase):
    '''Unit tests for ending the trump selection stage'''

    def test_selecting_trump_outside_status(self):
        '''Can only select trump during the trump selection phase'''

        game = setup_game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, game.select_trump,
                          game.active_round.active_player.identifier, SelectableSuit.CLUBS)
        self.assertIsNone(game.active_round.trump)

    def test_selecting_trump_as_inactive_player(self):
        '''Only the active bidder can select trump'''

        game = setup_game(RoundStatus.TRUMP_SELECTION)

        self.assertRaises(HundredAndTenError, game.select_trump,
                          game.active_round.inactive_players[0].identifier, SelectableSuit.CLUBS)
        self.assertIsNone(game.active_round.trump)

    def test_selecting_trump(self):
        '''The active bidder can select trump'''

        game = setup_game(RoundStatus.TRUMP_SELECTION)

        trump = SelectableSuit.DIAMONDS

        game.select_trump(game.active_round.active_player.identifier, trump)

        self.assertEqual(trump, game.active_round.trump)
        self.assertEqual(RoundStatus.TRICKS, game.status)
