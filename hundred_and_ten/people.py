'''Interact with a list of people'''

from typing import Optional

from hundred_and_ten.constants import AnyRole
from hundred_and_ten.person import Person


class People(list[Person]):
    '''A list of persons'''

    def upsert(self, person: Person):
        '''
        Upsert the provided person into the people array
        '''
        if person in self:
            index = self.index(person)
            self[index] = person
        else:
            self.append(person)

    def by_identifier(self, identifier: str) -> Optional[Person]:
        '''
        Find a person with the given identifier
        '''
        return next(iter([p for p in self if p.identifier == identifier]), None)

    def by_role(self, role: AnyRole) -> list[Person]:
        '''
        Find a person with the given identifier
        '''
        return [p for p in self if role in p.roles] or []

    def find_or_create(
            self,
            identifier: str, role: Optional[AnyRole] = None) -> Person:
        '''
        Find or create a person with the given attributes
        Provided role will append, not overwrite
        '''
        person = self.by_identifier(identifier) or Person(identifier=identifier)
        roles = person.roles.union({role}) if role else person.roles
        return Person(person.identifier, roles)

    def add_role(self, identifier: str, role: AnyRole):
        '''
        Add the provided role to the person with the given identifier
        '''
        person = self.find_or_create(identifier, role)
        self.upsert(person)
