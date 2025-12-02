from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract Base Class for the Command interface."""
    
    @abstractmethod
    def execute(self):
        """Method to execute the encapsulated request."""
        pass

    @abstractmethod
    def get_description(self):
        """Method to return a description for activity logging."""
        pass