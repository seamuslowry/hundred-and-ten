'''Provide a classe to represent a game of Hundred and Ten'''
from uuid import uuid4

from hundred_and_ten.constants import PUBLIC, GameStatus, PersonRole
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.person import Person


class Game:
    '''A Game of Hundred and Ten'''

    def __init__(self, people=None, accessibility=PUBLIC, uuid=None):
        self.uuid = uuid or uuid4()
        self.accessibility = accessibility
        self.people = people or []

    def invite(self, invitee):
        '''Invite a player to the game'''
        self.people = self.__upsert_person(self.__find_or_create_person(
            invitee, PersonRole.INVITEE))

    def join(self, player):
        '''Add a player to the game'''

        below_player_cap = len(self.players) < 4
        waiting_for_players = self.status == GameStatus.WAITING_FOR_PLAYERS
        public_game = self.accessibility == PUBLIC
        invited = not self.__find_or_create_person(player).roles.isdisjoint(
            [PersonRole.INVITEE, PersonRole.ORGANIZER])

        if waiting_for_players and below_player_cap and (public_game or invited):
            self.people = self.__upsert_person(self.__find_or_create_person(
                player, PersonRole.PLAYER))
        else:
            raise HundredAndTenError(
                ("Cannot join this game."
                 " It is either at capacity or you have not received an invitation."))

    @property
    def status(self):
        """The status property."""
        return GameStatus.WAITING_FOR_PLAYERS

    @property
    def organizer(self):
        """
        The organizer of the game
        If no player has the role, pick a random player
        """
        return next(
            iter(self.__find_people_by_role(PersonRole.ORGANIZER) or self.people),
            Person('unknown'))

    @property
    def invitees(self):
        """
        The invitees to the game
        """
        return self.__find_people_by_role(PersonRole.INVITEE) or []

    @property
    def players(self):
        """
        The players of the game
        """
        return self.__find_people_by_role(PersonRole.PLAYER) or []

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
