'''Test behavior of the deck'''
from unittest import TestCase

from hundredandten.deck import Deck
from hundredandten.hundred_and_ten_error import HundredAndTenError


class TestDeck(TestCase):
    '''Unit tests for a deck'''

    def test_shuffling_without_seed(self):
        '''Shuffling without the same seed is always different'''

        deck_1 = Deck()
        deck_2 = Deck()

        self.assertNotEqual(deck_1.cards, deck_2.cards)

    def test_shuffling_with_seed(self):
        '''Shuffling with the correct seed is always the same'''
        seed = 'test seed'

        deck_1 = Deck(seed)
        deck_2 = Deck(seed)

        self.assertEqual(deck_1.cards, deck_2.cards)

    def test_draw(self):
        '''Drawing returns requested cards'''

        deck = Deck()
        amt = 5
        first_hand = deck.draw(amt)
        second_hand = deck.draw(amt)

        self.assertNotEqual(first_hand, second_hand)
        self.assertEqual(amt*2, deck.pulled)

    def test_massive_overdraw(self):
        '''Drawing past the whole deck at once returns an error'''

        deck = Deck()

        self.assertRaises(HundredAndTenError, deck.draw, 54)

    def test_overdraw(self):
        '''Drawing past the whole deck returns an error'''

        deck = Deck()

        deck.draw(53)
        self.assertRaises(HundredAndTenError, deck.draw, 1)

    def test_underdraw(self):
        '''Trying to draw drawn cards returns an error'''

        deck = Deck()

        self.assertRaises(HundredAndTenError, deck.draw, -1)
