'''Handle the functions of a deck'''
from dataclasses import dataclass
from random import Random
from typing import Optional
from uuid import uuid4

from hundredandten.constants import CardNumber, CardSuit
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
    Card(CardNumber.TWO, CardSuit.HEARTS, 0, 0),
    Card(CardNumber.THREE, CardSuit.HEARTS, 1, 1),
    Card(CardNumber.FOUR, CardSuit.HEARTS, 2, 2),
    Card(CardNumber.FIVE, CardSuit.HEARTS, 14, 3),
    Card(CardNumber.SIX, CardSuit.HEARTS, 3, 4),
    Card(CardNumber.SEVEN, CardSuit.HEARTS, 4, 5),
    Card(CardNumber.EIGHT, CardSuit.HEARTS, 5, 6),
    Card(CardNumber.NINE, CardSuit.HEARTS, 6, 7),
    Card(CardNumber.TEN, CardSuit.HEARTS, 7, 8),
    Card(CardNumber.JACK, CardSuit.HEARTS, 13, 9),
    Card(CardNumber.QUEEN, CardSuit.HEARTS, 8, 10),
    Card(CardNumber.KING, CardSuit.HEARTS, 9, 11),
    Card(CardNumber.ACE, CardSuit.HEARTS, 11, 12, True),
    # Diamonds
    Card(CardNumber.TWO, CardSuit.DIAMONDS, 0, 0),
    Card(CardNumber.THREE, CardSuit.DIAMONDS, 1, 1),
    Card(CardNumber.FOUR, CardSuit.DIAMONDS, 2, 2),
    Card(CardNumber.FIVE, CardSuit.DIAMONDS, 14, 3),
    Card(CardNumber.SIX, CardSuit.DIAMONDS, 3, 4),
    Card(CardNumber.SEVEN, CardSuit.DIAMONDS, 4, 5),
    Card(CardNumber.EIGHT, CardSuit.DIAMONDS, 5, 6),
    Card(CardNumber.NINE, CardSuit.DIAMONDS, 6, 7),
    Card(CardNumber.TEN, CardSuit.DIAMONDS, 7, 8),
    Card(CardNumber.JACK, CardSuit.DIAMONDS, 13, 9),
    Card(CardNumber.QUEEN, CardSuit.DIAMONDS, 8, 10),
    Card(CardNumber.KING, CardSuit.DIAMONDS, 9, 11),
    Card(CardNumber.ACE, CardSuit.DIAMONDS, 10, 12),
    # Spades
    Card(CardNumber.TWO, CardSuit.SPADES, 7, 8),
    Card(CardNumber.THREE, CardSuit.SPADES, 6, 7),
    Card(CardNumber.FOUR, CardSuit.SPADES, 5, 6),
    Card(CardNumber.FIVE, CardSuit.SPADES, 14, 5),
    Card(CardNumber.SIX, CardSuit.SPADES, 4, 4),
    Card(CardNumber.SEVEN, CardSuit.SPADES, 3, 3),
    Card(CardNumber.EIGHT, CardSuit.SPADES, 2, 2),
    Card(CardNumber.NINE, CardSuit.SPADES, 1, 1),
    Card(CardNumber.TEN, CardSuit.SPADES, 0, 0),
    Card(CardNumber.JACK, CardSuit.SPADES, 13, 9),
    Card(CardNumber.QUEEN, CardSuit.SPADES, 8, 10),
    Card(CardNumber.KING, CardSuit.SPADES, 9, 11),
    Card(CardNumber.ACE, CardSuit.SPADES, 10, 12),
    # Clubs
    Card(CardNumber.TWO, CardSuit.CLUBS, 7, 8),
    Card(CardNumber.THREE, CardSuit.CLUBS, 6, 7),
    Card(CardNumber.FOUR, CardSuit.CLUBS, 5, 6),
    Card(CardNumber.FIVE, CardSuit.CLUBS, 14, 5),
    Card(CardNumber.SIX, CardSuit.CLUBS, 4, 4),
    Card(CardNumber.SEVEN, CardSuit.CLUBS, 3, 3),
    Card(CardNumber.EIGHT, CardSuit.CLUBS, 2, 2),
    Card(CardNumber.NINE, CardSuit.CLUBS, 1, 1),
    Card(CardNumber.TEN, CardSuit.CLUBS, 0, 0),
    Card(CardNumber.JACK, CardSuit.CLUBS, 13, 9),
    Card(CardNumber.QUEEN, CardSuit.CLUBS, 8, 10),
    Card(CardNumber.KING, CardSuit.CLUBS, 9, 11),
    Card(CardNumber.ACE, CardSuit.CLUBS, 10, 12),
    # Joker
    Card(CardNumber.JOKER, CardSuit.JOKER, 12, 12, True)
]


class Deck:
    '''A seeded deck of cards'''

    def __init__(self, seed: Optional[str] = None, pulled: int = 0):
        self.seed = seed or str(uuid4())
        self.pulled = pulled
        self.cards = [*range(53)]
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
