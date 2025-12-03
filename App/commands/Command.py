from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract Base class for all commands in the incentive app."""

    def __init__(self, actor=None, target=None):
        # actor = person doing the action (student or staff)
        # target = object of the action (e.g., request, logged hours)
        self.actor = actor
        self.target = target
        self.result = None

    @abstractmethod
    def execute(self):
        # carry out a command
        pass

    @abstractmethod
    def get_description(self) -> str:
        # return a simple text description
        pass

    def can_execute(self) -> bool:
        # test to see if the command works
        return True
