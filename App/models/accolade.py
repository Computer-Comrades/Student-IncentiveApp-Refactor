from App.database import db

class Accolade(db.Model):
    __tablename__ = 'accolade'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"[Accolade ID={self.id} Name={self.name}]"

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name
        }