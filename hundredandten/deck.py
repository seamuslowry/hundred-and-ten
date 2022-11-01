'''Handle the functions of a deck'''
from dataclasses import dataclass, field
from random import Random
from uuid import uuid4

from hundredandten.constants import (CardNumber, CardSuit, SelectableSuit,
                                     UnselectableSuit)
from hundredandten.hundred_and_ten_error import HundredAndTenError


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

    def draw(self, amount: int) -> list[Card]:
        '''Draw the specified amount of cards from the deck'''
        deck_size = len(cards)

        start = self.pulled
        end = self.pulled + amount
        if amount < 0:
            raise HundredAndTenError("Cannot draw previously drawn cards.")
        if end > deck_size:
            raise HundredAndTenError("Deck is overdrawn.")

        card_arr = [*range(deck_size)]
        Random(self.seed).shuffle(card_arr)

        self.pulled = end
        return list(map(lambda num: cards[num], card_arr[start:end]))
