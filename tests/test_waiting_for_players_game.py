'''Test behavior of the Game while it is Waiting for Players'''
from unittest import TestCase

from hundred_and_ten.constants import Accessibility, GameRole, GameStatus
from hundred_and_ten.game import Game
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.person import Person
from hundred_and_ten.round import Round


class TestWaitingForPlayersGame(TestCase):
    '''Unit tests for a Waiting for Players Game'''

    def test_default_inits_to_waiting(self):
        '''Game status defaults to waiting for players'''
        game = Game()

        self.assertIsNotNone(game.uuid)
        self.assertEqual(game.status, GameStatus.WAITING_FOR_PLAYERS)

    def test_invite(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        inviter = 'inviter'
        game = Game([Person(inviter, roles={GameRole.PLAYER})])

        self.assertFalse(invitee in map(lambda i: i.identifier, game.invitees))

        game.invite(inviter, invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.invitees))

    def test_invite_as_non_player(self):
        '''Test inviting a player without being in the game yourself'''
        invitee = 'invitee'
        inviter = 'inviter'
        game = Game()

        self.assertRaises(HundredAndTenError, game.invite, inviter, invitee)

    def test_invite_after_start(self):
        '''Test inviting a player after the game has started'''
        invitee = 'invitee'
        inviter = 'inviter'
        game = Game([Person(inviter, roles={GameRole.PLAYER})], rounds=[Round()])

        self.assertRaises(HundredAndTenError, game.invite, inviter, invitee)

    def test_join(self):
        '''Test a player joining a game'''
        invitee = 'invitee'
        game = Game([Person(invitee, {GameRole.INVITEE})])

        game.join(invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.players))

    def test_join_after_start(self):
        '''Test joining a game after it has started'''
        invitee = 'invitee'
        game = Game([Person(invitee, {GameRole.INVITEE})], rounds=[Round()])

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_too_many_players(self):
        '''Test joining a full game'''
        invitee = 'invitee'
        game = Game(
            list(map(lambda i: Person(str(i),
                                      {GameRole.PLAYER}),
                     range(4))) + [Person(invitee)])

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_not_invited_to_private(self):
        '''Test joining a private game without an invite'''
        invitee = 'invitee'
        game = Game(accessibility=Accessibility.PRIVATE)

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
        game = Game([Person(identifier=organizer, roles={GameRole.ORGANIZER})])

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

    def test_leave(self):
        '''Test leaving a game as a non player'''
        no_one = 'no one'
        game = Game()

        game.leave(no_one)

        self.assertNotIn(Person(no_one), game.players)

    def test_leave_as_invited_player(self):
        '''Test leaving a game as an invited player'''
        invited_player = 'invited'
        game = Game([Person('organizer', {GameRole.ORGANIZER}), Person(
            invited_player, {GameRole.INVITEE, GameRole.PLAYER})])

        self.assertIn(Person(invited_player), game.players)

        game.leave(invited_player)

        self.assertNotIn(Person(invited_player), game.players)

    def test_leave_as_organizer(self):
        '''Test leaving a game as an invited player'''
        organizer = 'organizer'
        game = Game([Person(organizer, {GameRole.ORGANIZER, GameRole.PLAYER})])

        self.assertRaises(HundredAndTenError, game.leave, organizer)

    def test_leave_after_start(self):
        '''Test leaving a game after it has started'''
        identifier = 'id'
        game = Game([Person('organizer', {GameRole.ORGANIZER}), Person(
            identifier, {GameRole.PLAYER})], rounds=[Round()])

        self.assertRaises(HundredAndTenError, game.leave, identifier)
