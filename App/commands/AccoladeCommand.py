from .Command import Command

class AccoladeCommand(Command):
    def __init__(self, student, accolade):
        super().__init__()
        self.actor = student
        self.target = accolade

    def execute(self):
        self.actor.request_hours_confirmation(self.target)
     

    def description(self):
        return f"{self.actor.username} achieved {self.target.name}"