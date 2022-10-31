'''Represent a game of Hundred and Ten'''
from typing import Optional

from hundredandten.constants import (HAND_SIZE, Accessibility, AnyStatus,
                                     BidAmount, GameRole, GameStatus,
                                     RoundRole, RoundStatus)
from hundredandten.deck import Deck
from hundredandten.group import Group, Person, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.round import Round


class Game:
    '''A game of Hundred and Ten'''

    def __init__(
            self, persons: Optional[Group[Person]] = None, rounds: Optional[list[Round]] = None,
            accessibility: Optional[Accessibility] = Accessibility.PUBLIC) -> None:
        self.accessibility = accessibility
        self.people = persons or Group[Person]()
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

        self.__new_round(self.players[0].identifier)

    def bid(self, identifier: str, amount: BidAmount) -> None:
        '''Place a bid from the identified player'''
        self.active_round.bid(identifier, amount)
        if self.active_round.status == RoundStatus.COMPLETED_NO_BIDDERS:
            current_dealer = self.active_round.dealer.identifier
            next_dealer = current_dealer if len(
                self.rounds) < 3 else self.players.after(current_dealer).identifier
            self.__new_round(next_dealer)

    def unpass(self, identifier: str) -> None:
        '''Discount a pre-pass bid from the identified player'''
        self.active_round.unpass(identifier)

    def __new_round(self, dealer: str) -> None:
        deck = Deck()

        round_players = Group[Player](map(lambda p: Player(
            p.identifier, hand=deck.draw(HAND_SIZE)), self.players))
        round_players.add_role(dealer, RoundRole.DEALER)

        self.rounds.append(Round(players=round_players, deck=deck))

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
    def invitees(self) -> Group[Person]:
        """
        The invitees to the game
        """
        return self.people.by_role(GameRole.INVITEE)

    @property
    def players(self) -> Group[Person]:
        """
        The players of the game
        """
        return self.people.by_role(GameRole.PLAYER)
