"""Unit test role operations on a list of players"""

from unittest import TestCase

from hundredandten.constants import RoundRole
from hundredandten.group import RoundGroup, RoundPlayer


class TestPeopleRoles(TestCase):
    """Role operations on People unit tests"""

    def test_add_role_with_no_players(self):
        """Does nothing when adding a role to a player an in empty list"""

        players = RoundGroup([])
        players.add_role("any", RoundRole.DEALER)

        self.assertEqual(0, len(players))

    def test_add_role_to_player_with_no_roles(self):
        """Adds a role to a player with no roles"""

        player = RoundPlayer("id")
        role = RoundRole.DEALER
        players = RoundGroup([player])
        players.add_role(player.identifier, role)

        self.assertEqual(1, len(players))
        self.assertIn(role, players[0].roles)

    def test_add_role_to_player_with_existing_roles(self):
        """Adds a role to a player with existing roles"""

        player = RoundPlayer("id", roles={RoundRole.DEALER})
        role = RoundRole.PRE_PASSED
        players = RoundGroup([player])
        players.add_role(player.identifier, role)

        self.assertEqual(1, len(players))
        self.assertLess(1, len(players[0].roles))
        self.assertIn(role, players[0].roles)

    def test_remove_role_with_no_players(self):
        """Does nothing when removing a role from a player an in empty list"""

        players = RoundGroup([])
        players.remove_role("any", RoundRole.DEALER)

        self.assertEqual(0, len(players))

    def test_remove_role_from_player_with_no_roles(self):
        """Removes a role from a player with no roles"""

        player = RoundPlayer("id")
        role = RoundRole.DEALER
        players = RoundGroup([player])
        players.remove_role(player.identifier, role)

        self.assertEqual(1, len(players))
        self.assertNotIn(role, players[0].roles)

    def test_remove_role_from_player_with_existing_roles(self):
        """Removes a role from a player with existing roles"""

        initial_roles = {RoundRole.PRE_PASSED, RoundRole.DEALER}
        initial_len = len(initial_roles)
        remove_role = next(iter(initial_roles))
        player = RoundPlayer("id", roles=initial_roles)
        players = RoundGroup([player])
        players.remove_role(player.identifier, remove_role)

        self.assertEqual(1, len(players))
        self.assertEqual(initial_len - 1, len(players[0].roles))
        self.assertNotIn(remove_role, players[0].roles)

    def test_swap_role(self):
        """Swaps a role between players"""

        role = RoundRole.DEALER
        player_one = RoundPlayer("one", roles={role})
        player_two = RoundPlayer("two")
        players = RoundGroup([player_one, player_two])

        self.assertIn(role, players[0].roles)
        self.assertNotIn(role, players[1].roles)

        players.swap_role(player_one.identifier, player_two.identifier, role)

        self.assertEqual(2, len(players))
        self.assertNotIn(role, players[0].roles)
        self.assertIn(role, players[1].roles)
