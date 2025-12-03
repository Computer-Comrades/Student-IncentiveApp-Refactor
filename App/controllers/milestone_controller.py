from App.database import db
from App.models import Student
from App.models import Staff
from App.models import Milestone
from App.models import StudentMilestone

class MilestoneController():
    """Service to handle milestone awarding and retrieval."""

    @staticmethod
    def create_milestone(name: str, required_hours: float, description: str = None):
        """Creates a new milestone in the system."""
        
        milestone = Milestone(name=name, required_hours=required_hours, description=description)
        db.session.add(milestone)
        db.session.commit()
        return milestone


    @staticmethod
    def award_milestone(student: Student, milestone: Milestone):
        """Awards a milestone to a student."""
        
        # Check if the student already has the milestone
        existing = StudentMilestone.query.filter_by(
            student_id=student.student_id,
            milestone_id=milestone.id
        ).first()
        
        if existing:
            raise ValueError(f"Student {student.username} already has the milestone '{milestone.name}'.")

        # Create a new StudentMilestone entry
        student_milestone = StudentMilestone(
            milestone_id=milestone.id,
            student_id=student.student_id
        )
        db.session.add(student_milestone)
        db.session.commit()


    @staticmethod
    def get_student_milestones(student: Student):
        """Retrieves all milestones awarded to a student."""
        
        milestones = db.session.query(Milestone).join(StudentMilestone).filter(
            StudentMilestone.student_id == student.student_id
        ).all()
        
        return milestones

    @staticmethod
    def get_student_milestone_details(student: Student):
        """Retrieves detailed information about milestones awarded to a student."""
        
        details = db.session.query(StudentMilestone).join(Milestone).filter(
            StudentMilestone.student_id == student.student_id
        ).all()
        
        return details