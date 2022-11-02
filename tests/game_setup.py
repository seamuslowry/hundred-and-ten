'''Helpers to set up a game for testing'''

from hundredandten.constants import (AnyStatus, BidAmount, GameRole,
                                     GameStatus, RoundStatus, SelectableSuit)
from hundredandten.game import Game
from hundredandten.group import Group, Person


def setup_game(status: AnyStatus, player_count: int = 2) -> Game:
    '''Return a game in the requested status'''

    return {
        GameStatus.WAITING_FOR_PLAYERS: __get_waiting_for_players_game,
        RoundStatus.BIDDING: __get_bidding_game,
        RoundStatus.COMPLETED_NO_BIDDERS: __get_completed_no_bidders_game,
        RoundStatus.TRUMP_SELECTION: __get_trump_selection_game
    }[status](player_count)


def __get_waiting_for_players_game(player_count: int = 2) -> Game:
    '''Returns a game that is waiting for players'''
    return Game(
        people=Group(
            list(map(
                lambda identifier: Person(str(identifier), roles={GameRole.PLAYER}),
                range(player_count)))))


def __get_bidding_game(player_count: int = 2) -> Game:
    '''Returns a game in the bidding status'''
    game = __get_waiting_for_players_game(player_count)
    game.start_game()
    return game


def __get_completed_no_bidders_game(player_count: int = 2) -> Game:
    '''Returns a game in the completed no bidders status'''
    game = __get_bidding_game(player_count)
    for player in game.players:
        game.bid(player.identifier, BidAmount.PASS)
    return game


def __get_trump_selection_game(player_count: int = 2) -> Game:
    '''Return a game in the trump selection status'''
    game = __get_bidding_game(player_count)
    for player in game.active_round.inactive_players:
        game.bid(player.identifier, BidAmount.PASS)
    game.bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)
    return game


def get_tricks_game(player_count: int = 2) -> Game:
    '''Return a game in the tricks status'''
    game = __get_trump_selection_game(player_count)
    game.select_trump(game.active_round.active_player.identifier, SelectableSuit.SPADES)
    return game
