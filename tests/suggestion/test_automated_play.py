'''Test to ensure automated games will play completely'''
from unittest import TestCase

from hundredandten.constants import GameStatus
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange

AUTOMATED_SEED = 'a92475b9-3df3-458d-b0df-486f9a305015'


class TestAutomatedPlay(TestCase):
    '''Unit tests for playing a game with all machine players'''

    def test_game_will_complete(self):
        '''When playing with all automated players, the game will complete'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS, seed=AUTOMATED_SEED)
        for player in game.players:
            game.automate(player.identifier)

        game.start_game()

        self.assertIsNotNone(game.winner)

    def test_no_suggestions_after_completion(self):
        '''When playing with all automated players, the game will complete'''
        game = arrange.game(GameStatus.WON, seed=AUTOMATED_SEED)

        self.assertRaises(HundredAndTenError, game.suggestion)
