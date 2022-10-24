'''Represent a game of Hundred and Ten'''
from uuid import uuid4

from hundred_and_ten.constants import PUBLIC, GameRole, GameStatus, RoundRole
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.person import Person
from hundred_and_ten.round import Round


class Game:
    '''A game of Hundred and Ten'''

    def __init__(self, people=None, rounds=None, accessibility=PUBLIC, uuid=None):
        self.uuid = uuid or uuid4()
        self.accessibility = accessibility
        self.people = people or []
        self.rounds = rounds or []

    def invite(self, inviter, invitee):
        '''Invite a player to the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot invite a player to an in progress game.")
        if not self.__find_or_create_person(inviter) in self.players:
            raise HundredAndTenError("You cannot invite a player to a game you aren't a part of.")

        self.people = self.__upsert_person(self.__find_or_create_person(
            invitee, GameRole.INVITEE))

    def join(self, player):
        '''Add a player to the game'''

        if len(self.players) >= 4:
            raise HundredAndTenError("You cannot join this game. It is at capacity.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot join this game. It has already started.")
        if self.accessibility != PUBLIC and GameRole.INVITEE not in self.__find_or_create_person(
                player).roles:
            raise HundredAndTenError("You cannot join this game. You must be invited first.")

        self.people = self.__upsert_person(self.__find_or_create_person(
            player, GameRole.PLAYER))

    def leave(self, player):
        '''Remove a player from the game'''

        if player == self.organizer.identifier:
            raise HundredAndTenError("The organizer cannot leave the game.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot leave an in-progress game.")

        self.people = map(lambda p: p if player != p.identifier else Person(
            p.identifier, filter(lambda r: r != GameRole.PLAYER, p.roles)), self.people)

    def start_game(self):
        '''Start the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("Cannot start a game that's already started.")
        if len(self.players) < 2:
            raise HundredAndTenError("You cannot play with fewer than two players.")

        self.rounds = [Round(
            players=[
                Person(identifier=self.players[0].identifier, roles={RoundRole.DEALER}),
                map(lambda p: Person(p.identifier), self.players[1:])
            ]
        )]

    @property
    def status(self):
        """The status property."""
        if len(self.rounds) == 0:
            return GameStatus.WAITING_FOR_PLAYERS
        return self.rounds[-1].status

    @property
    def organizer(self):
        """
        The organizer of the game
        If no player has the role, pick a random player
        """
        return next(
            iter(self.__find_people_by_role(GameRole.ORGANIZER) or self.people),
            Person('unknown'))

    @property
    def invitees(self):
        """
        The invitees to the game
        """
        return self.__find_people_by_role(GameRole.INVITEE) or []

    @property
    def players(self):
        """
        The players of the game
        """
        return self.__find_people_by_role(GameRole.PLAYER) or []

    def __find_person_by_identifier(self, identifier):
        '''
        Find a person with the given identifier
        '''
        return next(iter([p for p in self.people if p.identifier == identifier]), None)

    def __find_people_by_role(self, role):
        '''
        Find a person with the given identifier
        '''
        return [p for p in self.people if role in p.roles] or []

    def __find_or_create_person(self, identifier, *roles):
        '''
        Find or create a person with the given attributes
        Provided roles will append, not overwrite
        '''
        person = self.__find_person_by_identifier(identifier) or Person(identifier=identifier)
        person.roles.update(roles or [])
        return person

    def __upsert_person(self, person):
        '''
        Upsert the provided person into the people array
        '''
        return [p for p in self.people if p.identifier != person.identifier] + [person]
