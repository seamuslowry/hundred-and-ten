'''Provide a class to keep track person information'''
from dataclasses import dataclass


@dataclass
class Person:
    '''A class to keep track of person information'''

    def __init__(self, identifier: str, roles=None):
        self.identifier = identifier
        self.roles = roles or set()
