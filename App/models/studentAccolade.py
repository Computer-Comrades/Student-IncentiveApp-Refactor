from App.database import db

class StudentAccolade(db.Model):
    __tablename__ = 'student_accolade'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    accolade_id = db.Column(db.Integer, db.ForeignKey('accolade.id'), nullable=False)
    date_awarded = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.String(255), nullable=True)

    #relationships
    student = db.relationship('Student', backref=db.backref('student_accolades', lazy=True))
    staff = db.relationship('Staff', backref=db.backref('staff_accolades', lazy=True))
    accolade = db.relationship('Accolade', backref=db.backref('accolade_students', lazy=True))

    def __init__(self, student_id, staff_id, accolade_id, description):
        self.student_id = student_id
        self.staff_id = staff_id
        self.accolade_id = accolade_id
        self.description = description


    def __repr__(self):
        return f"[Student ID={self.student_id} Staff ID={self.staff_id} Accolade ID={self.accolade_id} Date Awarded={self.date_awarded}]"
    
    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.username if self.student else None,
            'staff_id': self.staff_id,
            'staff_name': self.staff.username if self.staff else None,
            'accolade_id': self.accolade_id,
            'accolade_name': self.accolade.name if self.accolade else None,
            'description': self.description,
            'date_awarded': self.date_awarded.strftime("%Y-%m-%d %H:%M:%S")
        }