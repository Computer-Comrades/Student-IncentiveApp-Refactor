from App.database import db
from App.models import Student
from App.models import Staff
from App.models import Accolade
from App.models import StudentAccolade

class AccoladeController():
    """Service to handle accolade awarding and retrieval."""

    @staticmethod
    def create_accolade(name: str):
        """Creates a new accolade in the system."""
        
        accolade = Accolade(name=name)
        db.session.add(accolade)
        db.session.commit()
        return accolade

    @staticmethod
    def award_accolade(student: Student, accolade: Accolade, staff: Staff = None, description: str = None):
        """Awards an accolade to a student and records the awarding staff if applicable."""
        
        # Check if the student already has the accolade
        existing = StudentAccolade.query.filter_by(
            student_id=student.student_id,
            accolade_id=accolade.id
        ).first()
        
        if existing:
            raise ValueError(f"Student {student.username} already has the accolade '{accolade.name}'.")

        # Create a new StudentAccolade entry
        student_accolade = StudentAccolade(
            student_id=student.student_id,
            accolade_id=accolade.id,
            staff_id=staff.staff_id if staff else None,
            description=description 
        )
        db.session.add(student_accolade)
        db.session.commit()

    @staticmethod
    def get_student_accolades(student: Student):
        """Retrieves all accolades awarded to a student."""
        
        accolades = db.session.query(Accolade).join(StudentAccolade).filter(
            StudentAccolade.student_id == student.student_id
        ).all()
        
        return accolades
    
    @staticmethod
    def get_student_accolade_details(student: Student):
        """Retrieves detailed information about accolades awarded to a student."""
        
        details = db.session.query(StudentAccolade).join(Accolade).filter(
            StudentAccolade.student_id == student.student_id
        ).all()
        
        return details

    
    @staticmethod
    def get_all_accolades():
        """Retrieves all available accolades in the system."""
        
        accolades = Accolade.query.all()
        return accolades
    
