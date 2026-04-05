"""A module providing naive decision making for hundred and ten games"""

from typing import Optional, Sequence

from hundredandten.engine.constants import (
    BidAmount,
    CardNumber,
    RoundStatus,
    SelectableSuit,
)
from hundredandten.engine.deck import Card
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.trumps import bleeds, trumps

from .state import (
    AvailableAction,
    AvailableBid,
    AvailableDiscard,
    AvailablePlay,
    AvailableSelectTrump,
    GameState,
)


def action(state: GameState) -> AvailableAction:
    """Return the suggested action given the game state"""
    if state.status == RoundStatus.BIDDING:
        return __suggested_bid(state)
    if state.status == RoundStatus.TRUMP_SELECTION:
        return __suggested_trump_selection(state)
    if state.status == RoundStatus.DISCARD:
        return __suggested_discard(state)
    if state.status == RoundStatus.TRICKS:
        return __suggested_play(state)
    raise HundredAndTenError(f"Cannot automate the action in status {state.status}")


def __suggested_bid(game_state: GameState) -> AvailableBid:
    """Return the suggested bid for the current player"""

    maximum_bid = max_bid(game_state.hand)
    available_bids = map(lambda b: b.amount, game_state.available_bids)
    willing_bids = list(filter(lambda b: b and b <= maximum_bid, available_bids))

    return AvailableBid(next(iter(willing_bids), BidAmount.PASS))


def __suggested_trump_selection(game_state: GameState) -> AvailableSelectTrump:
    """Return the suggested trump selection for the current player"""

    return AvailableSelectTrump(desired_trump(game_state.hand))


def __suggested_discard(game_state: GameState) -> AvailableDiscard:
    """Return the suggested dicard action for the current player"""

    return AvailableDiscard(
        list(non_trumps(game_state.hand, game_state.trump)),
    )


def __suggested_play(game_state: GameState) -> AvailablePlay:
    """Return the suggested play action for the current player"""

    playable_cards = game_state.hand
    if (
        len(game_state.tricks.current_trick_plays) > 0
        and game_state.trump
        and bleeds(game_state.current_trick_plays[0].card, game_state.trump)
    ):
        playable_cards = trumps(game_state.hand, game_state.trump) or playable_cards

    best_played_card = next(
        map(lambda p: p.card, game_state.tricks.current_trick_plays), None
    )

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

    return AvailablePlay(card)


def max_bid(cards: Sequence[Card]) -> BidAmount:
    """Return the maximum amount to bid with the given hand"""

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


def desired_trump(cards: Sequence[Card]) -> SelectableSuit:
    """Return the desired trump for the given hand"""

    return __most_valuable_suit(cards)[0]


def best_card(cards: Sequence[Card], trump: Optional[SelectableSuit]) -> Card:
    """Return the best trump card in the list of cards"""
    return max(trumps(cards, trump), key=lambda c: c.trump_value, default=cards[0])


def worst_card(cards: Sequence[Card], trump: Optional[SelectableSuit]) -> Card:
    """Return the worst card in the list of cards"""
    worst_non_trump = min(
        non_trumps(cards, trump), key=lambda c: c.weak_trump_value, default=None
    )
    worst_trump = min(
        trumps(cards, trump), key=lambda c: c.trump_value, default=cards[0]
    )

    return worst_non_trump or worst_trump


def worst_card_beating(
    cards: Sequence[Card], card_to_beat: Card, trump: Optional[SelectableSuit]
) -> Optional[Card]:
    """Return the worst card in the list of cards"""
    beating = __cards_beating(cards, card_to_beat, trump)

    return worst_card(beating, trump) if beating else None


def __cards_beating(
    cards: Sequence[Card], card_to_beat: Card, trump: Optional[SelectableSuit]
) -> Sequence[Card]:
    """Return all cards in the list that beat the provided card"""
    trump_cards = trumps(cards, trump)

    if not trumps([card_to_beat], trump):
        return [
            *trump_cards,
            *filter(
                lambda c: (
                    c.suit == card_to_beat.suit
                    and c.weak_trump_value > card_to_beat.weak_trump_value
                ),
                non_trumps(cards, trump),
            ),
        ]

    return list(filter(lambda c: c.trump_value > card_to_beat.trump_value, trump_cards))


def non_trumps(
    cards: Sequence[Card], trump: Optional[SelectableSuit]
) -> Sequence[Card]:
    """Return all non trump cards in the list"""
    return [card for card in cards if card.suit != trump and not card.always_trump]


def __bid_value(cards: Sequence[Card]) -> int:
    """Returns the bid value for a list of cards, assuming they are all trump"""
    discouragement = (
        -10 if CardNumber.FIVE not in list(map(lambda c: c.number, cards)) else 0
    )

    return sum(map(lambda card: card.trump_value, cards)) + discouragement


def __most_valuable_suit(cards: Sequence[Card]) -> tuple[SelectableSuit, int]:
    """Return a list of each suit with a numeric value of how much trump it has"""
    return max(__suits_by_value(cards).items(), key=lambda item: item[1])


def __suits_by_value(cards: Sequence[Card]) -> dict[SelectableSuit, int]:
    """Return a list of each suit with a numeric value of how much trump it has"""
    return {
        suit: __bid_value(grouped_cards)
        for suit, grouped_cards in __cards_by_suit(cards).items()
    }


def __cards_by_suit(cards: Sequence[Card]) -> dict[SelectableSuit, list[Card]]:
    """
    Return the list as a dictionary of cards sorted by suit
    if they would be trump for that suit.
    Cards that are always trump will appear in all lists
    """
    return {
        suit: [card for card in cards if card.suit == suit or card.always_trump]
        for suit in list(SelectableSuit)
    }
