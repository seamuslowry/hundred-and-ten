'''Helpers to create a game in setup for testing'''

from hundredandten.constants import BidAmount, GameRole
from hundredandten.game import Game
from hundredandten.group import Group, Person


def get_waiting_for_players_game(player_count: int = 2) -> Game:
    '''Returns a game that is waiting for players'''
    return Game(
        people=Group(
            list(map(
                lambda identifier: Person(str(identifier), roles={GameRole.PLAYER}),
                range(player_count)))))


def get_bidding_game(player_count: int = 2) -> Game:
    '''Returns a game in the bidding status'''
    game = get_waiting_for_players_game(player_count)
    game.start_game()
    return game


def get_completed_no_bidders_game(player_count: int = 2) -> Game:
    '''Returns a game in the completed no bidders status'''
    game = get_bidding_game(player_count)
    for player in game.players:
        game.bid(player.identifier, BidAmount.PASS)
    return game


def get_trump_selection_game(player_count: int = 2) -> Game:
    '''Return a game in the trump selection status'''
    game = get_bidding_game(player_count)
    for player in game.active_round.inactive_players:
        game.bid(player.identifier, BidAmount.PASS)
    game.bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)
    return game
