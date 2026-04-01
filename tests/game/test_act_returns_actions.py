"""Test that Game.act() returns the correct action chain"""

from unittest import TestCase

from hundredandten.actions import Bid
from hundredandten.constants import BidAmount, RoundStatus
from hundredandten.game import Game
from hundredandten.player import HumanPlayer, NaiveAutomatedPlayer
from tests import arrange


class TestActReturnsActions(TestCase):
    """Unit tests verifying Game.act() returns the correct action chain"""

    def test_act_returns_single_action_when_no_automated_player(self):
        """When active player acts and no automated players follow, returns just that action"""
        game = arrange.game(RoundStatus.BIDDING)

        player_id = game.active_round.active_player.identifier
        action = Bid(player_id, BidAmount.FIFTEEN)
        result = game.act(action)

        self.assertEqual([action], result)

    def test_act_returns_action_chain_with_automated_player_in_bidding(self):
        """When human acts and automated players follow, returns full chain"""
        game = Game(
            players=[
                NaiveAutomatedPlayer("auto0"),
                NaiveAutomatedPlayer("auto1"),
                NaiveAutomatedPlayer("auto2"),
                HumanPlayer("human"),
            ],
            seed="test_seed",
        )

        human_action = Bid("human", BidAmount.FIFTEEN)
        result = game.act(human_action)

        self.assertIn(human_action, result)
        self.assertGreater(len(result), 1)
