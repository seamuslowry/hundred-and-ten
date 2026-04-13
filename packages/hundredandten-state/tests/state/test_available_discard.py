"""Tests for AvailableDiscard equality and hashing"""

from unittest import TestCase

from hundredandten.deck import Card, CardNumber, CardSuit
from hundredandten.state import AvailableDiscard

ACE_HEARTS = Card(CardNumber.ACE, CardSuit.HEARTS)
FIVE_SPADES = Card(CardNumber.FIVE, CardSuit.SPADES)
TEN_CLUBS = Card(CardNumber.TEN, CardSuit.CLUBS)


class TestAvailableDiscardEquality(TestCase):
    """AvailableDiscard equality is order-insensitive"""

    def test_equal_same_order(self):
        """Identical card tuples are equal"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        self.assertEqual(a, b)

    def test_equal_different_order(self):
        """Same cards in different order are equal"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((FIVE_SPADES, ACE_HEARTS))
        self.assertEqual(a, b)

    def test_not_equal_different_cards(self):
        """Different card sets are not equal"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((ACE_HEARTS, TEN_CLUBS))
        self.assertNotEqual(a, b)

    def test_not_equal_different_lengths(self):
        """Different card counts are not equal"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((ACE_HEARTS,))
        self.assertNotEqual(a, b)

    def test_not_equal_to_non_discard(self):
        """Comparison to a non-AvailableDiscard returns NotImplemented"""
        a = AvailableDiscard((ACE_HEARTS,))
        self.assertNotEqual(a, (ACE_HEARTS,))

    def test_empty_equal(self):
        """Two empty AvailableDiscards are equal"""
        self.assertEqual(AvailableDiscard(()), AvailableDiscard(()))


class TestAvailableDiscardHash(TestCase):
    """AvailableDiscard hash is order-insensitive"""

    def test_hash_equal_same_order(self):
        """Same cards in same order have equal hashes"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        self.assertEqual(hash(a), hash(b))

    def test_hash_equal_different_order(self):
        """Same cards in different order have equal hashes"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((FIVE_SPADES, ACE_HEARTS))
        self.assertEqual(hash(a), hash(b))

    def test_usable_in_set(self):
        """AvailableDiscard instances with same cards collapse to one set entry"""
        a = AvailableDiscard((ACE_HEARTS, FIVE_SPADES))
        b = AvailableDiscard((FIVE_SPADES, ACE_HEARTS))
        self.assertEqual(len({a, b}), 1)
