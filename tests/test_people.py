'''Unit test common interactions with a list of persons'''
from unittest import TestCase

from hundred_and_ten import people
from hundred_and_ten.constants import GameRole
from hundred_and_ten.person import Person


class TestPeople(TestCase):
    '''People unit tests'''

    def test_upsert_person_not_in_list(self):
        '''Upsert a person that is not in the list'''

        person = Person('1')
        persons = []
        new_list = people.upsert(persons, person)

        self.assertEqual(len(persons) + 1, len(new_list))
        self.assertIn(person, new_list)

    def test_upsert_person_in_list(self):
        '''Upsert a person that is in the list'''

        person = Person('1')
        persons = [person]
        new_list = people.upsert(persons, person)

        self.assertEqual(len(persons), len(new_list))
        self.assertIn(person, new_list)

    def test_upsert_person_in_list_with_no_roles(self):
        '''Upsert a person that is in the list but has no roles'''

        identifier = '1'
        person = Person(identifier)
        person_with_roles = Person(identifier, {GameRole.ORGANIZER})
        persons = [person]
        new_list = people.upsert(persons, person_with_roles)

        self.assertEqual(len(persons), len(new_list))
        self.assertEqual(new_list[0], person_with_roles)
        self.assertEqual({GameRole.ORGANIZER}, new_list[0].roles)

    def test_upsert_person_in_list_with_different_roles(self):
        '''Upsert a person that is in the list but has different roles'''

        identifier = '1'
        person_player = Person(identifier, {GameRole.PLAYER})
        person_invitee = Person(identifier, {GameRole.INVITEE})
        persons = [person_player]
        new_list = people.upsert(persons, person_invitee)

        self.assertEqual(len(persons), len(new_list))
        self.assertEqual(new_list[0], person_invitee)
        self.assertEqual({GameRole.INVITEE}, new_list[0].roles)

    def test_upsert_person_maintains_position(self):
        '''Upsert a person that is not in the list'''

        identifier = 'p'
        person = Person(identifier)
        new_person = Person(identifier, {GameRole.ORGANIZER})
        persons = [Person('1'), person, Person('2')]
        new_list = people.upsert(persons, new_person)

        self.assertEqual(len(persons), len(new_list))
        self.assertEqual(persons.index(person), new_list.index(new_person))
