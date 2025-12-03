from App.models import Student, Staff, Request, db
from App.commands.LogHoursCommand import LogHoursCommand
from App.commands.DenyRequestCommand import DenyRequestCommand
from App.commands.AccoladeCommand import AccoladeCommand
from .activity_log import ActivityLog
from App.models.activity_history import ActivityHistory 


class StaffService():
    """Invoker: Handles staff-triggered actions by executing Commands."""
    
    @staticmethod
    def approve_request_action(staff_id: int, request_id: int):
        """Action that triggers the LogHoursCommand."""
        staff = Staff.query.get(staff_id)
        request = Request.query.get(request_id)
        student = Student.query.get(request.student_id)
        
        if not staff or not request:
            return None, "Staff or Request not found."
            
        # 1. Client creates and configures the Command
        command = LogHoursCommand(request, staff)
        
        # 2. Invoker calls execute()
        new_logged = command.execute()
        
    
        ActivityLog.log_command_execution(command, request.student_id)


          # 3. Invoker creates and executes the Accolade Command
        #    This checks if the new loggedhours makes the student eligible for a milestone
        accolade_command = AccoladeCommand(student)
        accolade_success = accolade_command.execute() 

        # 4. Invoker logs the Accolade Command execution if successful
        if accolade_success:
             ActivityLog.log_command_execution(accolade_command, student.student_id, staff_id) 

        return new_logged

    @staticmethod
    def deny_request_action(staff_id: int, request_id: int):
        """Action that triggers the DenyRequestCommand."""
        
        # 1. Invoker fetches necessary models (Client/Context/Data)
        staff = Staff.query.get(staff_id)
        request = Request.query.get(request_id)
        
        if not staff:
            return None, "Error: Staff member not found."
        if not request:
            return None, "Error: Request not found."
        
        # 2. Invoker creates and configures the Command
        command = DenyRequestCommand(request=request, staff=staff)
        
        # 3. Invoker calls execute()
        success = command.execute()
        
        if success:
            # 4. Invoker logs the command execution (Fulfills history feature)
            ActivityLog.log_command_execution(command, request.student_id, staff_id)
            return True, "Request denied successfully."
        else:
            # Handle cases where the command failed 
            return False, "Request could not be denied (status was not pending)."
