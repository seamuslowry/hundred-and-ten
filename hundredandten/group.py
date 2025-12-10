"""Interact with a list of people"""

from dataclasses import dataclass, field
from typing import Optional

from hundredandten.constants import AnyRole
from hundredandten.deck import Card
from hundredandten.hundred_and_ten_error import HundredAndTenError


@dataclass
class Player:
    """A class to keep track of player information"""

    identifier: str
    roles: set[AnyRole] = field(default_factory=set, compare=False)
    automate: bool = field(default=False, compare=False)
    hand: list[Card] = field(default_factory=list, compare=False)


class Group(list[Player]):
    """A list of players"""

    def update(self, person: Player) -> None:
        """
        Update the provided player within the group
        Will raise an error if the player is not in the group already
        """
        index = self.index(person)
        self[index] = person

    def upsert(self, person: Player) -> None:
        """
        Upsert the provided player into the group
        """
        if person in self:
            self.update(person)
        else:
            self.append(person)

    def by_identifier(self, identifier: str) -> Optional[Player]:
        """
        Find a player with the given identifier
        """
        return next(iter([p for p in self if p.identifier == identifier]), None)

    def by_role(self, role: AnyRole):
        """
        Find players with the given identifier
        """
        return type(self)([p for p in self if role in p.roles] or [])

    def find_or_use(self, example: Player) -> Player:
        """
        Find a player matching the example or return the example
        If the example has roles, any found player will append those roles
        """
        player = self.by_identifier(example.identifier) or example
        player.roles = player.roles.union(example.roles)
        return player

    def add_role(self, identifier: str, role: AnyRole) -> None:
        """
        Add the provided role to the player with the given identifier
        """
        player = self.by_identifier(identifier)
        if player:
            player.roles.add(role)

    def remove_role(self, identifier: str, role: AnyRole) -> None:
        """
        Remove the provided role from the person with the given identifier
        """
        player = self.by_identifier(identifier)
        if player:
            player.roles.discard(role)

    def swap_role(self, source_identifier: str, dest_identifier: str, role: AnyRole) -> None:
        """
        Swap a role from the source identifier to the destination identifier
        """
        self.remove_role(source_identifier, role)
        self.add_role(dest_identifier, role)

    def after(self, identifier: str) -> Player:
        """
        Determine the next player after the identified one
        """
        return self.__offset(identifier, 1)

    def __offset(self, identifier: str, offset: int) -> Player:
        """
        Determine the player sitting the provided distance away from the identified one
        """
        player = self.by_identifier(identifier)
        if not self or not player:
            raise HundredAndTenError(f"Unable to find player {offset} away from {identifier}.")
        return self[(self.index(player) + offset) % len(self)]
