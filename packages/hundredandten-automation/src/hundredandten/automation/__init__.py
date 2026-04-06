"""Init the automation module"""

from .naive import action_for as naive_action_for
from .state import GameState

__all__ = ["GameState", "naive_action_for"]
