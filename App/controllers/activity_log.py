from App.database import db
from App.models import Student
from App.models.activity_history import ActivityHistory
from App.commands.command_interface import Command

class ActivityLog():
    """Service to handle activity logging and achievement viewing."""

    @staticmethod
    def log_command_execution(command: Command, student_id: int, staff_id: int = None):
        """Logs the successful execution of any command to the ActivityHistory model."""
        
        log_entry = ActivityHistory(
            student_id,
            command.__class__.__name__,
            command.get_description(),
            staff_id                    # Will be None for student made reuests or accolade checks
        )
        db.session.add(log_entry)
        db.session.commit()

    @staticmethod
    def view_accolades_data(student: Student):
        """Queries ActivityHistory to return a list of previously awarded accolades."""
        
        awarded_records = ActivityHistory.query.filter_by(
            student_id=student.student_id,
            command_type='AccoladeCommand'
        ).all()
        
        awarded_names = set()
        for record in awarded_records:
            # Parse the description saved by the AccoladeCommand
            if 'Accolades awarded' in record.description:
                # Simple extraction
                parts = record.description.split(':')
                if len(parts) > 1:
                    for milestone in parts[1].split(','):
                        awarded_names.add(milestone.strip())
        
        return sorted(list(awarded_names))