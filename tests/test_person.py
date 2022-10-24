'''Person unit tests'''
from unittest import TestCase

from hundred_and_ten.constants import PersonRole
from hundred_and_ten.person import Person


class TestPerson(TestCase):
    '''Person unit tests'''

    def test_persons_equal_by_identifier_only(self):
        '''When checking if persons are equal, only the identifier matters'''
        identifier = "1"
        self.assertEqual(Person(identifier), Person(identifier, {PersonRole.INVITEE}))
