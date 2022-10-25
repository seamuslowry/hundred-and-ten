'''Person unit tests'''
from unittest import TestCase

from hundred_and_ten.constants import GameRole
from hundred_and_ten.person import Person


class TestPerson(TestCase):
    '''Person unit tests'''

    def test_persons_equal_by_identifier_only(self):
        '''When checking if persons are equal, only the identifier matters'''
        identifier = "1"
        self.assertEqual(Person(identifier), Person(identifier, {GameRole.INVITEE}))
        self.assertNotEqual(Person('one'), Person('two'))

    def test_persons_hash_by_identifier_only(self):
        '''When hashing a person, only the identifier matters'''
        identifier = "1"
        self.assertEqual(hash(Person(identifier)), hash(Person(identifier, {GameRole.INVITEE})))
        self.assertNotEqual(hash(Person('one')), hash(Person('two')))
