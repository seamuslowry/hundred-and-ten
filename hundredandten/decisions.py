'''A module to make machine decisions about how to act in a game'''
from hundredandten.constants import BidAmount, CardNumber, SelectableSuit
from hundredandten.deck import Card


def max_bid(cards: list[Card]) -> BidAmount:
    '''Return the maximum amount to bid with the given hand'''

    best_value = __most_valuable_suit(cards)[1]

    if best_value > 50:
        return BidAmount.SHOOT_THE_MOON
    if best_value > 40:
        return BidAmount.THIRTY
    if best_value > 30:
        return BidAmount.TWENTY_FIVE
    if best_value > 25:
        return BidAmount.TWENTY
    if best_value > 20:
        return BidAmount.FIFTEEN

    return BidAmount.PASS


def desired_trump(cards: list[Card]) -> SelectableSuit:
    '''Return the desired trump for the given hand'''

    return __most_valuable_suit(cards)[0]


def __bid_value(cards: list[Card]) -> int:
    '''Returns the bid value for a list of cards, assuming they are all trump'''
    discouragement = -10 if CardNumber.FIVE not in list(map(lambda c: c.number, cards)) else 0

    return sum(map(lambda card: card.trump_value, cards)) + discouragement


def __most_valuable_suit(cards: list[Card]) -> tuple[SelectableSuit, int]:
    '''Return a list of each suit with a numeric value of how much trump it has'''
    return max(__suits_by_value(cards).items(), key=lambda item: item[1])


def __suits_by_value(cards: list[Card]) -> dict[SelectableSuit, int]:
    '''Return a list of each suit with a numeric value of how much trump it has'''
    return {suit: __bid_value(grouped_cards)
            for suit, grouped_cards in __cards_by_suit(cards).items()}


def __cards_by_suit(cards: list[Card]) -> dict[SelectableSuit, list[Card]]:
    '''
    Return the list as a dictionary of cards sorted by suit
    if they would be trump for that suit.
    Cards that are always trump will appear in all lists
    '''
    return {suit: [card for card in cards if card.suit == suit or card.always_trump]
            for suit in list(SelectableSuit)}
