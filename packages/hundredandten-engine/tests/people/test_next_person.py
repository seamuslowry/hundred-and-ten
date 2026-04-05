"""Unit test determining the next person within a list of players"""

from unittest import TestCase

from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.player import RoundPlayer, player_after


class TestNextPlay(TestCase):
    """Next Player unit tests"""

    def test_after_with_no_players(self):
        """Finds no player in empty list"""

        self.assertRaises(HundredAndTenError, player_after, [], "any")

    def test_after_with_unknown_player(self):
        """Finds no player when not in list"""

        players = [RoundPlayer("1")]

        self.assertRaises(
            HundredAndTenError, player_after, players, players[0].identifier + "bad"
        )

    def test_after_with_one_player(self):
        """Determines the next player in a list of 1"""

        person_one = RoundPlayer("1")
        players = [person_one]

        self.assertEqual(person_one, player_after(players, person_one.identifier))

    def test_after_with_two_players(self):
        """Determines the next player in a list of 2"""

        person_one = RoundPlayer("1")
        person_two = RoundPlayer("2")
        players = [person_one, person_two]

        self.assertEqual(person_two, player_after(players, person_one.identifier))
        self.assertEqual(person_one, player_after(players, person_two.identifier))

    def test_after_with_three_players(self):
        """Determines the next player in a list of 3"""

        person_one = RoundPlayer("1")
        person_two = RoundPlayer("2")
        person_three = RoundPlayer("3")

        players = [person_one, person_two, person_three]

        self.assertEqual(person_two, player_after(players, person_one.identifier))
        self.assertEqual(person_three, player_after(players, person_two.identifier))
        self.assertEqual(person_one, player_after(players, person_three.identifier))

    def test_after_with_four_players(self):
        """Determines the next player in a list of 4"""

        person_one = RoundPlayer("1")
        person_two = RoundPlayer("2")
        person_three = RoundPlayer("3")
        person_four = RoundPlayer("4")

        players = [person_one, person_two, person_three, person_four]

        self.assertEqual(person_two, player_after(players, person_one.identifier))
        self.assertEqual(person_three, player_after(players, person_two.identifier))
        self.assertEqual(person_four, player_after(players, person_three.identifier))
        self.assertEqual(person_one, player_after(players, person_four.identifier))
