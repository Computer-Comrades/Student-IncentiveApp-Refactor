from App.models import Request, Staff, db
from .Command import Command

class DenyRequestCommand(Command):
    
    def __init__(self, request: Request, staff: Staff):
        """Configures the command with the request (data) and staff (context)."""
        self.request = request
        self.staff = staff
        
    def execute(self):
        """Marks a pending request as denied."""
        if self.request.status != 'pending':
            return False
        
        self.request.status = 'denied'
        db.session.commit()
        return True

    def get_description(self):
        return (f"Staff {self.staff.username} denied request {self.request.id} "
                f"for {self.request.hours} hours.")