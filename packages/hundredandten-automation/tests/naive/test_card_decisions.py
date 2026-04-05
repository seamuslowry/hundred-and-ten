"""Test to ensure card decisions are made consistently"""

from unittest import TestCase

from hundredandten.automation.naive import best_card, worst_card, worst_card_beating
from hundredandten.engine.constants import CardNumber, CardSuit, SelectableSuit
from hundredandten.engine.deck import Card


class TestCardDecisions(TestCase):
    """Unit tests for deciding on card value"""

    def test_finds_best_card(self):
        """Finds the highest value trump as the best card"""
        suit = SelectableSuit.CLUBS
        card = Card(CardNumber.FIVE, CardSuit[suit.name])
        self.assertEqual(
            card,
            best_card(
                [
                    Card(CardNumber.FIVE, CardSuit.DIAMONDS),
                    card,
                    Card(CardNumber.ACE, CardSuit[suit.name]),
                ],
                suit,
            ),
        )

    def test_finds_best_card_as_joker(self):
        """Finds the joker as the best card with no trumps"""
        suit = SelectableSuit.HEARTS
        card = Card(CardNumber.JOKER, CardSuit.JOKER)
        self.assertEqual(
            card,
            best_card(
                [
                    Card(CardNumber.FIVE, CardSuit.DIAMONDS),
                    card,
                    Card(CardNumber.ACE, CardSuit.CLUBS),
                ],
                suit,
            ),
        )

    def test_finds_worst_card_with_trumps(self):
        """Finds the lowest value non trump as the worst card"""
        card = Card(CardNumber.TWO, CardSuit.DIAMONDS)
        self.assertEqual(
            card,
            worst_card(
                [
                    Card(CardNumber.FIVE, CardSuit.SPADES),
                    card,
                    Card(CardNumber.ACE, CardSuit.CLUBS),
                ],
                SelectableSuit.CLUBS,
            ),
        )

    def test_finds_worst_card_with_only_trumps(self):
        """Finds the lowest value trump as the worst card"""
        suit = SelectableSuit.DIAMONDS
        card = Card(CardNumber.TWO, CardSuit[suit.name])
        self.assertEqual(
            card,
            worst_card(
                [
                    Card(CardNumber.FIVE, CardSuit[suit.name]),
                    card,
                    Card(CardNumber.ACE, CardSuit[suit.name]),
                ],
                SelectableSuit.DIAMONDS,
            ),
        )

    def test_finds_worst_card_beating(self):
        """Finds the lowest value card that beats the provided card with all trump"""
        suit = SelectableSuit.DIAMONDS
        card_to_beat = Card(CardNumber.TWO, CardSuit[suit.name])
        card = Card(CardNumber.ACE, CardSuit[suit.name])
        self.assertEqual(
            card,
            worst_card_beating(
                [
                    Card(CardNumber.FIVE, CardSuit[suit.name]),
                    Card(CardNumber.JACK, CardSuit[suit.name]),
                    card,
                ],
                card_to_beat,
                suit,
            ),
        )

    def test_finds_worst_card_beating_non_trump(self):
        """Finds the lowest value card that beats the provided card with all trump"""
        trump = SelectableSuit.DIAMONDS
        card_to_beat = Card(CardNumber.THREE, CardSuit.SPADES)
        card = Card(CardNumber.TWO, CardSuit.SPADES)
        self.assertEqual(
            card,
            worst_card_beating(
                [
                    Card(CardNumber.FIVE, CardSuit[trump.name]),
                    Card(CardNumber.JACK, CardSuit[trump.name]),
                    card,
                ],
                card_to_beat,
                trump,
            ),
        )
