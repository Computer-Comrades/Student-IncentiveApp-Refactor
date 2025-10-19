from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Student, Staff, User
from.index import index_views
from App.controllers.student_controller import get_all_students_json,register_student
from App.controllers.staff_controller import get_all_staff_json,register_staff
from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    view_leaderboard,
    get_all_requests_json,
    get_all_logged_hours_json
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'],data['email'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.form
    user = create_user(data['username'], data['password'])
    return jsonify({'message': f"user {user.username} created with id {user.id}"})

@user_views.route('/api/create_Student', methods=['POST'])
def create_student_endpoint():
    data = request.json
    
    users = User.query.all()
    for u in users:
        if u.email == data['email'] or u.username == data['name']:
            return jsonify({'message': f"User with email {data['email']} already exists or username {data['name']}."}), 400
    
    student = register_student(data['name'], data['email'], data['password'])
    return jsonify({'message': f"Student {student.username} created with id {student.student_id}"})

@user_views.route('/api/create_Staff', methods=['POST'])
def create_staff_endpoint():
    data = request.json

    users = User.query.all()
    for u in users:
        if u.email == data['email'] or u.username == data['name']:
            return jsonify({'message': f"User with email {data['email']} already exists or username {data['name']}."}), 400

    staff = register_staff(data['name'], data['email'], data['password'])
    return jsonify({'message': f"Staff {staff.username} created with id {staff.staff_id}"})

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@user_views.route('/api/students', methods=['GET'])
def get_students_action():
    students = get_all_students_json()
    return jsonify(students)

@user_views.route('/api/staff', methods=['GET'])
def get_staff_action():
    staff_members = get_all_staff_json()
    return jsonify(staff_members)


@user_views.route('/api/leaderboard', methods=['GET'])
def leaderboard_action():
    leaderboard = view_leaderboard()
    return jsonify(leaderboard)

@user_views.route('/api/requests', methods=['GET'])
def requests_action():
    requests = get_all_requests_json()
    return jsonify(requests)

@user_views.route('/api/logged_hours', methods=['GET'])
def logged_hours_action():
    logs = get_all_logged_hours_json()
    return jsonify(logs)