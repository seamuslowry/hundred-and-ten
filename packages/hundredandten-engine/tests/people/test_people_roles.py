"""Unit test role operations on a list of players"""

from unittest import TestCase

from hundredandten.engine.constants import RoundRole
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.player import RoundPlayer, add_player_role, remove_player_role


class TestPeopleRoles(TestCase):
    """Role operations on People unit tests"""

    def test_add_role_with_no_players(self):
        """Does nothing when adding a role to a player an in empty list"""

        players = []
        self.assertRaises(
            HundredAndTenError, add_player_role, players, "any", RoundRole.DEALER
        )

        self.assertEqual(0, len(players))

    def test_add_role_to_player_with_no_roles(self):
        """Adds a role to a player with no roles"""

        player = RoundPlayer("id")
        role = RoundRole.DEALER
        players = [player]
        add_player_role(players, player.identifier, role)

        self.assertEqual(1, len(players))
        self.assertIn(role, players[0].roles)

    def test_remove_role_with_no_players(self):
        """Does nothing when removing a role from a player an in empty list"""

        players = []
        self.assertRaises(
            HundredAndTenError, remove_player_role, players, "any", RoundRole.DEALER
        )

        self.assertEqual(0, len(players))

    def test_remove_role_from_player_with_no_roles(self):
        """Removes a role from a player with no roles"""

        player = RoundPlayer("id")
        role = RoundRole.DEALER
        players = [player]
        remove_player_role(players, player.identifier, role)

        self.assertEqual(1, len(players))
        self.assertNotIn(role, players[0].roles)
