'''Unit test determining the next person within a list of players'''
from unittest import TestCase

from hundredandten.group import Group, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError


class TestNextPlay(TestCase):
    '''Next Player unit tests'''

    def test_after_with_no_players(self):
        '''Finds no player in empty list'''

        players = Group([])

        self.assertRaises(HundredAndTenError, players.after, 'any')

    def test_after_with_unknown_player(self):
        '''Finds no player when not in list'''

        players = Group([Player('1')])

        self.assertRaises(HundredAndTenError, players.after, players[0].identifier + 'bad')

    def test_after_with_one_player(self):
        '''Determines the next player in a list of 1'''

        person_one = Player('1')
        players = Group([person_one])

        self.assertEqual(person_one, players.after(person_one.identifier))

    def test_after_with_two_players(self):
        '''Determines the next player in a list of 2'''

        person_one = Player('1')
        person_two = Player('2')
        players = Group([person_one, person_two])

        self.assertEqual(person_two, players.after(person_one.identifier))
        self.assertEqual(person_one, players.after(person_two.identifier))

    def test_after_with_three_players(self):
        '''Determines the next player in a list of 3'''

        person_one = Player('1')
        person_two = Player('2')
        person_three = Player('3')

        players = Group([person_one, person_two, person_three])

        self.assertEqual(person_two, players.after(person_one.identifier))
        self.assertEqual(person_three, players.after(person_two.identifier))
        self.assertEqual(person_one, players.after(person_three.identifier))

    def test_after_with_four_players(self):
        '''Determines the next player in a list of 4'''

        person_one = Player('1')
        person_two = Player('2')
        person_three = Player('3')
        person_four = Player('4')

        players = Group([person_one, person_two, person_three, person_four])

        self.assertEqual(person_two, players.after(person_one.identifier))
        self.assertEqual(person_three, players.after(person_two.identifier))
        self.assertEqual(person_four, players.after(person_three.identifier))
        self.assertEqual(person_one, players.after(person_four.identifier))
