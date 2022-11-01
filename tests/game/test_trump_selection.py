'''Test behavior of the Game when selecting trumps'''
from unittest import TestCase

from hundredandten.constants import (BidAmount, GameRole, RoundStatus,
                                     SelectableSuit)
from hundredandten.game import Game
from hundredandten.group import Group, Person
from hundredandten.hundred_and_ten_error import HundredAndTenError


class TestTrumpSelection(TestCase):
    '''Unit tests for ending the trump selection stage'''

    def get_trump_selection_game(self):
        '''Return a game in the trump selection status'''
        game = Game(
            people=Group(
                [Person('1', roles={GameRole.PLAYER}),
                 Person('2', roles={GameRole.PLAYER})]))
        game.start_game()
        game.bid(game.active_round.active_player.identifier, BidAmount.PASS)
        game.bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)
        return game

    def test_selecting_trump_outside_status(self):
        '''Can only select trump during the trump selection phase'''

        game = Game(
            people=Group(
                [Person('1', roles={GameRole.PLAYER}),
                 Person('2', roles={GameRole.PLAYER})]))

        game.start_game()
        self.assertRaises(HundredAndTenError, game.select_trump,
                          game.active_round.active_player.identifier, SelectableSuit.CLUBS)
        self.assertIsNone(game.active_round.trump)

    def test_selecting_trump_as_inactive_player(self):
        '''Only the active bidder can select trump'''

        game = self.get_trump_selection_game()

        self.assertRaises(HundredAndTenError, game.select_trump,
                          game.active_round.inactive_players[0].identifier, SelectableSuit.CLUBS)
        self.assertIsNone(game.active_round.trump)

    def test_selecting_trump(self):
        '''The active bidder can select trump'''

        game = self.get_trump_selection_game()
        trump = SelectableSuit.DIAMONDS

        game.select_trump(game.active_round.active_player.identifier, trump)

        self.assertEqual(trump, game.active_round.trump)
        self.assertEqual(RoundStatus.TRICKS, game.status)
