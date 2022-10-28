'''Represent a game of Hundred and Ten'''
from typing import Optional

from hundredandten.constants import (HAND_SIZE, Accessibility, AnyStatus,
                                     BidAmount, GameRole, GameStatus,
                                     RoundRole)
from hundredandten.deck import Deck
from hundredandten.group import Group, Person, Player, Players
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.round import Round


class Game:
    '''A game of Hundred and Ten'''

    def __init__(
            self, persons: Optional[Group] = None, rounds: Optional[list[Round]] = None,
            accessibility: Optional[Accessibility] = Accessibility.PUBLIC) -> None:
        self.accessibility = accessibility
        self.people = persons or Group()
        self.rounds = rounds or []

    def invite(self, inviter: str, invitee: str) -> None:
        '''Invite a player to the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot invite a player to an in progress game.")
        if self.people.find_or_use(Person(inviter)) not in self.players:
            raise HundredAndTenError("You cannot invite a player to a game you aren't a part of.")

        self.people.upsert(self.people.find_or_use(Person(invitee, {GameRole.INVITEE})))

    def join(self, player: str) -> None:
        '''Add a player to the game'''

        if len(self.players) >= 4:
            raise HundredAndTenError("You cannot join this game. It is at capacity.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot join this game. It has already started.")
        if (self.accessibility != Accessibility.PUBLIC
                and GameRole.INVITEE not in self.people.find_or_use(Player(player)).roles):
            raise HundredAndTenError("You cannot join this game. You must be invited first.")

        self.people.upsert(self.people.find_or_use(Person(player, {GameRole.PLAYER})))

    def leave(self, player: str) -> None:
        '''Remove a player from the game'''

        if player == self.organizer.identifier:
            raise HundredAndTenError("The organizer cannot leave the game.")
        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot leave an in-progress game.")

        person = Person(player)

        if person in self.people:
            self.people.remove(person)

    def start_game(self) -> None:
        '''Start the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("Cannot start a game that's already started.")
        if len(self.players) < 2:
            raise HundredAndTenError("You cannot play with fewer than two players.")

        deck = Deck()

        round_players = Players(map(lambda p: Player(
            p.identifier, hand=deck.draw(HAND_SIZE)), self.players))
        dealer = round_players[0]
        round_players.add_role(dealer.identifier, RoundRole.DEALER)

        self.rounds = [Round(players=round_players, deck=deck)]

    def bid(self, identifier: str, amount: BidAmount) -> None:
        '''Place a bid from the identified player'''
        self.active_round.bid(identifier, amount)

    def unpass(self, identifier: str) -> None:
        '''Discount a pre-pass bid from the identified player'''
        self.active_round.unpass(identifier)

    @property
    def status(self) -> AnyStatus:
        """The status property."""
        if not self.rounds:
            return GameStatus.WAITING_FOR_PLAYERS
        return self.active_round.status

    @property
    def active_round(self) -> Round:
        """The active round"""
        if not self.rounds:
            raise HundredAndTenError("No active round found.")
        return self.rounds[-1]

    @property
    def active_player(self) -> Person:
        """The active player"""
        return self.active_round.active_player

    @property
    def organizer(self) -> Person:
        """
        The organizer of the game
        If no player has the role, pick a random player
        """
        return next(
            iter(self.people.by_role(GameRole.ORGANIZER) or self.people),
            Person('unknown'))

    @property
    def invitees(self) -> Group:
        """
        The invitees to the game
        """
        return self.people.by_role(GameRole.INVITEE)

    @property
    def players(self) -> Group:
        """
        The players of the game
        """
        return self.people.by_role(GameRole.PLAYER)
