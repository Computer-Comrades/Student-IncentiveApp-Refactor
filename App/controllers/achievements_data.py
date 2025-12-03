from App.database import db
from App.models import Milestone, Accolade

class AchievementsData:
    """Service to seed initial milestones and accolades data."""

    @staticmethod
    def seed():
        # Milestones
        milestones = [
            {"name": "10 Hours Milestone", "required_hours": 10, "description": "Completed 10 approved service hours"},
            {"name": "25 Hours Milestone", "required_hours": 25, "description": "Completed 25 approved service hours"},
            {"name": "50 Hours Milestone", "required_hours": 50, "description": "Completed 50 approved service hours"},
        ]
        for ms in milestones:
            existing = Milestone.query.filter_by(name=ms["name"]).first()
            if not existing:
                milestone = Milestone(name=ms["name"], required_hours=ms["required_hours"], description=ms["description"])
                db.session.add(milestone)

        # Accolades
        accolades = [
            {"name": "Outstanding Helper"},
            {"name": "Volunteer Star"},
            {"name": "Team Player"},
        ]
        for ac in accolades:
            existing = Accolade.query.filter_by(name=ac["name"]).first()
            if not existing:
                accolade = Accolade(name=ac["name"])
                db.session.add(accolade)

        db.session.commit()

