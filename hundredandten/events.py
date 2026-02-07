"""The events that can occur during the game"""

from dataclasses import dataclass

from hundredandten.deck import Card


@dataclass
class Score:
    """A class to keep track of a player's score in either a trick or a game"""

    identifier: str
    value: int


@dataclass
class Event:
    """A superclass for events in the game"""


@dataclass
class GameStart(Event):
    """A class to represent the start of game event"""


@dataclass
class RoundStart(Event):
    """A class to represent the start of round event"""

    dealer: str
    hands: dict[str, list[Card]]


@dataclass
class TrickStart(Event):
    """A class to represent the start of trick event"""


@dataclass
class RoundEnd(Event):
    """A class to represent the end of round event"""

    scores: list[Score]


@dataclass
class TrickEnd(Event):
    """A class to represent the end of trick event"""

    winner: str


@dataclass
class GameEnd(Event):
    """A class to represent the end of game event"""

    winner: str
