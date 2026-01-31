"""Person unit tests"""

from unittest import TestCase

from hundredandten.constants import CardNumber, RoundRole, SelectableSuit
from hundredandten.deck import Card
from hundredandten.group import Player


class TestPlayer(TestCase):
    """Player unit tests"""

    def test_players_equal_by_identifier_only(self):
        """When checking if players are equal, only the identifier matters"""
        identifier = "1"
        self.assertEqual(
            Player(identifier),
            Player(
                identifier,
                {RoundRole.DEALER},
                hand=[Card(CardNumber.ACE, SelectableSuit.CLUBS)],
            ),
        )
        self.assertNotEqual(Player("one"), Player("two"))
