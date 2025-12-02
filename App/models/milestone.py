from App.database import db

class Milestone(db.Model):
    __tablename__ = 'milestone'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    required_hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, name, required_hours, description):
        self.name = name
        self.required_hours = required_hours
        self.description = description

    def __repr__(self):
        return f"[Milestone ID={self.id} Name={self.name} Required Hours={self.required_hours}]"

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'required_hours': self.required_hours,
            'description': self.description
        }