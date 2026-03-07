"""Interact with a list of people"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from hundredandten.actions import Action, Bid, Discard, Play, SelectTrump
from hundredandten.constants import BidAmount, RoundRole, RoundStatus
from hundredandten.decisions import (
    best_card,
    desired_trump,
    max_bid,
    non_trumps,
    trumps,
    worst_card,
    worst_card_beating,
)
from hundredandten.deck import Card
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.state import GameState


@dataclass
class Player(ABC):
    """A class to represent a player at the game level"""

    identifier: str

    @abstractmethod
    def act(self, game_state: GameState) -> Optional[Action]:
        """Return the action this player should take, or None if no action"""


@dataclass
class HumanPlayer(Player):
    """Represent a human player. Actions must be taken independently."""

    def act(self, _: GameState) -> None:
        return None


@dataclass
class NaiveAutomatedPlayer(Player):
    """Represent an automated player. Actions will be taken autonomously."""

    def act(self, game_state: GameState) -> Action:
        """Return the suggested action given the game state"""
        if game_state.status == RoundStatus.BIDDING:
            return self.__suggested_bid(game_state)
        if game_state.status == RoundStatus.TRUMP_SELECTION:
            return self.__suggested_trump_selection(game_state)
        if game_state.status == RoundStatus.DISCARD:
            return self.__suggested_discard(game_state)
        if game_state.status == RoundStatus.TRICKS:
            return self.__suggested_play(game_state)
        raise HundredAndTenError(
            f"Cannot automate the action in status {game_state.status}"
        )

    def __suggested_bid(self, game_state: GameState) -> Bid:
        """Return the suggested bid for the current player"""

        maximum_bid = max_bid(game_state.hand)
        available_bids = map(lambda b: b.amount, game_state.available_bids)
        willing_bids = list(filter(lambda b: b and b <= maximum_bid, available_bids))

        return Bid(self.identifier, next(iter(willing_bids), BidAmount.PASS))

    def __suggested_trump_selection(self, game_state: GameState) -> SelectTrump:
        """Return the suggested trump selection for the current player"""

        return SelectTrump(self.identifier, desired_trump(game_state.hand))

    def __suggested_discard(self, game_state: GameState) -> Discard:
        """Return the suggested dicard action for the current player"""

        return Discard(
            self.identifier,
            list(non_trumps(game_state.hand, game_state.trump)),
        )

    def __suggested_play(self, game_state: GameState) -> Play:
        """Return the suggested play action for the current player"""

        playable_cards = game_state.hand
        if game_state.tricks.bleeding:
            playable_cards = trumps(game_state.hand, game_state.trump) or playable_cards

        best_played_card = next(
            map(lambda p: p.card, game_state.tricks.current_trick_plays), None
        )  # self.active_trick.winning_play

        if not best_played_card:
            # if you are the bidder and you can bleed, do so
            if game_state.is_bidder:
                card = best_card(playable_cards, game_state.trump)
            # otherwise, don't bleed if you can help it
            else:
                card = worst_card(playable_cards, game_state.trump)
        else:
            worst_winning_card = worst_card_beating(
                playable_cards, best_played_card, game_state.trump
            )
            # if you can beat the current winning card, do it with the lowest card that will do it
            # otherwise, play nothing
            card = worst_winning_card or worst_card(playable_cards, game_state.trump)

        return Play(self.identifier, card)


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
