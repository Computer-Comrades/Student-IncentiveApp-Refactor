from App.models import Student, Staff, Request, LoggedHours, db
from .command_interface import Command

class LogHoursCommand(Command):
    
    def __init__(self, request: Request, staff: Staff):
        self.request = request
        self.staff = staff
        self.student = Student.query.get(request.student_id)
        
    def execute(self):
        if self.request.status != 'pending':
            print("Error: Request is not pending.")
            return False
        
        # 1. Update Request (Receiver)
        self.request.status = 'approved'
        
        # 2. Create LoggedHours Entry (Receiver)
        logged = LoggedHours(
            student_id=self.request.student_id, 
            staff_id=self.staff.staff_id, 
            hours=self.request.hours, 
            status='approved'
        )
        db.session.add(logged)
        
        # 3. Commit the transaction
        db.session.commit()
        return True

    def get_description(self):
        return f"Approved {self.request.hours} hours for Student {self.student.username} (Request {self.request.id})"

# Note: You would also need a DenyRequestCommand and a RequestConfirmationCommand