'''Interact with a list of people'''

from typing import Optional

from hundred_and_ten.constants import AnyRole
from hundred_and_ten.person import Person


class People(list[Person]):
    '''A list of persons'''

    def update(self, person: Person) -> None:
        '''
        Update the provided person within people
        Will raise an erro if the person is not in people already
        '''
        index = self.index(person)
        self[index] = person

    def upsert(self, person: Person) -> None:
        '''
        Upsert the provided person into people
        '''
        if person in self:
            self.update(person)
        else:
            self.append(person)

    def by_identifier(self, identifier: str) -> Optional[Person]:
        '''
        Find a person with the given identifier
        '''
        return next(iter([p for p in self if p.identifier == identifier]), None)

    def by_role(self, role: AnyRole) -> 'People':
        '''
        Find a person with the given identifier
        '''
        return People([p for p in self if role in p.roles] or [])

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

    def add_role(self, identifier: str, role: AnyRole) -> None:
        '''
        Add the provided role to the person with the given identifier
        '''
        person = self.by_identifier(identifier)
        if person:
            self.update(Person(person.identifier, person.roles.union({role})))

    def remove_role(self, identifier: str, role: AnyRole) -> None:
        '''
        Remove the provided role from the person with the given identifier
        '''
        person = self.by_identifier(identifier)
        if person:
            self.update(Person(person.identifier, person.roles.difference({role})))

    def swap_role(self, source_identifier: str, dest_identifier: str, role: AnyRole) -> None:
        '''
        Swap a role from the source identifier to the destination identifier
        '''
        self.remove_role(source_identifier, role)
        self.add_role(dest_identifier, role)

    def after(self, identifier: str) -> Optional[Person]:
        '''
        Determine the next player after the identified one
        '''
        person = self.by_identifier(identifier)
        if not self or not person:
            return None
        return self[(self.index(person) + 1) % len(self)]
