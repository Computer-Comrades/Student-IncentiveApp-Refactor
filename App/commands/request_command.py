from App.models import Student, Request, db
from .command_interface import Command 

class RequestCommand(Command):
    
    def __init__(self, student: Student, hours: float):
        """Configures the command with the student (Receiver data) and parameters."""
        self.student = student
        self.hours = hours
        
    def execute(self):
        """Creates a new pending Request entry."""
        # This is the encapsulated business logic
        request = Request(
            student_id=self.student.student_id, 
            hours=self.hours, 
            status='pending'
        )
        db.session.add(request)
        db.session.commit()
        return request

    def get_description(self):
        return f"Student {self.student.username} requested confirmation for {self.hours} hours."