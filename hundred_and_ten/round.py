'''Represent one round of a game of Hundred and Ten'''


from typing import Optional

from hundred_and_ten.bid import Bid
from hundred_and_ten.constants import BidAmount, RoundRole, RoundStatus
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError
from hundred_and_ten.people import People
from hundred_and_ten.person import Person


class Round:
    '''A round in the game of Hundred and Ten'''

    def __init__(self, players: Optional[People] = None, bids: Optional[list[Bid]] = None) -> None:
        self.players = players or People()
        self.bids = bids or []

    def bid(self, identifier: str, amount: BidAmount) -> None:
        "Record a bid from a player"
        if self.active_player == self.players.by_identifier(identifier):
            self.__bid(identifier, amount)
        elif amount == BidAmount.PASS:
            self.players.add_role(identifier, RoundRole.PRE_PASSED)
        else:
            raise HundredAndTenError("Cannot bid out of order")

    def unpass(self, identifier: str) -> None:
        '''Discount a prepass bid from the identified player'''
        self.players.remove_role(identifier, RoundRole.PRE_PASSED)

    def available_bids(self, identifier: str) -> list[BidAmount]:
        '''Compute the bid amounts available to the identified player'''
        return [
            bid_amount for bid_amount in BidAmount
            if self.__is_available_bid(identifier, bid_amount)
        ]

    def __bid(self, identifier: str, amount: BidAmount) -> None:
        if amount in self.available_bids(identifier):
            self.bids.append(Bid(identifier, amount))
        else:
            raise HundredAndTenError(f'Player {identifier} cannot place a bid for {amount.value}')

    def __is_available_bid(self, identifier: str, amount: BidAmount) -> bool:
        '''Determine if the listed bid amount is available to the listed player'''
        player = self.players.find_or_create(identifier)
        return (
            # the identified player must be able to submit a bid
            player in self.bidders and
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

    @property
    def dealer(self) -> Person:
        """The dealer this round."""
        active_p = next(iter(self.players.by_role(RoundRole.DEALER)), None)
        if active_p:
            return active_p
        raise HundredAndTenError("No dealer found.")

    @property
    def active_player(self) -> Person:
        """The current active player."""
        active_p = None
        # before bids, the active player is the one after the dealer
        if self.status == RoundStatus.DEALING:
            active_p = self.players.after(self.dealer.identifier)
        # while bidding, the active player is the one after the last bidder that can place a bid
        elif self.status == RoundStatus.BIDDING:
            last_bidder = self.bids[-1].identifier
            active_and_last_bidders = People(
                [p for p in self.players if p in self.bidders or p.identifier == last_bidder])
            active_p = active_and_last_bidders.after(last_bidder)
        # when in trump selection, the active bidder is the active player
        elif self.status == RoundStatus.TRUMP_SELECTION:
            active_p = self.active_bidder

        if active_p:
            return active_p
        raise HundredAndTenError("No active player found.")

    @property
    def inactive_players(self) -> People:
        """The players that are not active."""
        return People([p for p in self.players if p != self.active_player])

    @property
    def active_bid(self) -> Optional[BidAmount]:
        """The maximum bid submitted this round"""
        return max(self.bids).amount if self.bids else None

    @property
    def bidders(self) -> People:
        """Anyone in this round that can still submit a bid."""
        return People(
            [p for p in self.players
             if self.__current_bid(p.identifier) != Bid('', BidAmount.PASS)])

    @property
    def active_bidder(self) -> Optional[Person]:
        """The active bidder this round."""

        if len(self.bidders) == 1 and self.active_bid:
            return self.bidders[0]
        return None

    @property
    def status(self) -> RoundStatus:
        """The status property."""
        bids = len(self.bids)
        if bids == 0:
            return RoundStatus.DEALING
        if self.active_bidder:
            return RoundStatus.TRUMP_SELECTION
        if not self.bidders:
            return RoundStatus.COMPLETED_NO_BIDDERS
        return RoundStatus.BIDDING
