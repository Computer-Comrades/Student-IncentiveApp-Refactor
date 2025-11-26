from App.database import db

class ActivityHistory(db.Model):
    """Stores a persistent record of every executed command."""
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    
    # Store key details of the executed command
    command_type = db.Column(db.String(50), nullable=False) 
    description = db.Column(db.String(255), nullable=False) 
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True) 

    def get_json(self):
        return {
            'timestamp': str(self.timestamp),
            'action': self.description,
            'command_type': self.command_type
        }