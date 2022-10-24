'''Provide a class to keep track person information'''
from dataclasses import dataclass
from typing import Optional

from hundred_and_ten.constants import AnyRole


@dataclass
class Person:
    '''A class to keep track of person information'''

    def __init__(self, identifier: str, roles: Optional[set[AnyRole]] = None):
        self.identifier = identifier
        self.roles = roles or set()