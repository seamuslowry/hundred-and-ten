'''Helpers to create a game in setup for testing'''

from hundredandten.constants import BidAmount, GameRole
from hundredandten.game import Game
from hundredandten.group import Group, Person


def get_waiting_for_players_game() -> Game:
    '''Returns a game that is waiting for players'''
    return Game(
        people=Group(
            [Person('1', roles={GameRole.PLAYER}),
             Person('2', roles={GameRole.PLAYER})]))


def get_bidding_game() -> Game:
    '''Returns a game in the bidding status'''
    game = get_waiting_for_players_game()
    game.start_game()
    return game


def get_trump_selection_game() -> Game:
    '''Return a game in the trump selection status'''
    game = get_bidding_game()
    game.bid(game.active_round.active_player.identifier, BidAmount.PASS)
    game.bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN)
    return game
