from App.database import db

class StudentMilestone(db.Model):
    __tablename__ = 'student_milestone'
    
    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    achieved_on = db.Column(db.DateTime, default=db.func.current_timestamp())

    #relationships
    student = db.relationship('Student', backref=db.backref('student_milestones', lazy=True, cascade="all, delete-orphan"))
    milestone = db.relationship('Milestone', backref=db.backref('milestone_students', lazy=True))

    def __init__(self, milestone_id, student_id):
        self.milestone_id = milestone_id
        self.student_id = student_id

    def __repr__(self):
        return f"[Student ID={self.student_id} Milestone ID={self.milestone_id} Achieved On={self.achieved_on}]"
    
    def get_json(self):
        return {
            'id': self.id,
            'milestone_id': self.milestone_id,
            'milestone_name': self.milestone.name if self.milestone else None,
            'student_id': self.student_id,
            'student_name': self.student.username if self.student else None,
            'achieved_on': self.achieved_on.strftime("%Y-%m-%d %H:%M:%S")
        }
