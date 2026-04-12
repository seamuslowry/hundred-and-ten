"""A module providing naive decision making for hundred and ten games"""

from collections.abc import Sequence

from hundredandten.deck import Card, CardNumber, SelectableSuit, bleeds, trumps
from hundredandten.state import (
    AvailableAction,
    AvailableBid,
    AvailableDiscard,
    AvailablePlay,
    AvailableSelectTrump,
    BidAmount,
    GameState,
    StateError,
    Status,
)


def action_for(state: GameState) -> AvailableAction:
    """Return the suggested action given the game state"""
    if state.status == Status.BIDDING:
        return __suggested_bid(state)
    if state.status == Status.TRUMP_SELECTION:
        return __suggested_trump_selection(state)
    if state.status == Status.DISCARD:
        return __suggested_discard(state)
    if state.status == Status.TRICKS:
        return __suggested_play(state)
    raise StateError(f"Cannot automate the action in status {state.status}")


def __suggested_bid(game_state: GameState) -> AvailableBid:
    """Return the suggested bid for the current player"""

    maximum_bid = max_bid(game_state.hand)
    available_bids = [b.amount for b in game_state.available_bids]
    willing_bids = [b for b in available_bids if b and b <= maximum_bid]

    return AvailableBid(next(iter(willing_bids), 0))


def __suggested_trump_selection(game_state: GameState) -> AvailableSelectTrump:
    """Return the suggested trump selection for the current player"""

    return AvailableSelectTrump(desired_trump(game_state.hand))


def __suggested_discard(game_state: GameState) -> AvailableDiscard:
    """Return the suggested dicard action for the current player"""

    return AvailableDiscard(
        tuple(__non_trumps(game_state.hand, game_state.bidding.trump)),
    )


def __suggested_play(game_state: GameState) -> AvailablePlay:
    """Return the suggested play action for the current player"""

    playable_cards = game_state.hand
    if (
        len(game_state.tricks.current_trick_plays) > 0
        and game_state.bidding.trump
        and bleeds(
            game_state.tricks.current_trick_plays[0].card, game_state.bidding.trump
        )
    ):
        playable_cards = (
            trumps(game_state.hand, game_state.bidding.trump) or playable_cards
        )

    # Find the current winning card (not just the lead card)
    best_played_card = None
    if game_state.tricks.current_trick_plays:
        best_played_card = game_state.tricks.current_trick_plays[0].card
        for play in game_state.tricks.current_trick_plays[1:]:
            # Check if this card beats the current best
            if __cards_beating([play.card], best_played_card, game_state.bidding.trump):
                best_played_card = play.card

    if not best_played_card:
        # if you are the bidder and you can bleed, do so
        if game_state.is_bidder:
            card = best_card(playable_cards, game_state.bidding.trump)
        # otherwise, don't bleed if you can help it
        else:
            card = worst_card(playable_cards, game_state.bidding.trump)
    else:
        worst_winning_card = worst_card_beating(
            playable_cards, best_played_card, game_state.bidding.trump
        )
        # if you can beat the current winning card, do it with the lowest card that will do it
        # otherwise, play nothing
        card = worst_winning_card or worst_card(
            playable_cards, game_state.bidding.trump
        )

    return AvailablePlay(card)


def max_bid(cards: Sequence[Card]) -> BidAmount:
    """Return the maximum amount to bid with the given hand"""

    best_value = __most_valuable_suit(cards)[1]

    if best_value > 50:
        return 60
    if best_value > 40:
        return 30
    if best_value > 30:
        return 25
    if best_value > 25:
        return 20
    if best_value > 20:
        return 15

    return 0


def desired_trump(cards: Sequence[Card]) -> SelectableSuit:
    """Return the desired trump for the given hand"""

    return __most_valuable_suit(cards)[0]


def best_card(cards: Sequence[Card], trump: SelectableSuit | None) -> Card:
    """Return the best trump card in the list of cards"""
    trump_cards = trumps(cards, trump)
    return max(trump_cards, key=lambda c: c.trump_value) if trump_cards else cards[0]


def worst_card(cards: Sequence[Card], trump: SelectableSuit | None) -> Card:
    """Return the worst card in the list of cards"""
    non_trumps = __non_trumps(cards, trump)
    worst_non_trump = (
        min(non_trumps, key=lambda c: c.weak_trump_value) if non_trumps else None
    )

    trump_cards = trumps(cards, trump)
    worst_trump = (
        min(trump_cards, key=lambda c: c.trump_value) if trump_cards else cards[0]
    )

    return worst_non_trump or worst_trump


def worst_card_beating(
    cards: Sequence[Card], card_to_beat: Card, trump: SelectableSuit | None
) -> Card | None:
    """Return the worst card in the list that beats card_to_beat, or None"""
    beating = __cards_beating(cards, card_to_beat, trump)

    return worst_card(beating, trump) if beating else None


def __cards_beating(
    cards: Sequence[Card], card_to_beat: Card, trump: SelectableSuit | None
) -> Sequence[Card]:
    """Return all cards in the list that beat the provided card"""
    trump_cards = trumps(cards, trump)

    if not trumps([card_to_beat], trump):
        non_trump_beaters = [
            c
            for c in __non_trumps(cards, trump)
            if c.suit == card_to_beat.suit
            and c.weak_trump_value > card_to_beat.weak_trump_value
        ]
        return [*trump_cards, *non_trump_beaters]

    return [c for c in trump_cards if c.trump_value > card_to_beat.trump_value]


def __non_trumps(cards: Sequence[Card], trump: SelectableSuit | None) -> Sequence[Card]:
    """Return all non trump cards in the list"""
    return [card for card in cards if card.suit != trump and not card.always_trump]


def __bid_value(cards: Sequence[Card]) -> int:
    """Returns the bid value for a list of cards, assuming they are all trump"""
    card_numbers = [c.number for c in cards]
    discouragement = -10 if CardNumber.FIVE not in card_numbers else 0

    return sum(card.trump_value for card in cards) + discouragement


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
