"""Represent one round of a game of Hundred and Ten"""

from dataclasses import InitVar, dataclass, field
from functools import cached_property
from itertools import chain
from typing import Optional

from hundredandten.actions import (
    Action,
    Bid,
    DetailedDiscard,
    Discard,
    Play,
    SelectTrump,
)
from hundredandten.constants import (
    HAND_SIZE,
    TRICK_VALUE,
    BidAmount,
    RoundRole,
    RoundStatus,
    SelectableSuit,
)
from hundredandten.decisions import (
    trumps,
)
from hundredandten.deck import Deck
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.player import (
    Player,
    RoundPlayer,
    add_player_role,
    player_after,
    player_by_identifier,
    players_by_role,
)
from hundredandten.trick import Score, Trick


@dataclass
class Round:
    """A round in the game of Hundred and Ten"""

    game_players: InitVar[list[Player]]
    dealer_identifier: InitVar[str]
    seed: InitVar[str]

    players: list[RoundPlayer] = field(init=False)
    _deck: Deck = field(init=False, repr=False)
    _bids: list[Bid] = field(default_factory=list, init=False, repr=False)
    _select_trump: Optional[SelectTrump] = field(default=None, init=False, repr=False)
    _discards: list[DetailedDiscard] = field(
        default_factory=list, init=False, repr=False
    )
    _tricks: list[Trick] = field(default_factory=list, init=False, repr=False)

    def __post_init__(
        self, player_info: list[Player], dealer_identifier: str, seed: str
    ) -> None:
        # Create deck from seed
        self._deck = Deck(seed=seed)

        # Create players RoundGroup by dealing hands from deck
        self.players = [
            RoundPlayer(p.identifier, hand=self._deck.draw(HAND_SIZE))
            for p in player_info
        ]

        # Add DEALER role to dealer
        add_player_role(self.players, dealer_identifier, RoundRole.DEALER)

    @property
    def bids(self) -> list[Bid]:
        """All bids placed in this round."""
        return self._bids

    @property
    def selection(self) -> Optional[SelectTrump]:
        """The trump selection, if any."""
        return self._select_trump

    @property
    def discards(self) -> list[DetailedDiscard]:
        """All discards in this round."""
        return self._discards

    @property
    def tricks(self) -> list[Trick]:
        """All tricks in this round."""
        return self._tricks

    @property
    def deck(self) -> Deck:
        """The deck for this round."""
        return self._deck

    @property
    def dealer(self) -> RoundPlayer:
        """The dealer this round."""
        dlr = next(iter(players_by_role(self.players, RoundRole.DEALER)), None)
        if not dlr:
            raise HundredAndTenError("No dealer found.")
        return dlr

    @cached_property
    def active_player(self) -> RoundPlayer:
        """The current active player."""
        # while bidding, the active player is the one after the last bidder that can place a bid
        if self.status == RoundStatus.BIDDING:
            # before anyone has bid, treat the dealer as the last bidder
            last_bidder = (
                self.dealer.identifier if not self.bids else self.bids[-1].identifier
            )
            active_and_last_bidders = [
                p
                for p in self.players
                if p in self.bidders or p.identifier == last_bidder
            ]

            return player_after(active_and_last_bidders, last_bidder)
        # when in trump selection, the active bidder is the active player
        if self.status == RoundStatus.TRUMP_SELECTION:
            assert self.active_bidder
            return self.active_bidder
        if self.status == RoundStatus.DISCARD:
            assert self.active_bidder
            last_discarder = (
                self.dealer.identifier
                if not self.discards
                else self.discards[-1].identifier
            )
            return player_after(self.players, last_discarder)
        # while playing tricks, active player needs to consider
        # trick number, trick status, and winner of last trick
        if self.status == RoundStatus.TRICKS:
            assert self.active_bidder
            # when we're starting a new trick
            if not self.active_trick.plays:
                # the player after the bidder goes first on the first trick
                if len(self.tricks) == 1:
                    return player_after(self.players, self.active_bidder.identifier)
                # otherwise, its the winner of the last trick
                winning_play = self.tricks[-2].winning_play
                # when we have more than one trick, any previous trick will have a winning play
                assert winning_play
                winner = player_by_identifier(self.players, winning_play.identifier)
                # when the trick has a winning play, there will be a valid player associated to it
                assert winner
                return winner
            # in an ongoing trick, active player is next around the table
            return player_after(self.players, self.active_trick.plays[-1].identifier)
        raise HundredAndTenError(
            f"Cannot determine active player in {self.status} status"
        )

    @cached_property
    def inactive_players(self) -> list[RoundPlayer]:
        """The players that are not active."""
        return [p for p in self.players if p != self.active_player]

    @cached_property
    def active_bid(self) -> Optional[BidAmount]:
        """The maximum bid submitted this round"""
        return max(self.bids).amount if self.bids else None

    @cached_property
    def bidders(self) -> list[RoundPlayer]:
        """Anyone in this round that can still submit a bid."""
        return [
            p
            for p in self.players
            if self.__current_bid(p.identifier) != Bid("", BidAmount.PASS)
        ]

    @cached_property
    def active_bidder(self) -> Optional[RoundPlayer]:
        """The active bidder this round."""

        if not self.active_bid or len(self.bidders) != 1:
            return None
        return self.bidders[0]

    @property
    def active_trick(self) -> Trick:
        """The current active trick"""
        if not self.tricks:
            raise HundredAndTenError("No active trick found.")
        return self.tricks[-1]

    @cached_property
    def trump(self) -> Optional[SelectableSuit]:
        """The selected trump"""
        if not self.selection:
            return None
        return self.selection.suit

    @property
    def completed(self) -> bool:
        """True if the round is complete, False otherwise"""
        return self.status in [RoundStatus.COMPLETED, RoundStatus.COMPLETED_NO_BIDDERS]

    @cached_property
    def status(self) -> RoundStatus:
        """The status property."""
        if self.tricks and all(not player.hand for player in self.players):
            return RoundStatus.COMPLETED
        if len(self.discards) == len(self.players):
            return RoundStatus.TRICKS
        if self.selection:
            return RoundStatus.DISCARD
        if self.active_bidder:
            return RoundStatus.TRUMP_SELECTION
        if not self.bidders:
            return RoundStatus.COMPLETED_NO_BIDDERS
        return RoundStatus.BIDDING

    @cached_property
    def actions(self) -> list[Action]:
        """The actions that occurred in the round."""
        return [
            *self._bids,
            *([self._select_trump] if self._select_trump else []),
            *self._discards,
            *chain.from_iterable(trick.plays for trick in self.tricks),
        ]

    @cached_property
    def scores(self) -> list[Score]:
        """
        The scores each player earned for this round
        A list of tuples in the form
        left: player identifier
        value: score for the trick

        The list will come in the order the points were earned.
        This is to determine a disputed winner
        """
        winning_plays = [
            winning_play
            for winning_play in map(lambda trick: trick.winning_play, self.tricks)
            if winning_play is not None
        ]

        trump_wins = [
            play
            for play in winning_plays
            if play.card.suit == self.trump or play.card.always_trump
        ]
        highest_play = max(
            trump_wins, key=lambda play: play.card.trump_value, default=None
        )

        base_scores = list(
            map(
                lambda play: Score(
                    play.identifier,
                    TRICK_VALUE +
                    # treat the highest value play as two tricks
                    (TRICK_VALUE if play == highest_play else 0),
                ),
                winning_plays,
            )
        )

        # use default values here so scores can be calculated before tricks are played
        # should return all zeros
        acting_bidder = self.active_bidder or self.players[0]
        acting_bid = self.active_bid or BidAmount.PASS

        bidder_identifier = acting_bidder.identifier
        bidder_base_scores = list(
            filter(lambda score: score.identifier == bidder_identifier, base_scores)
        )
        non_bidder_base_scores = [
            score for score in base_scores if score not in bidder_base_scores
        ]
        bidder_base_score = sum(map(lambda score: score.value, bidder_base_scores))

        shot_the_moon = self.active_bid == BidAmount.SHOOT_THE_MOON and all(
            score.identifier == bidder_identifier for score in base_scores
        )
        met_bid = bidder_base_score >= acting_bid

        if shot_the_moon:
            return [Score(bidder_identifier, BidAmount.SHOOT_THE_MOON)]
        if not met_bid:
            return [Score(bidder_identifier, -1 * acting_bid)] + non_bidder_base_scores

        return base_scores

    def act(self, action: Action) -> None:
        """Perform an action as a player of the game"""
        if isinstance(action, Bid):
            self.__bid(action)
            self.__invalidate_cached_properties()
        if isinstance(action, SelectTrump):
            self.__select_trump(action)
            self.__invalidate_cached_properties()
        if isinstance(action, Discard):
            self.__discard(action)
            self.__invalidate_cached_properties()
            self.__end_discard()
        if isinstance(action, Play):
            self.__play(action)
            self.__invalidate_cached_properties()
            self.__end_play()
        self.__invalidate_cached_properties()

    def __bid(self, bid: Bid) -> None:
        """Record a bid from a player"""
        identifier = bid.identifier
        amount = bid.amount
        if (
            self.status == RoundStatus.BIDDING
            and self.active_player == player_by_identifier(self.players, identifier)
        ):
            self.__handle_bid(identifier, amount)
        else:
            raise HundredAndTenError("Cannot bid out of order")

    def __select_trump(self, select_trump: SelectTrump) -> None:
        """Select the passed suit as trump"""
        if self.status != RoundStatus.TRUMP_SELECTION:
            raise HundredAndTenError(
                "Cannot select trump outside of the trump selection phase."
            )
        if (
            not self.active_bidder
            or select_trump.identifier != self.active_bidder.identifier
        ):
            raise HundredAndTenError("Only the bidder can select trump.")

        self._select_trump = select_trump

    def __discard(self, discard: Discard) -> None:
        """
        Discard the selected cards from the identified player's hand and replace them
        """
        if self.status != RoundStatus.DISCARD:
            raise HundredAndTenError("Cannot discard outside of the discard phase.")
        if discard.identifier != self.active_player.identifier:
            raise HundredAndTenError("Only the active player can discard.")
        if any(card not in self.active_player.hand for card in discard.cards):
            raise HundredAndTenError(
                "You may only discard cards that are in your hand."
            )

        remaining = list(
            filter(lambda c: c not in discard.cards, self.active_player.hand)
        )

        self.active_player.hand = [*remaining]
        self.active_player.hand.extend(self.deck.draw(len(discard.cards)))
        self._discards.append(
            DetailedDiscard(discard.identifier, discard.cards, remaining)
        )

    def __play(self, play: Play) -> None:
        """Play the specified card from the identified player's hand"""

        active_player_trump_cards = trumps(self.active_player.hand, self.trump)

        if self.active_player.identifier != play.identifier:
            raise HundredAndTenError("Cannot play a card out of turn.")
        if play.card not in self.active_player.hand:
            raise HundredAndTenError("Cannot play a card you do not have.")
        if (
            self.active_trick.bleeding
            and active_player_trump_cards
            and play.card not in active_player_trump_cards
        ):
            raise HundredAndTenError(
                "You must play a trump card when the trick is bleeding."
            )

        self.active_player.hand.remove(play.card)
        self.active_trick.plays.append(play)

    def available_bids(self, identifier: str) -> list[BidAmount]:
        """Compute the bid amounts available to the identified player"""
        return [
            bid_amount
            for bid_amount in BidAmount
            if self.__is_available_bid(identifier, bid_amount)
        ]

    def __handle_bid(self, identifier: str, amount: BidAmount) -> None:
        if amount in self.available_bids(identifier):
            self._bids.append(Bid(identifier, amount))
        else:
            raise HundredAndTenError(
                f"Player {identifier} cannot place a bid for {amount.value}"
            )

    def __is_available_bid(self, identifier: str, amount: BidAmount) -> bool:
        """Determine if the listed bid amount is available to the listed player"""
        player = player_by_identifier(self.players, identifier)
        return (
            # the identified player must be able to submit a bid
            player in self.bidders
            and
            # pass is always available as a bid
            (
                amount == BidAmount.PASS
                or
                # no active bid means every bid is available
                not self.active_bid
                # if there is an active bid, the specified bid must be larger
                or amount > self.active_bid
                # unless the player is the dealer,
                # in which case it can be the same as the active bid
                or (self.dealer.identifier == identifier and amount == self.active_bid)
            )
        )

    def __current_bid(self, identifier: str) -> Optional[Bid]:
        """Return the most recent bid for the provided player"""
        loc_index = max(
            (loc for loc, val in enumerate(self.bids) if val.identifier == identifier),
            default=None,
        )
        return self.bids[loc_index] if loc_index is not None else None

    def __end_discard(self) -> None:
        if self.status == RoundStatus.TRICKS:
            self.__new_trick()

    def __end_play(self) -> None:
        if self.status == RoundStatus.TRICKS and len(self.active_trick.plays) == len(
            self.players
        ):
            self.__new_trick()

    def __new_trick(self) -> None:
        assert self.trump
        self.tricks.append(Trick(self.trump))

    def __invalidate_cached_properties(self) -> None:
        for name, value in type(self).__dict__.items():
            if isinstance(value, cached_property):
                self.__dict__.pop(name, None)
