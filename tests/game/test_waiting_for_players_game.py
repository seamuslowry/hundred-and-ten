'''Test behavior of the Game while it is Waiting for Players'''
from unittest import TestCase
from uuid import UUID

from hundredandten import RoundStatus
from hundredandten.game import Game
from hundredandten.group import Player, Group
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestNewGame(TestCase):
    '''Unit tests for a New Game'''

    def test_will_not_allow_zero_players(self):
        '''Game throws if initialized with no players'''
        self.assertRaises(HundredAndTenError, lambda: Game())

    def test_will_not_allow_one_players(self):
        '''Game throws if initialized with one player'''
        self.assertRaises(HundredAndTenError, lambda: Game(Group([Player('one')])))

    def test_will_not_allow_give_players(self):
        '''Game throws if initialized with give players'''
        self.assertRaises(HundredAndTenError, lambda: Game(Group(list(map(
                lambda identifier: Player(str(identifier)),
                range(5))))))

    def test_generates_seed_when_none_passed(self):
        '''Game defaults a seed if none is passed'''
        game = arrange.game(RoundStatus.BIDDING)

        self.assertIsNotNone(game.seed)
        self.assertEqual(str(UUID(game.seed)), game.seed)

    def test_default_inits_to_in_progress_with_one_round(self):
        '''Game status defaults to waiting for players'''
        game = arrange.game(RoundStatus.BIDDING)

        self.assertEqual(game.status, RoundStatus.BIDDING)
        self.assertIsNotNone(game.active_round)
        self.assertEqual(1, len(game.rounds))