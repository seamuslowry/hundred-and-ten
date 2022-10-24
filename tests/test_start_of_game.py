'''Test behavior of the Game while it is starting or newly starting'''
from unittest import TestCase

from hundred_and_ten.constants import GameRole
from hundred_and_ten.game import Game
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.person import Person


class TestStartOfGame(TestCase):
    '''Unit tests for starting a Game'''

    def test_start_game(self):
        '''Adds the first round when starting a game'''
        game = Game(
            persons=[Person('1', roles={GameRole.PLAYER}),
                     Person('2', roles={GameRole.PLAYER})])

        self.assertEqual(0, len(game.rounds))

        game.start_game()

        self.assertEqual(1, len(game.rounds))
        self.assertEqual(len(game.people), len(game.rounds[0].unknowns))
        self.assertEqual(0, len(game.rounds[0].bidders))
        self.assertIsNotNone(game.rounds[0].dealer)
        self.assertIsNone(game.rounds[0].active_bidder)

    def test_start_game_when_started(self):
        '''Will not allow restarting a game'''
        game = Game(
            persons=[Person('1', roles={GameRole.PLAYER}),
                     Person('2', roles={GameRole.PLAYER})])

        game.start_game()
        self.assertRaises(HundredAndTenError, game.start_game)

    def test_start_game_with_no_players(self):
        '''Will not allow starting a game with no players'''
        game = Game()

        self.assertRaises(HundredAndTenError, game.start_game)
