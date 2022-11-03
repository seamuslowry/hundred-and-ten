'''Helpers to set up a game for testing'''

from typing import Callable, Optional

from hundredandten.constants import (AnyStatus, BidAmount, CardNumber,
                                     CardSuit, GameRole, GameStatus,
                                     RoundStatus, SelectableSuit)
from hundredandten.deck import Card, cards
from hundredandten.discard import Discard
from hundredandten.game import Game
from hundredandten.group import Group, Person
from hundredandten.trick import Play


def game(
        status: AnyStatus,
        massage: Callable[[Game], None] = lambda f_game: None,
        seed: Optional[str] = None) -> Game:
    '''
    Return a game in the requested status.
    If passed, will call the massage function on the game before returning
    '''

    new_game = {
        GameStatus.WAITING_FOR_PLAYERS: __get_waiting_for_players_game,
        RoundStatus.BIDDING: __get_bidding_game,
        RoundStatus.COMPLETED_NO_BIDDERS: __get_completed_no_bidders_game,
        RoundStatus.TRUMP_SELECTION: __get_trump_selection_game,
        RoundStatus.DISCARD: __get_discard_game,
        RoundStatus.TRICKS: __get_tricks_game
    }[status](seed)
    massage(new_game)
    return new_game


def card(number: CardNumber, suit: CardSuit) -> Card:
    '''Get the card with the given number and suit'''
    return next(card for card in cards if card.suit == suit and card.number == number)


def nothing_card(trump: CardSuit) -> Card:
    '''Get the card that is not a trump given the trump suit'''
    return next(card for card in cards if card.suit != trump and not card.always_trump)


def make_space(game_to_open: Game) -> None:
    '''Make space in the game, which will be full by default when arranged by this file'''
    game_to_open.leave(game_to_open.players[-1].identifier)


def pass_round(game_to_pass: Game) -> None:
    '''Pass the current round of the provided game'''
    for player in game_to_pass.active_round.bidders:
        game_to_pass.bid(player.identifier, BidAmount.PASS)


def pass_to_dealer(game_to_pass: Game) -> None:
    '''Pass the current round until reaching the dealer'''
    for player in filter(
            lambda player: player != game_to_pass.active_round.dealer,
            game_to_pass.active_round.bidders):
        game_to_pass.bid(player.identifier, BidAmount.PASS)


def play_trick(game_to_play: Game) -> None:
    '''Play through the current trick of the provided game'''
    preexisting_trick_count = len(game_to_play.active_round.tricks)
    while len(game_to_play.active_round.tricks) == preexisting_trick_count:
        active_player = game_to_play.active_round.active_player
        game_to_play.play(Play(active_player.identifier, active_player.hand[0]))


def play_round(game_to_play: Game) -> None:
    '''Play through the current trick of the provided game'''
    preexisting_round_count = len(game_to_play.rounds)
    while len(game_to_play.rounds) == preexisting_round_count:
        play_trick(game_to_play)


def __get_waiting_for_players_game(seed: Optional[str]) -> Game:
    '''Returns a game that is waiting for players'''
    new_game = Game(
        people=Group(
            list(map(
                lambda identifier: Person(str(identifier), roles={GameRole.PLAYER}),
                range(4)))), **{k: v for k, v in {'seed': seed}.items() if v is not None})
    new_game.people.add_role(new_game.people[0].identifier, GameRole.ORGANIZER)
    return new_game


def __get_bidding_game(seed: Optional[str]) -> Game:
    '''Returns a game in the bidding status'''
    new_game = __get_waiting_for_players_game(seed)
    new_game.start_game()
    return new_game


def __get_completed_no_bidders_game(seed: Optional[str]) -> Game:
    '''Returns a game in the completed no bidders status'''
    new_game = __get_bidding_game(seed)
    pass_round(new_game)
    return new_game


def __get_trump_selection_game(seed: Optional[str]) -> Game:
    '''Return a game in the trump selection status'''
    new_game = __get_bidding_game(seed)
    for player in new_game.active_round.inactive_players:
        new_game.bid(player.identifier, BidAmount.PASS)
    new_game.bid(new_game.active_round.active_player.identifier, BidAmount.FIFTEEN)
    return new_game


def __get_discard_game(seed: Optional[str]) -> Game:
    '''Return a game in the discard status'''
    new_game = __get_trump_selection_game(seed)
    new_game.select_trump(new_game.active_round.active_player.identifier, SelectableSuit.SPADES)
    return new_game


def __get_tricks_game(seed: Optional[str]) -> Game:
    '''Return a game in the tricks status'''
    new_game = __get_discard_game(seed)
    while new_game.status == RoundStatus.DISCARD:
        new_game.discard(Discard(new_game.active_round.active_player.identifier, []))

    return new_game
