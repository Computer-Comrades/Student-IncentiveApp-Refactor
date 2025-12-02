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

    def __repr__(self):
        return f"[Activity ID = {str(self.id)}    Timestamp = {str(self.timestamp)}   Command Type = {self.command_type}   Description = {self.description}   Student ID = {str(self.student_id):<3}   Staff ID = {str(self.staff_id):<3}]"

    def get_json(self):
        return {
            'timestamp': str(self.timestamp),
            'action': self.description,
            'command_type': self.command_type
        }