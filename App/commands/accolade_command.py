from App.models import Student, ActivityHistory, db  # Import ActivityHistory
from .Command import Command

class AccoladeCommand(Command):
    
    def __init__(self, student: Student):
        self.student = student
        self.accolades_awarded = [] 
        
    def _get_logged_milestones(self):
        """Internal utility: Queries ActivityHistory to find previously awarded milestones."""
        
        awarded_records = ActivityHistory.query.filter_by(
            student_id=self.student.student_id,
            command_type='AccoladeCommand'
        ).all()
        
        # Building a set of unique milestone names found in the history descriptions
        logged_names = set()
        for record in awarded_records:
            if '10 Hours Milestone' in record.description:
                logged_names.add('10 Hours Milestone')
            if '25 Hours Milestone' in record.description:
                logged_names.add('25 Hours Milestone')
            if '50 Hours Milestone' in record.description:
                logged_names.add('50 Hours Milestone')
        
        return logged_names

    def _calculate_accolades(self):
        """Internal method to calculate all achievable milestones based on current hours."""
        total_hours = self.student.get_total_approved_hours()
        achievable_milestones = []
        
        if total_hours >= 10:
            achievable_milestones.append('10 Hours Milestone')
        if total_hours >= 25:
            achievable_milestones.append('25 Hours Milestone')
        if total_hours >= 50:
            achievable_milestones.append('50 Hours Milestone')
            
        return achievable_milestones

    def execute(self):
        """Checks the student's hours, awards new milestones, and prepares for logging."""
        
        # Get current achievable milestones
        achievable = self._calculate_accolades()
        
        # Get milestones already logged in history 
        logged = self._get_logged_milestones()
        
        # Determine which milestones are achieved but logged
        newly_awarded = [m for m in achievable if m not in logged]
        
        self.accolades_awarded = newly_awarded
        
        if self.accolades_awarded:
            # Command succeeded in finding new awards
            return True
            
        return False

    def get_description(self):
        """Returns the description that the ActivityLog will save."""
        if self.accolades_awarded:
            # Ensure the milestone names are in the description for future history checks
            return f"Accolades awarded: {', '.join(self.accolades_awarded)}."
        return f"Accolade check run. No new milestones achieved."