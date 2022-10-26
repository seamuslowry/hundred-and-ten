'''Test behavior of the Game while it is starting or newly starting'''
from unittest import TestCase

from hundredandten.constants import GameRole
from hundredandten.game import Game
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.people import People
from hundredandten.person import Person


class TestStartOfGame(TestCase):
    '''Unit tests for starting a Game'''

    def test_start_game(self):
        '''Adds the first round when starting a game'''
        game = Game(
            persons=People([Person('1', roles={GameRole.PLAYER}),
                            Person('2', roles={GameRole.PLAYER})]))

        self.assertEqual(0, len(game.rounds))

        game.start_game()

        self.assertEqual(1, len(game.rounds))
        self.assertIsNotNone(game.active_round)
        self.assertEqual(len(game.players), len(game.active_round.bidders))
        self.assertIsNotNone(game.active_round.dealer)
        self.assertIsNotNone(game.active_round.active_player)
        self.assertNotEqual(game.active_round.dealer, game.active_round.active_player)
        self.assertIsNone(game.active_round.active_bidder)

    def test_start_game_with_unjoined_players(self):
        '''Adds the first round when starting a game'''
        game = Game(
            persons=People([Person('1', roles={GameRole.PLAYER}),
                            Person('2', roles={GameRole.PLAYER}),
                            Person('3', roles={GameRole.INVITEE})]))

        self.assertEqual(0, len(game.rounds))

        game.start_game()

        self.assertEqual(1, len(game.rounds))
        self.assertIsNotNone(game.active_round)
        self.assertGreater(len(game.people), len(game.active_round.bidders))
        self.assertEqual(len(game.players), len(game.active_round.bidders))
        self.assertIsNotNone(game.active_round.dealer)
        self.assertIsNotNone(game.active_round.active_player)
        self.assertNotEqual(game.active_round.dealer, game.active_round.active_player)
        self.assertIsNone(game.active_round.active_bidder)

    def test_start_game_when_started(self):
        '''Will not allow restarting a game'''
        game = Game(
            persons=People([Person('1', roles={GameRole.PLAYER}),
                            Person('2', roles={GameRole.PLAYER})]))

        game.start_game()
        self.assertRaises(HundredAndTenError, game.start_game)

    def test_start_game_with_no_players(self):
        '''Will not allow starting a game with no players'''
        game = Game()

        self.assertRaises(HundredAndTenError, game.start_game)
