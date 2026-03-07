"""Interact with a list of people"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from hundredandten.constants import RoundRole
from hundredandten.deck import Card
from hundredandten.hundred_and_ten_error import HundredAndTenError


@dataclass
class Player(ABC):
    """A class to represent a player at the game level"""

    identifier: str

    @abstractmethod
    def automate(self) -> bool:
        """Return true if this player is automated, false otherwise"""
        # TODO: should eventually be act and return the action given a game state


@dataclass
class HumanPlayer(Player):
    """Represent a human player. Actions must be taken independently."""

    def automate(self) -> bool:
        return False


@dataclass
class NaiveAutomatedPlayer(Player):
    """Represent an automated player. Actions will be taken autonomously."""

    def automate(self) -> bool:
        return True


@dataclass
class RoundPlayer:
    """A class to keep track of player information within a round"""

    identifier: str
    roles: set[RoundRole] = field(default_factory=set, compare=False)
    hand: list[Card] = field(default_factory=list, compare=False)


def player_after(players: list[RoundPlayer], identifier: str) -> RoundPlayer:
    """
    Determine the player sitting after the identified one.
    """
    player = player_by_identifier(players, identifier)

    return players[(players.index(player) + 1) % len(players)]


def player_by_identifier(players: list[RoundPlayer], identifier: str) -> RoundPlayer:
    """Find a player with the given identifier."""
    p = next((p for p in players if p.identifier == identifier), None)

    if not p:
        raise HundredAndTenError(f"Unrecognized player ${p}")

    return p


def players_by_role(players: list[RoundPlayer], role: RoundRole) -> list[RoundPlayer]:
    """Find all players carrying the given role."""
    return [p for p in players if role in p.roles]


def add_player_role(
    players: list[RoundPlayer], identifier: str, role: RoundRole
) -> None:
    """Add the provided role to the player with the given identifier."""
    player_by_identifier(players, identifier).roles.add(role)


def remove_player_role(
    players: list[RoundPlayer], identifier: str, role: RoundRole
) -> None:
    """Remove the provided role from the player with the given identifier."""
    player_by_identifier(players, identifier).roles.discard(role)


def relative_distance(players: list[RoundPlayer], self: str, other: str) -> int:
    """Return the relative distance of the other player to the first player"""
    self_player = player_by_identifier(players, self)
    other_player = player_by_identifier(players, other)

    return (players.index(other_player) - players.index(self_player)) % len(players)
