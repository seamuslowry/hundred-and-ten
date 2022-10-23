'''Game unit tests'''
from unittest import TestCase

from hundred_and_ten.constants import GameStatus, PersonRole
from hundred_and_ten.game import Game
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.person import Person


class TestCreateGame(TestCase):
    '''Game unit tests'''

    def test_default_init(self):
        '''Test init a game with minimal info'''
        game = Game()

        self.assertIsNotNone(game.uuid)
        self.assertEqual(game.status, GameStatus.WAITING_FOR_PLAYERS)

    def test_invite(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = Game()

        self.assertFalse(invitee in map(lambda i: i.identifier, game.invitees))

        game.invite(invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.invitees))

    def test_join(self):
        '''Test a player joining a game'''
        invitee = 'invitee'
        game = Game([Person(invitee, {PersonRole.INVITEE})])

        game.join(invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.players))

    def test_join_too_many_players(self):
        '''Test joining a full game'''
        invitee = 'invitee'
        game = Game(
            list(map(lambda i: Person(str(i),
                                      [PersonRole.PLAYER]),
                     range(4))) + [Person(invitee)])

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_not_invited_to_private(self):
        '''Test joining a private game without an invite'''
        invitee = 'invitee'
        game = Game(accessibility='PRIVATE')

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_not_invited_to_public(self):
        '''Test joining a public game without an invite'''
        invitee = 'invitee'
        game = Game()

        game.join(invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.players))

    def test_determines_organizer(self):
        '''Test finding organizer'''
        organizer = 'organizer'
        game = Game([Person(identifier=organizer, roles={PersonRole.ORGANIZER})])

        self.assertEqual(game.organizer.identifier, organizer)

    def test_determines_organizer_without_one(self):
        '''Test finding organizer when no one has the role specifically'''
        organizer = 'organizer'
        game = Game([Person(identifier=organizer)])

        self.assertEqual(game.organizer.identifier, organizer)

    def test_determines_organizer_with_no_players(self):
        '''Test finding organizer when there are no players'''
        game = Game()

        self.assertIsNotNone(game.organizer)
