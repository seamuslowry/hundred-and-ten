"""Helpers to set up a game for testing"""

from typing import Callable, Optional
from uuid import uuid4

from hundredandten.deck import SelectableSuit
from hundredandten.engine.actions import Bid, Discard, Play, SelectTrump
from hundredandten.engine.constants import (
    BidAmount,
    Status,
)
from hundredandten.engine.game import Game
from hundredandten.engine.player import Player


def game(
    status: Status,
    massage: Callable[[Game], None] = lambda f_game: None,
    seed: Optional[str] = None,
) -> Game:
    """
    Return a game in the requested status.
    If passed, will call the massage function on the game before returning
    """

    return __game(status, massage, seed)


def __game(
    status: Status,
    massage: Callable[[Game], None] = lambda f_game: None,
    seed: Optional[str] = None,
) -> Game:
    """
    Return a game in the requested status.
    If passed, will call the massage function on the game before returning.
    Will automate players based on the automated flag.
    """

    new_game = {
        Status.BIDDING: __get_bidding_game,
        Status.COMPLETED_NO_BIDDERS: __get_completed_no_bidders_game,
        Status.TRUMP_SELECTION: __get_trump_selection_game,
        Status.DISCARD: __get_discard_game,
        Status.TRICKS: __get_tricks_game,
        Status.WON: __get_won_game,
    }[status](seed)
    massage(new_game)
    return new_game


def pass_round(game_to_pass: Game) -> None:
    """Pass the current round of the provided game"""
    for _ in range(len(game_to_pass.active_round.bidders)):
        game_to_pass.act(Bid(game_to_pass.active_player.identifier, BidAmount.PASS))


def pass_to_dealer(game_to_pass: Game) -> None:
    """Pass the current round until reaching the dealer"""
    while (
        p := game_to_pass.active_player
    ).identifier != game_to_pass.active_round.dealer.identifier:
        game_to_pass.act(Bid(p.identifier, BidAmount.PASS))


def bid(game_to_bid: Game) -> None:
    """Have the active player place a bid"""
    game_to_bid.act(
        Bid(game_to_bid.active_round.active_player.identifier, BidAmount.FIFTEEN)
    )

    while game_to_bid.status != Status.TRUMP_SELECTION:
        game_to_bid.act(Bid(game_to_bid.active_player.identifier, BidAmount.PASS))


def select_trump(game_to_select: Game) -> None:
    """Have the active player select a trump"""
    game_to_select.act(
        SelectTrump(
            game_to_select.active_round.active_player.identifier, SelectableSuit.SPADES
        )
    )


def discard(game_to_discard: Game) -> None:
    """Have all players discard"""
    while game_to_discard.status == Status.DISCARD:
        game_to_discard.act(
            Discard(game_to_discard.active_round.active_player.identifier, [])
        )


def play_trick(game_to_play: Game) -> None:
    """Play through the current trick of the provided game"""
    starting_active_trick = game_to_play.active_round.active_trick
    while len(starting_active_trick.plays) < len(game_to_play.players):
        active_player = game_to_play.active_round.active_player
        trump_cards = list(
            card
            for card in active_player.hand
            if card.trump_for_selection(game_to_play.active_round.trump)
        )
        game_to_play.act(
            Play(active_player.identifier, next(iter(trump_cards + active_player.hand)))
        )


def play_round(game_to_play: Game) -> None:
    """Play through the current round of tricks of the provided game"""
    while game_to_play.status == Status.TRICKS:
        play_trick(game_to_play)


def __get_bidding_game(seed: Optional[str]) -> Game:
    """Returns a game with no actions taken"""
    new_game = Game(
        players=list(
            map(
                lambda identifier: Player(str(identifier)),
                range(4),
            )
        ),
        seed=seed or str(uuid4()),
    )
    return new_game


def __get_completed_no_bidders_game(seed: Optional[str]) -> Game:
    """Returns a game in the completed no bidders status"""
    new_game = __get_bidding_game(seed)
    pass_round(new_game)
    return new_game


def __get_trump_selection_game(seed: Optional[str]) -> Game:
    """Return a game in the trump selection status"""
    new_game = __get_bidding_game(seed)
    bid(new_game)
    return new_game


def __get_discard_game(seed: Optional[str]) -> Game:
    """Return a game in the discard status"""
    new_game = __get_trump_selection_game(seed)
    select_trump(new_game)
    return new_game


def __get_tricks_game(seed: Optional[str]) -> Game:
    """Return a game in the tricks status"""
    new_game = __get_discard_game(seed)
    discard(new_game)

    return new_game


def __get_won_game(seed: Optional[str]) -> Game:
    """Return a game in the won status"""
    new_game = __get_bidding_game(seed)
    while new_game.status != Status.WON:
        bid(new_game)
        select_trump(new_game)
        discard(new_game)
        play_round(new_game)

    return new_game
