from .Command import Command

class LogHoursCommand(Command):
    def __init__(self, staff, request):
        super().__init__()
        self.actor = staff
        self.target = request

    def execute(self):
        self.actor.approve_request(self.hours)
    

    def description(self):
        return f"{self.staff.username} logged {self.target.hours} hours for Student ID{self.target.student_id}"