from App.models import Student, db
from App.commands.RequestCommand import RequestCommand
from App.controllers.activity_log import ActivityLog
from App.models.activity_history import ActivityHistory 

class StudentService():
    """Invoker and Query Layer for student-related features."""
    
    @staticmethod
    def create_hours_request(student_id: int, hours: float):
        """Invoker action: Creates and executes the RequestConfirmationCommand."""
        student = Student.query.get(student_id)
        
        if not student:
            return None, "Student not found."
            
        # 1. Invoker creates and executes Command
        command = RequestCommand(student=student, hours=hours)
        new_request = command.execute()
        
        # 2. Invoker logs the command execution 
        ActivityLog.log_command_execution(command, student_id, staff_id=None) 
        
        return new_request
    #, "Request submitted successfully. Accolade check run."
        
        #
    @staticmethod
    def view_activity_history(student_id: int):
        """Queries the ActivityHistory log for the student."""
        # Fulfills the special feature requirement 
        history_records = ActivityHistory.query.filter_by(student_id=student_id).order_by(ActivityHistory.timestamp.desc()).all()
        
        return [record.get_json() for record in history_records]

    @staticmethod
    def view_accolades(student_id: int):
        """Queries the ActivityHistory via ActivityLog to return a list of awarded accolades."""
        student = Student.query.get(student_id)
        if not student:
            return []
        
        # The Invoker calls the ActivityLog to retrieve the data
        return ActivityLog.view_accolades_data(student)
    
            
