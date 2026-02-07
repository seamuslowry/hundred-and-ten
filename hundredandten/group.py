"""Interact with a list of people"""

from dataclasses import dataclass, field
from typing import Generic, Optional, TypeVar

from hundredandten.constants import RoundRole
from hundredandten.deck import Card
from hundredandten.hundred_and_ten_error import HundredAndTenError


@dataclass
class Player:
    """A class to keep track of player information at the game level"""

    identifier: str
    automate: bool = field(default=False, compare=False)


@dataclass
class RoundPlayer(Player):
    """A class to keep track of player information within a round"""

    roles: set[RoundRole] = field(default_factory=set, compare=False)
    hand: list[Card] = field(default_factory=list, compare=False)


P = TypeVar("P", bound=Player)


class Group(list[P], Generic[P]):
    """A list of players"""

    def update(self, person: P) -> None:
        """
        Update the provided player within the group.
        Will raise an error if the player is not in the group already.
        """
        index = self.index(person)
        self[index] = person

    def upsert(self, person: P) -> None:
        """Upsert the provided player into the group."""
        if person in self:
            self.update(person)
        else:
            self.append(person)

    def by_identifier(self, identifier: str) -> Optional[P]:
        """Find a player with the given identifier."""
        return next((p for p in self if p.identifier == identifier), None)

    def after(self, identifier: str) -> P:
        """Determine the next player after the identified one."""
        return self._offset(identifier, 1)

    def _offset(self, identifier: str, offset: int) -> P:
        """
        Determine the player sitting the provided distance away
        from the identified one.
        """
        player = self.by_identifier(identifier)
        if not self or not player:
            raise HundredAndTenError(
                f"Unable to find player {offset} away from {identifier}."
            )
        return self[(self.index(player) + offset) % len(self)]


class RoundGroup(Group[RoundPlayer]):
    """A group of round players, with role-based operations."""

    def by_role(self, role: RoundRole) -> "RoundGroup":
        """Find all players carrying the given role."""
        return RoundGroup(p for p in self if role in p.roles)

    def find_or_use(self, example: RoundPlayer) -> RoundPlayer:
        """
        Find a player matching the example or return the example.
        If the example has roles, any found player will have those roles merged in.
        """
        player = self.by_identifier(example.identifier) or example
        player.roles = player.roles.union(example.roles)
        return player

    def add_role(self, identifier: str, role: RoundRole) -> None:
        """Add the provided role to the player with the given identifier."""
        player = self.by_identifier(identifier)
        if player:
            player.roles.add(role)

    def remove_role(self, identifier: str, role: RoundRole) -> None:
        """Remove the provided role from the player with the given identifier."""
        player = self.by_identifier(identifier)
        if player:
            player.roles.discard(role)

    def swap_role(
        self, source_identifier: str, dest_identifier: str, role: RoundRole
    ) -> None:
        """Swap a role from the source identifier to the destination identifier."""
        self.remove_role(source_identifier, role)
        self.add_role(dest_identifier, role)
