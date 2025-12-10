'''Helpers to set up a game for testing'''
from typing import Callable, Optional
from uuid import uuid4

from hundredandten.actions import Bid, Discard, Play, SelectTrump
from hundredandten.constants import AnyStatus, BidAmount, GameStatus, RoundStatus, SelectableSuit
from hundredandten.decisions import trumps
from hundredandten.game import Game
from hundredandten.group import Group, Player


def automated_game(
        status: AnyStatus,
        massage: Callable[[Game], None] = lambda f_game: None,
        seed: Optional[str] = None) -> Game:
    return __game(status, massage, seed, True)

def game(
        status: AnyStatus,
        massage: Callable[[Game], None] = lambda f_game: None,
        seed: Optional[str] = None) -> Game:
    return __game(status, massage, seed, False)

def __game(
        status: AnyStatus,
        massage: Callable[[Game], None] = lambda f_game: None,
        seed: Optional[str] = None,
        automate: Optional[bool] = False) -> Game:
    '''
    Return a game in the requested status.
    If passed, will call the massage function on the game before returning
    '''

    new_game = {
        RoundStatus.BIDDING: __get_bidding_game,
        RoundStatus.COMPLETED_NO_BIDDERS: __get_completed_no_bidders_game,
        RoundStatus.TRUMP_SELECTION: __get_trump_selection_game,
        RoundStatus.DISCARD: __get_discard_game,
        RoundStatus.TRICKS: __get_tricks_game,
        GameStatus.WON: __get_won_game
    }[status](seed, automate)
    massage(new_game)
    return new_game


def pass_round(game_to_pass: Game) -> None:
    '''Pass the current round of the provided game'''
    for player in game_to_pass.active_round.bidders:
        game_to_pass.act(Bid(player.identifier, BidAmount.PASS))


def pass_to_dealer(game_to_pass: Game) -> None:
    '''Pass the current round until reaching the dealer'''
    for player in filter(
            lambda player: player != game_to_pass.active_round.dealer,
            game_to_pass.active_round.bidders):
        game_to_pass.act(Bid(player.identifier, BidAmount.PASS))


def bid(game_to_bid: Game) -> None:
    '''Have the active player place a bid'''
    for player in game_to_bid.active_round.inactive_players:
        game_to_bid.act(Bid(player.identifier, BidAmount.PASS))
    game_to_bid.act(Bid(game_to_bid.active_round.active_player.identifier, BidAmount.FIFTEEN))


def select_trump(game_to_select: Game) -> None:
    '''Have the active player select a trump'''
    game_to_select.act(SelectTrump(
        game_to_select.active_round.active_player.identifier, SelectableSuit.SPADES))


def discard(game_to_discard: Game) -> None:
    '''Have all players discard'''
    while game_to_discard.status == RoundStatus.DISCARD:
        game_to_discard.act(Discard(game_to_discard.active_round.active_player.identifier, []))


def play_trick(game_to_play: Game) -> None:
    '''Play through the current trick of the provided game'''
    starting_active_trick = game_to_play.active_round.active_trick
    while len(starting_active_trick.plays) < len(game_to_play.players):
        active_player = game_to_play.active_round.active_player
        trump_cards = trumps(active_player.hand, game_to_play.active_round.trump)
        game_to_play.act(
            Play(
                active_player.identifier, next(
                    iter(trump_cards + active_player.hand))))


def play_round(game_to_play: Game) -> None:
    '''Play through the current trick of the provided game'''
    while game_to_play.status == RoundStatus.TRICKS:
        play_trick(game_to_play)

def __get_bidding_game(seed: Optional[str], automate: Optional[bool] = False) -> Game:
    '''Returns a game with no moves'''
    new_game = Game(
        players=Group(
            list(map(
                lambda identifier: Player(str(identifier), automate=automate),
                range(4)))), seed=seed or str(uuid4()))
    return new_game

def __get_completed_no_bidders_game(seed: Optional[str], automate: Optional[bool] = False) -> Game:
    '''Returns a game in the completed no bidders status'''
    new_game = __get_bidding_game(seed, automate)
    pass_round(new_game)
    return new_game


def __get_trump_selection_game(seed: Optional[str], automate: Optional[bool] = False) -> Game:
    '''Return a game in the trump selection status'''
    new_game = __get_bidding_game(seed, automate)
    bid(new_game)
    return new_game


def __get_discard_game(seed: Optional[str], automate: Optional[bool] = False) -> Game:
    '''Return a game in the discard status'''
    new_game = __get_trump_selection_game(seed, automate)
    select_trump(new_game)
    return new_game


def __get_tricks_game(seed: Optional[str], automate: Optional[bool] = False) -> Game:
    '''Return a game in the tricks status'''
    new_game = __get_discard_game(seed, automate)
    discard(new_game)

    return new_game


def __get_won_game(seed: Optional[str], automate: Optional[bool] = False) -> Game:
    '''Return a game in the won status'''
    new_game = __get_bidding_game(seed, automate)
    while new_game.status != GameStatus.WON:
        bid(new_game)
        select_trump(new_game)
        discard(new_game)
        play_round(new_game)

    return new_game
