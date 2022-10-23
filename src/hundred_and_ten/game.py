'''Provide a classe to represent a game of Hundred and Ten'''
from uuid import uuid4

from hundred_and_ten.constants import PUBLIC, GameStatus
from hundred_and_ten.hundred_and_ten_error import HundredAndTenError


class Game:
    '''A Game of Hundred and Ten'''

    def __init__(self, player_data, accessibility=PUBLIC, uuid=None):
        self.uuid = uuid or uuid4()
        self.accessibility = accessibility
        self.player_data = player_data

    def invite(self, invitee):
        '''Invite a player to the game'''
        self.player_data.invitees.append(invitee)

    def join_game(self, player):
        '''Add a player to the game'''

        below_player_cap = len(self.player_data.players) < 4
        waiting_for_players = self.status == GameStatus.WAITING_FOR_PLAYERS
        public_game = self.accessibility == PUBLIC
        invited = player in [self.player_data.organizer] + self.player_data.invitees

        if waiting_for_players and below_player_cap and (public_game or invited):
            self.player_data.players.append(player)
        else:
            raise HundredAndTenError(
                ("Cannot join this game."
                 " It is either at capacity or you have not received an invitation."))

    @property
    def status(self):
        """The status property."""
        return GameStatus.WAITING_FOR_PLAYERS
