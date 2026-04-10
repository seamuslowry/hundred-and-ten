"""Test to ensure games are scored properly"""

from unittest import TestCase

from hundredandten.engine.constants import WINNING_SCORE, Status
from hundredandten.testing import arrange

# tests in this file run off of seeded games to avoid setting up everything necessary for the tests
# seeds and their expected values in different situations are recorded here

PLAYER_0_WIN_SEED = "ba297348-77d7-42bb-9164-03712b05ba21"
BIDDER_WINS_IN_DISPUTE_SEED = "cc710b75-f7f5-4c6f-ba6d-4406c3735087"
FIRST_TO_SCORE_WINS_IN_DISPUTE_SEED = "2eb541a3-3160-4b02-a113-efea10a2c2c6"


SEEDS_TO_SCORES = {
    PLAYER_0_WIN_SEED: {"0": 110, "1": 60, "2": 35, "3": 30},
    BIDDER_WINS_IN_DISPUTE_SEED: {"0": 60, "1": 115, "2": 110, "3": 50},
    FIRST_TO_SCORE_WINS_IN_DISPUTE_SEED: {"0": 115, "1": 115, "2": 70, "3": 50},
}


class TestGameScoring(TestCase):
    """Unit tests for scoring a game"""

    def test_start_at_zeroes(self):
        """At game start, scores are all zeroes"""
        game = arrange.game(Status.BIDDING)

        self.assertEqual([0] * len(game.players), list(game.scores.values()))
        self.assertEqual([0] * len(game.players), list(game.scores_by_round[-1].values()))

    def test_win_at_winning_score(self):
        """At the end of the game, the winner has 110"""
        seed = PLAYER_0_WIN_SEED
        game = arrange.game(Status.WON, seed=seed)

        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores_by_round[-1])

    def test_bidder_wins_when_sharing(self):
        """If multiple players including the bidder reach 110, the bidder wins"""
        seed = BIDDER_WINS_IN_DISPUTE_SEED
        game = arrange.game(Status.WON, seed=seed)

        assert game.winner
        assert game.active_round.active_bidder
        self.assertEqual(game.winner.identifier, game.active_round.active_bidder.identifier)
        self.assertTrue(
            len([score for score in game.scores.values() if score >= WINNING_SCORE]) == 2
        )
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores_by_round[-1])

    def test_first_to_score_wins_when_sharing(self):
        """If multiple players NOT including the bidder reach 110, the first to 110 wins"""
        seed = FIRST_TO_SCORE_WINS_IN_DISPUTE_SEED
        game = arrange.game(Status.WON, seed=seed)

        winners = [key for key, value in game.scores.items() if value >= WINNING_SCORE]
        winning_scores = [
            score
            for score in game.score_history
            if score.identifier in winners and score.value >= WINNING_SCORE
        ]

        assert game.winner
        assert game.active_round.active_bidder
        self.assertNotEqual(game.winner.identifier, game.active_round.active_bidder.identifier)
        self.assertEqual(winning_scores[0].identifier, game.winner.identifier)
        self.assertLess(game.scores[game.active_round.active_bidder.identifier], WINNING_SCORE)
        self.assertTrue(len(winners) > 1)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores_by_round[-1])

    def test_available_actions_empty_when_won(self):
        """When game is won, available_actions returns empty tuple"""
        game = arrange.game(Status.WON, seed=PLAYER_0_WIN_SEED)

        # Try to get actions for any player
        actions = game.available_actions(game.players[0].identifier)
        self.assertEqual(actions, ())

    def test_act_does_nothing_when_won(self):
        """Game.act() returns None and doesn't change game state when won"""
        from hundredandten.engine import Bid, BidAmount

        game = arrange.game(Status.WON, seed=PLAYER_0_WIN_SEED)
        rounds_before = len(game.rounds)

        # Try to act - should do nothing
        result = game.act(Bid(game.players[0].identifier, BidAmount.FIFTEEN))

        # Verify returns None
        self.assertIsNone(result)
        # Verify no new rounds created
        self.assertEqual(len(game.rounds), rounds_before)
