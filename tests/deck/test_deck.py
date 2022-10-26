'''Test behavior of the deck'''
from random import Random
from unittest import TestCase


def deck():
    '''return a range of ints representing a deck'''
    return [*range(53)]


class TestDeck(TestCase):
    '''Unit tests for a deck'''

    def test_shuffling_without_seed(self):
        '''Shuffling without the correct seed is always different'''
        seed = 'test seed'

        deck_1 = deck()
        deck_2 = deck()
        Random().shuffle(deck_1)
        Random().shuffle(deck_2)

        self.assertNotEqual(deck_1, deck_2)

        deck_3 = deck()
        deck_4 = deck()
        Random(seed).shuffle(deck_3)
        Random(seed).shuffle(deck_4)

        self.assertEqual(deck_3, deck_4)

    def test_shuffling_with_seed(self):
        '''Shuffling with the correct seed is always the same'''
        seed = 'test seed'

        deck_1 = deck()
        deck_2 = deck()
        Random(seed).shuffle(deck_1)
        Random(seed).shuffle(deck_2)

        self.assertEqual(deck_1, deck_2)
