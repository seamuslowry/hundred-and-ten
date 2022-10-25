'''Unit test common interactions with a list of persons'''
from unittest import TestCase

from hundred_and_ten.constants import GameRole
from hundred_and_ten.people import People
from hundred_and_ten.person import Person


class TestPeople(TestCase):
    '''People unit tests'''

    def test_upsert_person_not_in_list(self):
        '''Upsert a person that is not in the list'''

        person = Person('1')
        persons = People()

        pre_len = len(persons)

        persons.upsert(person)

        self.assertEqual(pre_len + 1, len(persons))
        self.assertIn(person, persons)

    def test_upsert_person_in_list(self):
        '''Upsert a person that is in the list'''

        person = Person('1')
        persons = People([person])

        pre_len = len(persons)

        persons.upsert(person)

        self.assertEqual(pre_len, len(persons))
        self.assertIn(person, persons)

    def test_upsert_person_in_list_with_no_roles(self):
        '''Upsert a person that is in the list but has no roles'''

        identifier = '1'
        person = Person(identifier)
        person_with_roles = Person(identifier, {GameRole.ORGANIZER})
        persons = People([person])

        pre_len = len(persons)

        persons.upsert(person_with_roles)

        self.assertEqual(pre_len, len(persons))
        self.assertEqual(persons[0], person_with_roles)
        self.assertEqual({GameRole.ORGANIZER}, persons[0].roles)

    def test_upsert_person_in_list_with_different_roles(self):
        '''Upsert a person that is in the list but has different roles'''

        identifier = '1'
        person_player = Person(identifier, {GameRole.PLAYER})
        person_invitee = Person(identifier, {GameRole.INVITEE})
        persons = People([person_player])

        pre_len = len(persons)

        persons.upsert(person_invitee)

        self.assertEqual(pre_len, len(persons))
        self.assertEqual(persons[0], person_invitee)
        self.assertEqual({GameRole.INVITEE}, persons[0].roles)

    def test_upsert_person_maintains_position(self):
        '''Upsert a person that is not in the list'''

        identifier = 'p'
        person = Person(identifier)
        new_person = Person(identifier, {GameRole.ORGANIZER})
        persons = People([Person('1'), person, Person('2')])
        pre_len = len(persons)
        pre_index = persons.index(person)

        persons.upsert(new_person)

        self.assertEqual(pre_len, len(persons))
        self.assertEqual(pre_index, persons.index(new_person))
