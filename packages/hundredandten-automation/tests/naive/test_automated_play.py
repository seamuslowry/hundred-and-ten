"""Test to ensure automated games will play completely"""

from unittest import TestCase

from hundredandten.automation import naive
from hundredandten.automation.state import GameState
from hundredandten.engine.constants import GameStatus
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.game import Game
from hundredandten.engine.player import Player
from hundredandten.testing import arrange

AUTOMATED_SEED = "a92475b9-3df3-458d-b0df-486f9a305015"


class TestAutomatedPlay(TestCase):
    """Unit tests for playing a game with all automated actios"""

    def test_game_will_complete_from_start(self):
        """When playing with all automated actiosn, the game will complete"""
        game = Game(
            seed=AUTOMATED_SEED,
            players=list(
                map(
                    lambda identifier: Player(str(identifier)),
                    range(4),
                )
            ),
        )

        while game.status != GameStatus.WON:
            player_id = game.active_player.identifier
            game.act(
                naive.action(GameState.from_game(game, player_id)).for_player(player_id)
            )

        self.assertIsNotNone(game.winner)

    def test_no_actions_after_completion(self):
        """When playing with all automated players, the game will complete"""
        game = arrange.game(GameStatus.WON, seed=AUTOMATED_SEED)

        self.assertRaises(
            HundredAndTenError,
            naive.action,
            GameState.from_game(game, game.players[0].identifier),
        )
