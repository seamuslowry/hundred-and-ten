'''Test behavior of the Game while it is starting or newly starting'''
from unittest import TestCase

from hundredandten.constants import HAND_SIZE, RoundStatus
from hundredandten.game import Game
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestStartOfGame(TestCase):
    '''Unit tests for starting a Game'''

    def test_start_game(self):
        '''Adds the first round when starting a game'''
        game = arrange.game(RoundStatus.BIDDING)

        self.assertEqual(1, len(game.rounds))
        self.assertIsNotNone(game.active_round.deck.seed)
        self.assertIsNotNone(game.active_round)
        self.assertEqual(len(game.players), len(game.active_round.bidders))
        self.assertIsNotNone(game.active_round.dealer)
        self.assertIsNotNone(game.active_round.active_player)
        self.assertNotEqual(game.active_round.dealer, game.active_round.active_player)
        self.assertIsNone(game.active_round.active_bidder)
        self.assertTrue(all(len(p.hand) == HAND_SIZE for p in game.active_round.players))

    def test_games_dont_have_same_seed(self):
        '''Two different games' decks will have different seeds'''
        game_1 = arrange.game(RoundStatus.BIDDING)
        game_2 = arrange.game(RoundStatus.BIDDING)

        self.assertIsNotNone(game_1.active_round.deck.seed)
        self.assertIsNotNone(game_2.active_round.deck.seed)
        self.assertNotEqual(game_2.active_round.deck.seed, game_1.active_round.deck.seed)

    def test_game_with_no_players(self):
        '''Will not allow creating a game with no players'''
        self.assertRaises(HundredAndTenError, Game)
