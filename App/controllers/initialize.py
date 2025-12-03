from App.models import User, Student, Staff, Request
from App.database import db
from App.controllers.achievements_data import AchievementsData


def initialize_db(drop_first=True):
    """Initialize the database and seed sample data.

    Args:
        drop_first (bool): if True, drop all tables before creating them.

    Returns a dict with lists of created record IDs.
    """
    if drop_first:
        db.drop_all()
    db.create_all()

    AchievementsData.seed()


    # Sample students (username, email, password)
    students_data = [
        ("alice", "alice.smith@gmail.com", "password1"),
        ("bob", "bob.jones@hotmail.com", "password2"),
        ("charlie", "charlie.brown@gmail.com", "password3"),
        ("diana", "diana.lee@hotmail.com", "password4"),
        ("eve", "eve.patel@gmail.com", "password5"),
    ]

    # Sample staff (username, email, password)
    staff_data = [
        ("msmith", "mr.smith@gmail.com", "staffpass1"),
        ("mjohnson", "ms.johnson@hotmail.com", "staffpass2"),
        ("mlee", "mr.lee@gmail.com", "staffpass3"),
    ]

    students = []
    for username, email, pwd in students_data:
        s = Student(username=username, email=email, password=pwd)
        students.append(s)
        db.session.add(s)

    staff_members = []
    for username, email, pwd in staff_data:
        st = Staff(username=username, email=email, password=pwd)
        staff_members.append(st)
        db.session.add(st)

    db.session.commit()

    # Create 4 requests for first 4 students
    import random
    requests = []
    for i in range(4):
        student = students[i]
        hours = random.choice([5, 10, 12.5, 8])
        req = Request(student_id=student.user_id, hours=hours, status='pending')
        requests.append(req)
        db.session.add(req)

    db.session.commit()

    # Add logged hours
    from App.models import LoggedHours

    # Approve first two requests and create logged entries
    for i, req in enumerate(requests[:2]):
        req.status = 'approved'
        staff_member = staff_members[i % len(staff_members)]
        log = LoggedHours(student_id=req.student_id, staff_id=staff_member.user_id, hours=req.hours, status='approved')
        db.session.add(log)

    # Deny the third request (if present)
    if len(requests) >= 3:
        requests[2].status = 'denied'

    # Leave the fourth request pending

    # Add 3 extra logged hours entries (to reach 6 total logged hours)
    extra_logs = [
        (students[0].user_id, staff_members[0].user_id, 3.5, 'approved'),
        (students[1].user_id, staff_members[1].user_id, 7.0, 'approved'),
        (students[2].user_id, staff_members[2].user_id, 4.0, 'approved'),
    ]
    for student_id, staff_id, hours, status in extra_logs:
        log = LoggedHours(student_id=student_id, staff_id=staff_id, hours=hours, status=status)
        db.session.add(log)

    db.session.commit()

    # Return ids for reference
    result = {
        'students': [s.user_id for s in students],
        'staff': [st.user_id for st in staff_members],
        'requests': [r.id for r in Request.query.order_by(Request.id).all()],
        'logged_hours': [l.id for l in LoggedHours.query.order_by(LoggedHours.id).all()]
    }

    return result



def initialize(drop_first=True):
    """Compatibility wrapper used by CLI (keeps previous name `initialize`)."""
    return initialize_db(drop_first=drop_first)