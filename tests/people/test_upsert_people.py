"""Unit test common upserting into a list of players"""

from unittest import TestCase

from hundredandten.constants import RoundRole
from hundredandten.group import Group, Player


class TestUpsertPlayers(TestCase):
    """Upsert Players unit tests"""

    def test_upsert_player_not_in_list(self):
        """Upsert a player that is not in the list"""

        player = Player("1")
        players = Group()

        pre_len = len(players)

        players.upsert(player)

        self.assertEqual(pre_len + 1, len(players))
        self.assertIn(player, players)

    def test_upsert_player_in_list(self):
        """Upsert a player that is in the list"""

        player = Player("1")
        players = Group([player])

        pre_len = len(players)

        players.upsert(player)

        self.assertEqual(pre_len, len(players))
        self.assertIn(player, players)

    def test_upsert_player_in_list_with_no_roles(self):
        """Upsert a player that is in the list but has no roles"""

        identifier = "1"
        player = Player(identifier)
        player_with_roles = Player(identifier, {RoundRole.DEALER})
        players = Group([player])

        pre_len = len(players)

        players.upsert(player_with_roles)

        self.assertEqual(pre_len, len(players))
        self.assertEqual(players[0], player_with_roles)
        self.assertEqual({RoundRole.DEALER}, players[0].roles)

    def test_upsert_player_in_list_with_different_roles(self):
        """Upsert a player that is in the list but has different roles"""

        identifier = "1"
        player_player = Player(identifier, {RoundRole.DEALER})
        player_prepassed = Player(identifier, {RoundRole.PRE_PASSED})
        players = Group([player_player])

        pre_len = len(players)

        players.upsert(player_prepassed)

        self.assertEqual(pre_len, len(players))
        self.assertEqual(players[0], player_prepassed)
        self.assertEqual({RoundRole.PRE_PASSED}, players[0].roles)

    def test_upsert_player_maintains_position(self):
        """Upsert a player that is not in the list"""

        identifier = "p"
        player = Player(identifier)
        new_player = Player(identifier, {RoundRole.PRE_PASSED})
        players = Group([Player("1"), player, Player("2")])
        pre_len = len(players)
        pre_index = players.index(player)

        players.upsert(new_player)

        self.assertEqual(pre_len, len(players))
        self.assertEqual(pre_index, players.index(new_player))
