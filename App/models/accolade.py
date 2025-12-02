from App.database import db

class Accolade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"[Accolade ID={self.id} Name={self.name}]"

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }