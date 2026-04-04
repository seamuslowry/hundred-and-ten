"""Person unit tests"""

from unittest import TestCase

from hundredandten.constants import CardNumber, CardSuit, RoundRole
from hundredandten.deck import Card
from hundredandten.player import HumanPlayer, RoundPlayer


class TestPlayer(TestCase):
    """Player unit tests"""

    def test_round_players_equal_by_identifier_only(self):
        """When checking if round players are equal, only the identifier matters"""
        identifier = "1"
        self.assertEqual(
            RoundPlayer(identifier),
            RoundPlayer(
                identifier,
                roles={RoundRole.DEALER},
                hand=[Card(CardNumber.ACE, CardSuit.CLUBS)],
            ),
        )
        self.assertNotEqual(HumanPlayer("one"), HumanPlayer("two"))
