'''Represent a game of Hundred and Ten'''
from typing import Optional
from uuid import uuid4

from hundred_and_ten import people
from hundred_and_ten.constants import (Accessibility, GameRole, GameStatus,
                                       RoundRole)
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.person import Person
from hundred_and_ten.round import Round


class Game:
    '''A game of Hundred and Ten'''

    def __init__(
            self, persons: Optional[list[Person]] = None, rounds: Optional[list[Round]] = None,
            accessibility: Optional[Accessibility] = Accessibility.PUBLIC,
            uuid: Optional[str] = None):
        self.uuid = uuid or uuid4()
        self.accessibility = accessibility
        self.people = persons or []
        self.rounds = rounds or []

    def invite(self, inviter, invitee):
        '''Invite a player to the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot invite a player to an in progress game.")
        if not people.find_or_create(self.people, inviter) in self.players:
            raise HundredAndTenError("You cannot invite a player to a game you aren't a part of.")

        self.people = people.upsert(self.people, people.find_or_create(self.people,
                                                                       invitee, GameRole.INVITEE))

    def join(self, player):
        '''Add a player to the game'''

        if len(self.players) >= 4:
            raise HundredAndTenError("You cannot join this game. It is at capacity.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot join this game. It has already started.")
        if (self.accessibility != Accessibility.PUBLIC
                and GameRole.INVITEE not in people.find_or_create(self.people, player).roles):
            raise HundredAndTenError("You cannot join this game. You must be invited first.")

        self.people = people.upsert(self.people, people.find_or_create(self.people,
                                                                       player, GameRole.PLAYER))

    def leave(self, player):
        '''Remove a player from the game'''

        if player == self.organizer.identifier:
            raise HundredAndTenError("The organizer cannot leave the game.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot leave an in-progress game.")

        self.people = list(map(lambda p: p if player != p.identifier else Person(
            p.identifier, set(filter(lambda r: r != GameRole.PLAYER, p.roles))), self.people))

    def start_game(self):
        '''Start the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("Cannot start a game that's already started.")
        if len(self.players) < 2:
            raise HundredAndTenError("You cannot play with fewer than two players.")

        round_players = list(map(lambda p: Person(p.identifier, {RoundRole.UNKNOWN}), self.people))

        self.rounds = [
            Round(
                players=people.add_role(
                    round_players, round_players[0].identifier, RoundRole.DEALER))]

    @ property
    def status(self):
        """The status property."""
        if len(self.rounds) == 0:
            return GameStatus.WAITING_FOR_PLAYERS
        return self.rounds[-1].status

    @ property
    def organizer(self):
        """
        The organizer of the game
        If no player has the role, pick a random player
        """
        return next(
            iter(people.by_role(self.people, GameRole.ORGANIZER) or self.people),
            Person('unknown'))

    @ property
    def invitees(self):
        """
        The invitees to the game
        """
        return people.by_role(self.people, GameRole.INVITEE) or []

    @ property
    def players(self):
        """
        The players of the game
        """
        return people.by_role(self.people, GameRole.PLAYER) or []
