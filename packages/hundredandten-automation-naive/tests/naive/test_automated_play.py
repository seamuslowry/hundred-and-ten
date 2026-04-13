"""Test to ensure automated games will play completely"""

from unittest import TestCase

from hundredandten.automation import naive
from hundredandten.automation.engineadapter import EngineAdapter
from hundredandten.engine.constants import Status
from hundredandten.engine.game import Game
from hundredandten.engine.player import Player
from hundredandten.testing import arrange

AUTOMATED_SEED = "a92475b9-3df3-458d-b0df-486f9a305015"


def action_for(game: Game, player: str):
    """Bridge: wire naive.action_for to the engine Game type"""
    return EngineAdapter.available_action_for_player(
        naive.action_for(EngineAdapter.state_from_engine(game, player)), player
    )


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

        while game.status != Status.WON:
            player_id = game.active_player.identifier
            game.act(action_for(game, player_id))

        self.assertIsNotNone(game.winner)

    def test_no_actions_after_completion(self):
        """When playing with all automated players, the game will complete"""
        game = arrange.game(Status.WON, seed=AUTOMATED_SEED)

        self.assertRaises(
            naive.AutomationError,
            action_for,
            game,
            game.players[0].identifier,
        )
