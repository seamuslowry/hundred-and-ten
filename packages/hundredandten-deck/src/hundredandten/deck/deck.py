"""Card domain primitives for Hundred and Ten"""

from dataclasses import dataclass, field
from enum import Enum
from random import Random
from uuid import uuid4


class _Suit(Enum):
    """
    Base enum for card and selectable suits.
    Cross-enum equality (CardSuit.X == SelectableSuit.X) is intentional --
    it is load-bearing for trump comparison throughout the game engine.
    """

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Enum):
            return self.value == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)


class CardSuit(_Suit):
    """The valid card suits"""

    HEARTS = "HEARTS"
    CLUBS = "CLUBS"
    SPADES = "SPADES"
    DIAMONDS = "DIAMONDS"
    JOKER = "JOKER"


class SelectableSuit(_Suit):
    """The selectable card suits"""

    HEARTS = "HEARTS"
    CLUBS = "CLUBS"
    SPADES = "SPADES"
    DIAMONDS = "DIAMONDS"


class CardNumber(Enum):
    """The valid card values"""

    JOKER = "JOKER"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"
    EIGHT = "EIGHT"
    NINE = "NINE"
    TEN = "TEN"
    JACK = "JACK"
    QUEEN = "QUEEN"
    KING = "KING"
    ACE = "ACE"


@dataclass(frozen=True)
class CardInfo:
    """Game metadata about a card"""

    # value when this suit is trumps
    trump_value: int
    # value when this suit is "trumps" for a trick when no trumps are played
    weak_trump_value: int
    # true if the card is _always_ trumps
    always_trump: bool = False


card_info = {
    CardSuit.HEARTS: {
        CardNumber.TWO: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.THREE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.FOUR: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=3),
        CardNumber.SIX: CardInfo(trump_value=3, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=4, weak_trump_value=5),
        CardNumber.EIGHT: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.NINE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.TEN: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(
            trump_value=11, weak_trump_value=12, always_trump=True
        ),
    },
    CardSuit.DIAMONDS: {
        CardNumber.TWO: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.THREE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.FOUR: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=3),
        CardNumber.SIX: CardInfo(trump_value=3, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=4, weak_trump_value=5),
        CardNumber.EIGHT: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.NINE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.TEN: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12),
    },
    CardSuit.SPADES: {
        CardNumber.TWO: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.THREE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.FOUR: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=5),
        CardNumber.SIX: CardInfo(trump_value=4, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=3, weak_trump_value=3),
        CardNumber.EIGHT: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.NINE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.TEN: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12),
    },
    CardSuit.CLUBS: {
        CardNumber.TWO: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.THREE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.FOUR: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=5),
        CardNumber.SIX: CardInfo(trump_value=4, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=3, weak_trump_value=3),
        CardNumber.EIGHT: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.NINE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.TEN: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12),
    },
    CardSuit.JOKER: {
        CardNumber.JOKER: CardInfo(
            trump_value=12, weak_trump_value=12, always_trump=True
        )
    },
}


@dataclass(frozen=True)
class Card:
    """A playing card"""

    number: CardNumber
    suit: CardSuit

    def __repr__(self) -> str:
        return f"{self.number.name} of {self.suit.name}"

    @property
    def trump_value(self) -> int:
        """The value of this card as a trump"""
        return card_info[self.suit][self.number].trump_value

    @property
    def weak_trump_value(self) -> int:
        """The value of this card in a suit with no trumps where its suit leads"""
        return card_info[self.suit][self.number].weak_trump_value

    @property
    def always_trump(self) -> bool:
        """Whether the card is always considered trump"""
        return card_info[self.suit][self.number].always_trump


defined_cards = [
    Card(number, suit)
    for (suit, number_dict) in card_info.items()
    for number in number_dict
]


@dataclass
class Deck:
    """A seeded deck of cards"""

    seed: str = field(default_factory=lambda: str(uuid4()))
    pulled: int = 0
    cards: list[int] = field(init=False)

    def __post_init__(self):
        self.cards = [*range(len(defined_cards))]
        Random(self.seed).shuffle(self.cards)

    def draw(self, amount: int) -> list[Card]:
        """Draw the specified amount of cards from the deck"""
        start = self.pulled
        end = self.pulled + amount
        if amount < 0:
            raise ValueError("Cannot draw previously drawn cards.")
        if end > len(self.cards):
            raise ValueError("Deck is overdrawn.")

        self.pulled = end
        return [defined_cards[num] for num in self.cards[start:end]]
