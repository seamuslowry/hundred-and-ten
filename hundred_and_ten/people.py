'''Interact with a list of people'''

from typing import Optional

from hundred_and_ten.constants import AnyRole
from hundred_and_ten.person import Person


def by_identifier(people: list[Person], identifier: str) -> Optional[Person]:
    '''
    Find a person with the given identifier
    '''
    return next(iter([p for p in people if p.identifier == identifier]), None)


def by_role(people: list[Person], role: str) -> list[Person]:
    '''
    Find a person with the given identifier
    '''
    return [p for p in people if role in p.roles] or []


def find_or_create(people: list[Person], identifier: str, role: Optional[AnyRole] = None) -> Person:
    '''
    Find or create a person with the given attributes
    Provided role will append, not overwrite
    '''
    person = by_identifier(people, identifier) or Person(identifier=identifier)
    if role is not None:
        person.roles.add(role)
    return person


def add_role(people: list[Person], identifier: str, role: AnyRole) -> list[Person]:
    '''
    Add the provided role to the person with the given identifier
    '''
    person = find_or_create(people, identifier, role)
    return upsert(people, person)


def upsert(people: list[Person], person: Person) -> list[Person]:
    '''
    Upsert the provided person into the people array
    '''
    return [p for p in people if p.identifier != person.identifier] + [person]
