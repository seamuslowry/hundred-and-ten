'''Represent one round of a game of Hundred and Ten'''


from dataclasses import dataclass, field
from typing import Optional

from hundredandten.bid import Bid
from hundredandten.constants import (TRICK_VALUE, BidAmount, RoundRole,
                                     RoundStatus, SelectableSuit)
from hundredandten.deck import Deck
from hundredandten.discard import Discard
from hundredandten.group import Group, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.trick import Play, Score, Trick


@dataclass
class Round:
    '''A round in the game of Hundred and Ten'''
    players: Group[Player] = field(default_factory=Group)
    bids: list[Bid] = field(default_factory=list)
    deck: Deck = field(default_factory=Deck)
    trump: Optional[SelectableSuit] = None
    discards: list[Discard] = field(default_factory=list)
    tricks: list[Trick] = field(default_factory=list)

    def bid(self, identifier: str, amount: BidAmount) -> None:
        "Record a bid from a player"
        if self.status == RoundStatus.BIDDING and self.active_player == self.players.by_identifier(
                identifier):
            self.__bid(identifier, amount)
        elif amount == BidAmount.PASS:
            self.players.add_role(identifier, RoundRole.PRE_PASSED)
        else:
            raise HundredAndTenError("Cannot bid out of order")

    def unpass(self, identifier: str) -> None:
        '''Discount a prepass bid from the identified player'''
        self.players.remove_role(identifier, RoundRole.PRE_PASSED)

    def select_trump(self, identifier: str, suit: SelectableSuit) -> None:
        '''Select the passed suit as trump'''
        if self.status != RoundStatus.TRUMP_SELECTION:
            raise HundredAndTenError("Cannot select trump outside of the trump selection phase.")
        if not self.active_bidder or identifier != self.active_bidder.identifier:
            raise HundredAndTenError("Only the bidder can select trump.")

        self.trump = suit

    def discard(self, discard: Discard) -> None:
        '''
        Discard the selected cards from the identified player's hand and replace them
        '''
        if self.status != RoundStatus.DISCARD:
            raise HundredAndTenError("Cannot discard outside of the discard phase.")
        if discard.identifier != self.active_player.identifier:
            raise HundredAndTenError("Only the active player can discard.")
        if any(card not in self.active_player.hand for card in discard.cards):
            raise HundredAndTenError("You may only discard cards that are in your hand.")

        self.active_player.hand = list(
            filter(lambda c: c not in discard.cards, self.active_player.hand))
        self.active_player.hand.extend(self.deck.draw(len(discard.cards)))
        self.discards.append(discard)
        self.__end_discard()

    def play(self, play: Play) -> None:
        '''Play the specified card from the identified player's hand'''

        active_player_trump_cards = [
            card for card in self.active_player.hand
            if card.suit == self.trump or card.always_trump]

        if self.active_player.identifier != play.identifier:
            raise HundredAndTenError("Cannot play a card out of turn.")
        if play.card not in self.active_player.hand:
            raise HundredAndTenError("Cannot play a card you do not have.")
        if (self.active_trick.bleeding and
                active_player_trump_cards and
                not play.card in active_player_trump_cards):
            raise HundredAndTenError("You must play a trump card when the trick is bleeding.")

        self.active_player.hand.remove(play.card)
        self.active_trick.plays.append(play)
        self.__end_play()

    def available_bids(self, identifier: str) -> list[BidAmount]:
        '''Compute the bid amounts available to the identified player'''
        return [
            bid_amount for bid_amount in BidAmount
            if self.__is_available_bid(identifier, bid_amount)
        ]

    def __bid(self, identifier: str, amount: BidAmount) -> None:
        if amount in self.available_bids(identifier):
            self.bids.append(Bid(identifier, amount))
            self.__handle_prepass()
        else:
            raise HundredAndTenError(f'Player {identifier} cannot place a bid for {amount.value}')

    def __handle_prepass(self) -> None:
        if self.status == RoundStatus.BIDDING and RoundRole.PRE_PASSED in self.active_player.roles:
            self.players.remove_role(self.active_player.identifier, RoundRole.PRE_PASSED)
            self.__bid(self.active_player.identifier, BidAmount.PASS)

    def __is_available_bid(self, identifier: str, amount: BidAmount) -> bool:
        '''Determine if the listed bid amount is available to the listed player'''
        player = self.players.find_or_use(Player(identifier))
        return (
            # the identified player must be able to submit a bid
            (player in self.bidders and RoundRole.PRE_PASSED not in player.roles) and
            # pass is always available as a bid
            (amount == BidAmount.PASS or
             # no active bid means every bid is available
             not self.active_bid
             # if there is an active bid, the specified bid must be larger
             or amount > self.active_bid
             # unless the player is the dealer, in which case it can be the same as the active bid
             or (self.dealer.identifier == identifier and amount == self.active_bid))
        )

    def __current_bid(self, identifier: str) -> Optional[Bid]:
        '''Return the most recent bid for the provided player'''
        loc_index = max(
            (loc for loc, val in enumerate(self.bids) if val.identifier == identifier),
            default=None)
        return self.bids[loc_index] if loc_index is not None else None

    def __end_discard(self) -> None:
        if self.status == RoundStatus.TRICKS:
            self.__new_trick()

    def __end_play(self) -> None:
        if self.status == RoundStatus.TRICKS and len(self.active_trick.plays) == len(self.players):
            self.__new_trick()

    def __new_trick(self) -> None:
        assert self.trump
        self.tricks.append(Trick(self.trump))

    @property
    def dealer(self) -> Player:
        """The dealer this round."""
        dlr = next(iter(self.players.by_role(RoundRole.DEALER)), None)
        if not dlr:
            raise HundredAndTenError("No dealer found.")
        return dlr

    @property
    def active_player(self) -> Player:
        """The current active player."""
        # while bidding, the active player is the one after the last bidder that can place a bid
        if self.status == RoundStatus.BIDDING:
            # before anyone has bid, treat the dealer as the last bidder
            last_bidder = self.dealer.identifier if not self.bids else self.bids[-1].identifier
            active_and_last_bidders = Group(
                [p for p in self.players if p in self.bidders or p.identifier == last_bidder])
            return active_and_last_bidders.after(last_bidder)
        # when in trump selection, the active bidder is the active player
        if self.status == RoundStatus.TRUMP_SELECTION:
            assert self.active_bidder
            return self.active_bidder
        if self.status == RoundStatus.DISCARD:
            assert self.active_bidder
            last_discarder = (self.dealer.identifier
                              if not self.discards else self.discards[-1].identifier)
            return self.players.after(last_discarder)
        # while playing tricks, active player needs to consider
        # trick number, trick status, and winner of last trick
        if self.status == RoundStatus.TRICKS:
            assert self.active_bidder
            assert self.trump
            # when we're starting a new trick
            if not self.active_trick.plays:
                # the player after the bidder goes first on the first trick
                if len(self.tricks) == 1:
                    return self.players.after(self.active_bidder.identifier)
                # otherwise, its the winner of the last trick
                winning_play = self.tricks[-2].winning_play
                # when we have more than one trick, any previous trick will have a winning play
                assert winning_play
                winner = self.players.by_identifier(winning_play.identifier)
                # when the trick has a winning play, there will be a valid player associated to it
                assert winner
                return winner
            # in an ongoing trick, active player is next around the table
            return self.players.after(self.active_trick.plays[-1].identifier)
        raise HundredAndTenError(f'Cannot determine active player in {self.status} status')

    @property
    def inactive_players(self) -> Group[Player]:
        """The players that are not active."""
        return Group([p for p in self.players if p != self.active_player])

    @property
    def active_bid(self) -> Optional[BidAmount]:
        """The maximum bid submitted this round"""
        return max(self.bids).amount if self.bids else None

    @property
    def bidders(self) -> Group[Player]:
        """Anyone in this round that can still submit a bid."""
        return Group(
            [p for p in self.players
             if self.__current_bid(p.identifier) != Bid('', BidAmount.PASS)])

    @property
    def active_bidder(self) -> Optional[Player]:
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

    @property
    def status(self) -> RoundStatus:
        """The status property."""
        if self.tricks and all(not player.hand for player in self.players):
            return RoundStatus.COMPLETED
        if len(self.discards) == len(self.players):
            return RoundStatus.TRICKS
        if self.trump:
            return RoundStatus.DISCARD
        if self.active_bidder:
            return RoundStatus.TRUMP_SELECTION
        if not self.bidders:
            return RoundStatus.COMPLETED_NO_BIDDERS
        return RoundStatus.BIDDING

    @property
    def scores(self) -> list[Score]:
        """
        The scores each player earned for this round
        A list of tuples in the form
        left: player identifier
        value: score for the trick

        The list will come in the order the points were earned.
        This is to determine a disputed winner
        """
        naive_scores = self.__ordered_naive_scores

        # use default values here so scores can be calculated before tricks are played
        # should return all zeros
        acting_bidder = self.active_bidder or self.players[0]
        acting_bid = self.active_bid or BidAmount.PASS

        bidder_identifier = acting_bidder.identifier
        bidder_naive_scores = list(
            filter(
                lambda score: score.identifier == bidder_identifier,
                naive_scores))
        non_bidder_naive_scores = [score for score in naive_scores
                                   if score not in bidder_naive_scores]
        bidder_naive_score = sum(map(lambda score: score.value, bidder_naive_scores))

        shot_the_moon = self.active_bid == BidAmount.SHOOT_THE_MOON and all(
            score.identifier == bidder_identifier for score in naive_scores)
        met_bid = bidder_naive_score >= acting_bid

        if shot_the_moon:
            return [Score(bidder_identifier, BidAmount.SHOOT_THE_MOON)]
        if not met_bid:
            return [Score(bidder_identifier, -1 * acting_bid)] + non_bidder_naive_scores

        return naive_scores

    @property
    def __ordered_naive_scores(self) -> list[Score]:
        none_type_winning_plays = [trick.winning_play for trick in self.tricks]
        winning_plays = [play for play in none_type_winning_plays if play is not None]

        trump_wins = [play for play in winning_plays
                      if play.card.suit == self.trump or
                      play.card.always_trump]
        highest_play = max(
            trump_wins, key=lambda play: play.card.trump_value, default=None)

        return list(map(lambda play: Score(play.identifier, TRICK_VALUE +
                                           # treat the highest value play as two tricks
                                           (TRICK_VALUE if play == highest_play else 0)),
                        winning_plays))
