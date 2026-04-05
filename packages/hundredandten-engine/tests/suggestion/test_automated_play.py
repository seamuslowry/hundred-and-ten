# """Test to ensure automated games will play completely"""

# from unittest import TestCase

# from hundredandten.engine.actions import Action, Bid
# from hundredandten.engine.constants import BidAmount, GameStatus
# from hundredandten.engine.errors import HundredAndTenError
# from hundredandten.engine.game import Game
# from hundredandten.engine.player import NaiveAutomatedPlayer

# from tests import arrange

# AUTOMATED_SEED = "a92475b9-3df3-458d-b0df-486f9a305015"


# class TestAutomatedPlay(TestCase):
#     """Unit tests for playing a game with all machine players"""

#     def test_game_will_complete_from_start(self):
#         """When playing with all automated players, the game will complete"""
#         game = Game(
#             seed=AUTOMATED_SEED,
#             players=list(
#                 map(
#                     lambda identifier: NaiveAutomatedPlayer(str(identifier)),
#                     range(4),
#                 )
#             ),
#         )

#         self.assertIsNotNone(game.winner)

#     def test_no_actions_after_completion(self):
#         """When playing with all automated players, the game will complete"""
#         game = arrange.game(GameStatus.WON, seed=AUTOMATED_SEED)

#         self.assertRaises(
#             HundredAndTenError,
#             NaiveAutomatedPlayer(game.players[0].identifier).act,
#             game.game_state_for(game.players[0].identifier),
#         )

#     def test_initial_actions_dont_automate(self):
#         """When starting a game with automated players, initial actions do not trigger automation"""
#         automated_game_from_start = Game(
#             seed=AUTOMATED_SEED,
#             players=[
#                 NaiveAutomatedPlayer(identifier="automated0"),
#                 NaiveAutomatedPlayer(identifier="automated1"),
#                 NaiveAutomatedPlayer(identifier="automated2"),
#                 NaiveAutomatedPlayer(identifier="automated3"),
#             ],
#         )

#         initial_actions: list[Action] = [
#             Bid(identifier="automated1", amount=BidAmount.FIFTEEN),
#             Bid(identifier="automated2", amount=BidAmount.TWENTY),
#             Bid(identifier="automated3", amount=BidAmount.TWENTY_FIVE),
#             Bid(identifier="automated0", amount=BidAmount.PASS),
#             Bid(identifier="automated1", amount=BidAmount.SHOOT_THE_MOON),
#         ]

#         automated_game_after_start = Game(
#             seed=AUTOMATED_SEED,
#             players=[
#                 NaiveAutomatedPlayer(identifier="automated0"),
#                 NaiveAutomatedPlayer(identifier="automated1"),
#                 NaiveAutomatedPlayer(identifier="automated2"),
#                 NaiveAutomatedPlayer(identifier="automated3"),
#             ],
#             initial_actions=initial_actions,
#         )

#         self.assertEqual(
#             initial_actions, automated_game_after_start.actions[: len(initial_actions)]
#         )
#         self.assertNotEqual(
#             initial_actions, automated_game_from_start.actions[: len(initial_actions)]
#         )
