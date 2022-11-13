'''Handle the functions of a deck'''
from dataclasses import dataclass, field
from random import Random
from uuid import uuid4

from hundredandten.constants import (CardNumber, CardSuit, SelectableSuit,
                                     UnselectableSuit)
from hundredandten.hundred_and_ten_error import HundredAndTenError


@dataclass
class CardInfo:
    '''Game metadata about a card'''
    # value when this suit is trumps
    trump_value: int
    # value when this suit is "trumps" for a trick when no trumps are played
    weak_trump_value: int
    # true if the card is _always_ trumps
    always_trump: bool = False


card_info = {
    SelectableSuit.HEARTS: {
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
        CardNumber.ACE: CardInfo(trump_value=11, weak_trump_value=12, always_trump=True)
    },
    SelectableSuit.DIAMONDS: {
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
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12)
    },
    SelectableSuit.SPADES: {
        CardNumber.TWO: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.THREE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.FOUR: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=5),
        CardNumber.SIX: CardInfo(trump_value=4, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=3, weak_trump_value=3),
        CardNumber.EIGHT: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.NINE: CardInfo(trump_value=2, weak_trump_value=1),
        CardNumber.TEN: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12)
    },
    SelectableSuit.CLUBS: {
        CardNumber.TWO: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.THREE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.FOUR: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=5),
        CardNumber.SIX: CardInfo(trump_value=4, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=3, weak_trump_value=3),
        CardNumber.EIGHT: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.NINE: CardInfo(trump_value=2, weak_trump_value=1),
        CardNumber.TEN: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12)
    },
    UnselectableSuit.JOKER: {
        CardNumber.JOKER: CardInfo(trump_value=12, weak_trump_value=12, always_trump=True)
    }
}


@dataclass
class Card:
    '''A playing card'''
    number: CardNumber
    suit: CardSuit
    # value when this suit is trumps
    trump_value: int
    # value when this suit is "trumps" for a trick when no trumps are played
    weak_trump_value: int
    # true if the card is _always_ trumps
    always_trump: bool = False

    def __repr__(self):
        return f'{self.number.name} of {self.suit.name}'


