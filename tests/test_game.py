'''Game unit tests'''
from unittest import TestCase

from hundred_and_ten.constants import GameStatus
from hundred_and_ten.game import Game
from hundred_and_ten.game_players import GamePlayers
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError


class TestCreateGame(TestCase):
    '''Game unit tests'''

    def test_default_init(self):
        '''Test init a game with minimal info'''
        organizer = 'organizer'
        game = Game(GamePlayers(organizer))

        self.assertIsNotNone(game.uuid)
        self.assertEqual(game.status, GameStatus.WAITING_FOR_PLAYERS)
        self.assertTrue(game.player_data.organizer in game.player_data.players)

    def test_invite(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = Game(GamePlayers(''))

        self.assertFalse(game.player_data.invitees)

        game.invite(invitee)

        self.assertTrue(invitee in game.player_data.invitees)

    def test_join(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = Game(GamePlayers('', invitees=['invitee']))

        game.join(invitee)

        self.assertTrue(invitee in game.player_data.players)

    def test_join_too_many_players(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = Game(GamePlayers('', players=list(range(4)), invitees=['invitee']))

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_not_invited_to_private(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = Game(GamePlayers(''), accessibility='PRIVATE')

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_not_invited_to_public(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = Game(GamePlayers(''))

        game.join(invitee)

        self.assertTrue(invitee in game.player_data.players)
