from App.models import Student, Staff, Request, db
from App.commands.log_hours_command import LogHoursCommand
from .activity_history import ActivityLog

class StaffService():
    """Invoker: Handles staff-triggered actions by executing Commands."""
    
    @staticmethod
    def approve_request_action(staff_id: int, request_id: int):
        """Action that triggers the LogHoursCommand."""
        staff = Staff.query.get(staff_id)
        request = Request.query.get(request_id)
        
        if not staff or not request:
            return None, "Staff or Request not found."
            
        # 1. Client creates and configures the Command
        command = LogHoursCommand(request=request, staff=staff)
        
        # 2. Invoker calls execute()
        success = command.execute()
        
        if success:
            # 3. Invoker logs the command execution (Fulfills history feature)
            ActivityLog.log_command_execution(command, request.student_id)
            return True, "Request approved and hours logged successfully."
        else:
            return False, "Request could not be approved."

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
            ActivityLog.log_command_execution(command, request.student_id, staff_id=staff.staff_id)
            return True, "Request denied successfully."
        else:
            # Handle cases where the command failed (e.g., request was not pending)
            return False, "Request could not be denied (status was not pending)."