cards = [
    # Hearts
    Card(CardNumber.TWO, SelectableSuit.HEARTS, 0, 0),
    Card(CardNumber.THREE, SelectableSuit.HEARTS, 1, 1),
    Card(CardNumber.FOUR, SelectableSuit.HEARTS, 2, 2),
    Card(CardNumber.FIVE, SelectableSuit.HEARTS, 14, 3),
    Card(CardNumber.SIX, SelectableSuit.HEARTS, 3, 4),
    Card(CardNumber.SEVEN, SelectableSuit.HEARTS, 4, 5),
    Card(CardNumber.EIGHT, SelectableSuit.HEARTS, 5, 6),
    Card(CardNumber.NINE, SelectableSuit.HEARTS, 6, 7),
    Card(CardNumber.TEN, SelectableSuit.HEARTS, 7, 8),
    Card(CardNumber.JACK, SelectableSuit.HEARTS, 13, 9),
    Card(CardNumber.QUEEN, SelectableSuit.HEARTS, 8, 10),
    Card(CardNumber.KING, SelectableSuit.HEARTS, 9, 11),
    Card(CardNumber.ACE, SelectableSuit.HEARTS, 11, 12, True),
    # Diamonds
    Card(CardNumber.TWO, SelectableSuit.DIAMONDS, 0, 0),
    Card(CardNumber.THREE, SelectableSuit.DIAMONDS, 1, 1),
    Card(CardNumber.FOUR, SelectableSuit.DIAMONDS, 2, 2),
    Card(CardNumber.FIVE, SelectableSuit.DIAMONDS, 14, 3),
    Card(CardNumber.SIX, SelectableSuit.DIAMONDS, 3, 4),
    Card(CardNumber.SEVEN, SelectableSuit.DIAMONDS, 4, 5),
    Card(CardNumber.EIGHT, SelectableSuit.DIAMONDS, 5, 6),
    Card(CardNumber.NINE, SelectableSuit.DIAMONDS, 6, 7),
    Card(CardNumber.TEN, SelectableSuit.DIAMONDS, 7, 8),
    Card(CardNumber.JACK, SelectableSuit.DIAMONDS, 13, 9),
    Card(CardNumber.QUEEN, SelectableSuit.DIAMONDS, 8, 10),
    Card(CardNumber.KING, SelectableSuit.DIAMONDS, 9, 11),
    Card(CardNumber.ACE, SelectableSuit.DIAMONDS, 10, 12),
    # Spades
    Card(CardNumber.TWO, SelectableSuit.SPADES, 7, 8),
    Card(CardNumber.THREE, SelectableSuit.SPADES, 6, 7),
    Card(CardNumber.FOUR, SelectableSuit.SPADES, 5, 6),
    Card(CardNumber.FIVE, SelectableSuit.SPADES, 14, 5),
    Card(CardNumber.SIX, SelectableSuit.SPADES, 4, 4),
    Card(CardNumber.SEVEN, SelectableSuit.SPADES, 3, 3),
    Card(CardNumber.EIGHT, SelectableSuit.SPADES, 2, 2),
    Card(CardNumber.NINE, SelectableSuit.SPADES, 1, 1),
    Card(CardNumber.TEN, SelectableSuit.SPADES, 0, 0),
    Card(CardNumber.JACK, SelectableSuit.SPADES, 13, 9),
    Card(CardNumber.QUEEN, SelectableSuit.SPADES, 8, 10),
    Card(CardNumber.KING, SelectableSuit.SPADES, 9, 11),
    Card(CardNumber.ACE, SelectableSuit.SPADES, 10, 12),
    # Clubs
    Card(CardNumber.TWO, SelectableSuit.CLUBS, 7, 8),
    Card(CardNumber.THREE, SelectableSuit.CLUBS, 6, 7),
    Card(CardNumber.FOUR, SelectableSuit.CLUBS, 5, 6),
    Card(CardNumber.FIVE, SelectableSuit.CLUBS, 14, 5),
    Card(CardNumber.SIX, SelectableSuit.CLUBS, 4, 4),
    Card(CardNumber.SEVEN, SelectableSuit.CLUBS, 3, 3),
    Card(CardNumber.EIGHT, SelectableSuit.CLUBS, 2, 2),
    Card(CardNumber.NINE, SelectableSuit.CLUBS, 1, 1),
    Card(CardNumber.TEN, SelectableSuit.CLUBS, 0, 0),
    Card(CardNumber.JACK, SelectableSuit.CLUBS, 13, 9),
    Card(CardNumber.QUEEN, SelectableSuit.CLUBS, 8, 10),
    Card(CardNumber.KING, SelectableSuit.CLUBS, 9, 11),
    Card(CardNumber.ACE, SelectableSuit.CLUBS, 10, 12),
    # Joker
    Card(CardNumber.JOKER, UnselectableSuit.JOKER, 12, 12, True)
]


@dataclass
class Deck:
    '''A seeded deck of cards'''
    seed: str = field(default_factory=lambda: str(uuid4()))
    pulled: int = 0
    cards: list[int] = field(init=False)

    def __post_init__(self):
        self.cards = [*range(len(cards))]
        Random(self.seed).shuffle(self.cards)

    def draw(self, amount: int) -> list[Card]:
        '''Draw the specified amount of cards from the deck'''
        start = self.pulled
        end = self.pulled + amount
        if amount < 0:
            raise HundredAndTenError("Cannot draw previously drawn cards.")
        if end > len(self.cards):
            raise HundredAndTenError("Deck is overdrawn.")

        self.pulled = end
        return list(map(lambda num: cards[num], self.cards[start:end]))
