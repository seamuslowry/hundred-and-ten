'''Represent a game of Hundred and Ten'''
from typing import Optional
from uuid import uuid4

from hundred_and_ten.constants import (Accessibility, AnyStatus, GameRole,
                                       GameStatus, RoundRole)
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.people import People
from hundred_and_ten.person import Person
from hundred_and_ten.round import Round


class Game:
    '''A game of Hundred and Ten'''

    def __init__(
            self, persons: Optional[People] = None, rounds: Optional[list[Round]] = None,
            accessibility: Optional[Accessibility] = Accessibility.PUBLIC,
            uuid: Optional[str] = None):
        self.uuid = uuid or uuid4()
        self.accessibility = accessibility
        self.people = persons or People()
        self.rounds = rounds or []

    def invite(self, inviter: str, invitee: str):
        '''Invite a player to the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot invite a player to an in progress game.")
        if self.people.find_or_create(inviter) not in self.players:
            raise HundredAndTenError("You cannot invite a player to a game you aren't a part of.")

        self.people.upsert(self.people.find_or_create(invitee, GameRole.INVITEE))

    def join(self, player: str):
        '''Add a player to the game'''

        if len(self.players) >= 4:
            raise HundredAndTenError("You cannot join this game. It is at capacity.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot join this game. It has already started.")
        if (self.accessibility != Accessibility.PUBLIC
                and GameRole.INVITEE not in self.people.find_or_create(player).roles):
            raise HundredAndTenError("You cannot join this game. You must be invited first.")

        self.people.upsert(self.people.find_or_create(player, GameRole.PLAYER))

    def leave(self, player: str):
        '''Remove a player from the game'''

        if player == self.organizer.identifier:
            raise HundredAndTenError("The organizer cannot leave the game.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot leave an in-progress game.")

        person = Person(player)

        if person in self.people:
            self.people.remove(person)

    def start_game(self):
        '''Start the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("Cannot start a game that's already started.")
        if len(self.players) < 2:
            raise HundredAndTenError("You cannot play with fewer than two players.")

        round_players = People(map(lambda p: Person(
            p.identifier, {RoundRole.UNKNOWN}), self.people))
        round_players.add_role(round_players[0].identifier, RoundRole.DEALER)

        self.rounds = [Round(players=round_players)]

    @ property
    def status(self) -> AnyStatus:
        """The status property."""
        if len(self.rounds) == 0:
            return GameStatus.WAITING_FOR_PLAYERS
        return self.rounds[-1].status

    @ property
    def organizer(self) -> Person:
        """
        The organizer of the game
        If no player has the role, pick a random player
        """
        return next(
            iter(self.people.by_role(GameRole.ORGANIZER) or self.people),
            Person('unknown'))

    @ property
    def invitees(self) -> list[Person]:
        """
        The invitees to the game
        """
        return self.people.by_role(GameRole.INVITEE) or []

    @ property
    def players(self) -> list[Person]:
        """
        The players of the game
        """
        return self.people.by_role(GameRole.PLAYER) or []
