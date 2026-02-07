"""Test to ensure automated games will play completely"""

from unittest import TestCase

from hundredandten.actions import Action, Bid
from hundredandten.constants import BidAmount, GameStatus
from hundredandten.game import Game
from hundredandten.group import Group, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange

AUTOMATED_SEED = "a92475b9-3df3-458d-b0df-486f9a305015"


class TestAutomatedPlay(TestCase):
    """Unit tests for playing a game with all machine players"""

    def test_game_will_complete_from_start(self):
        """When playing with all automated players, the game will complete"""
        game = arrange.automated_game(seed=AUTOMATED_SEED)

        self.assertIsNotNone(game.winner)

    def test_no_suggestions_after_completion(self):
        """When playing with all automated players, the game will complete"""
        game = arrange.game(GameStatus.WON, seed=AUTOMATED_SEED)

        self.assertRaises(HundredAndTenError, game.suggestion)

    def test_initial_moves_dont_automate(self):
        """When starting a game with automated players, initial moves do not trigger automation"""
        automated_game_from_start = Game(
            seed=AUTOMATED_SEED,
            players=Group(
                [
                    Player(identifier="unautomated", automate=True),
                    Player(identifier="automated1", automate=True),
                    Player(identifier="automated2", automate=True),
                    Player(identifier="automated3", automate=True),
                ]
            ),
        )

        initial_moves: list[Action] = [
            Bid(identifier="automated1", amount=BidAmount.FIFTEEN),
            Bid(identifier="automated2", amount=BidAmount.TWENTY),
            Bid(identifier="automated3", amount=BidAmount.TWENTY_FIVE),
            Bid(identifier="unautomated", amount=BidAmount.PASS),
            Bid(identifier="automated1", amount=BidAmount.SHOOT_THE_MOON),
        ]

        automated_game_after_start = Game(
            seed=AUTOMATED_SEED,
            players=Group(
                [
                    Player(identifier="unautomated", automate=True),
                    Player(identifier="automated1", automate=True),
                    Player(identifier="automated2", automate=True),
                    Player(identifier="automated3", automate=True),
                ]
            ),
            initial_moves=initial_moves,
        )

        self.assertEqual(
            initial_moves, automated_game_after_start.moves[: len(initial_moves)]
        )
        self.assertNotEqual(
            initial_moves, automated_game_from_start.moves[: len(initial_moves)]
        )
