"""Person unit tests"""

from unittest import TestCase

from hundredandten.constants import CardNumber, RoundRole, SelectableSuit
from hundredandten.deck import Card
from hundredandten.group import Player, RoundPlayer


class TestPlayer(TestCase):
    """Player unit tests"""

    def test_players_equal_by_identifier_only(self):
        """When checking if players are equal, only the identifier matters"""
        identifier = "1"
        self.assertEqual(
            Player(identifier),
            Player(identifier, automate=True),
        )
        self.assertNotEqual(Player("one"), Player("two"))

    def test_round_players_equal_by_identifier_only(self):
        """When checking ifround  players are equal, only the identifier matters"""
        identifier = "1"
        self.assertEqual(
            RoundPlayer(identifier),
            RoundPlayer(
                identifier,
                automate=True,
                roles={RoundRole.DEALER},
                hand=[Card(CardNumber.ACE, SelectableSuit.CLUBS)],
            ),
        )
        self.assertNotEqual(Player("one"), Player("two"))
