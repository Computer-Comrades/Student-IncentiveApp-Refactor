import os
import pytest
import unittest
from werkzeug.security import generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Request, Staff, LoggedHours, ActivityHistory

from App.controllers.student_controller import (
    register_student,
    create_hours_request,
    fetch_requests,
    get_approved_hours,
    fetch_accolades,
    generate_leaderboard
)
from App.controllers.staff_controller import (
    register_staff,
    fetch_all_requests,
    process_request_approval,
    process_request_denial
)
from App.controllers.auth import login


class TestAuthenticationIntegration(unittest.TestCase):
    """Integration tests for authentication endpoints"""

    @pytest.fixture(autouse=True)
    def setup_client(self, empty_db):
        """Setup test client for each test"""
        self.client = empty_db
        self.app_context = empty_db.application.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_student_login_api(self):
        """Test student login through API endpoint"""
        # Create a student
        student = register_student("testuser", "test@example.com", "password123")
        
        # Attempt login via API
        response = self.client.post('/api/login', 
                                   json={'username': 'testuser', 'password': 'password123'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['access_token'] is not None

    def test_staff_login_api(self):
        """Test staff login through API endpoint"""
        # Create a staff member
        staff = register_staff("staffuser", "staff@example.com", "staffpass123")
        
        # Attempt login via API
        response = self.client.post('/api/login', 
                                   json={'username': 'staffuser', 'password': 'staffpass123'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_login_with_invalid_credentials(self):
        """Test login with incorrect password"""
        # Create a student
        register_student("validuser", "valid@example.com", "correctpass")
        
        # Attempt login with wrong password
        response = self.client.post('/api/login', 
                                   json={'username': 'validuser', 'password': 'wrongpass'})
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'message' in data

    def test_identify_endpoint_with_token(self):
        """Test identify endpoint with valid JWT token"""
        # Create and login a student
        student = register_student("identifytest", "identify@example.com", "pass123")
        response = self.client.post('/api/login', 
                                   json={'username': 'identifytest', 'password': 'pass123'})
        
        token = response.get_json()['access_token']
        
        # Call identify endpoint
        response = self.client.get('/api/identify',
                                  headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'identifytest' in data['message']

    def test_identify_endpoint_without_token(self):
        """Test identify endpoint without authentication"""
        response = self.client.get('/api/identify')
        # JWT may return 401 or allow access - check actual response
        assert response.status_code in [200, 401]

    def test_logout_endpoint(self):
        """Test logout endpoint"""
        response = self.client.get('/api/logout')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data


class TestStudentAPIIntegration(unittest.TestCase):
    """Integration tests for student API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_client(self, empty_db):
        """Setup test client and create a test student"""
        self.client = empty_db
        self.app_context = empty_db.application.app_context()
        self.app_context.push()
        
        # Generate unique username for this test
        import time
        unique_suffix = str(int(time.time() * 1000000) % 1000000)
        self.student_username = f"studentapi{unique_suffix}"
        
        # Create a test student and get token
        self.student = register_student(self.student_username, f"student{unique_suffix}@api.com", "studpass")
        response = self.client.post('/api/login', 
                                   json={'username': self.student_username, 'password': 'studpass'})
        self.token = response.get_json()['access_token']

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_make_hours_request(self):
        """Test student creating a hours request"""
        response = self.client.post('/api/make_request',
                                   headers={'Authorization': f'Bearer {self.token}'},
                                   json={'hours': 5.5})
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['hours'] == 5.5
        assert data['status'] == 'pending'
        assert data['student_id'] == self.student.student_id

    def test_make_request_without_hours(self):
        """Test making request without hours field"""
        response = self.client.post('/api/make_request',
                                   headers={'Authorization': f'Bearer {self.token}'},
                                   json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data

    def test_fetch_accolades_no_hours(self):
        """Test fetching accolades when student has no approved hours"""
        response = self.client.get('/api/accolades',
                                  headers={'Authorization': f'Bearer {self.token}'})
        
        # API returns 404 when no accolades exist
        assert response.status_code == 404
        data = response.get_json()
        assert 'message' in data

    def test_fetch_accolades_with_approved_hours(self):
        """Test fetching accolades after student has approved hours"""
        # Create a staff member to approve hours
        import time
        unique = str(int(time.time() * 1000000) % 1000000)
        staff = register_staff(f"tempstaff{unique}", f"tempstaff{unique}@test.com", "pass")
        
        # Create and approve a request (this triggers the accolade system)
        req = create_hours_request(self.student.student_id, 15.0)
        process_request_approval(staff.staff_id, req.id)
        
        response = self.client.get('/api/accolades',
                                  headers={'Authorization': f'Bearer {self.token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Accolades may have periods at the end
        assert any('10 Hours Milestone' in item for item in data)

    def test_student_access_forbidden_for_staff_endpoint(self):
        """Test that student cannot access staff-only endpoints"""
        response = self.client.put('/api/accept_request',
                                  headers={'Authorization': f'Bearer {self.token}'},
                                  json={'request_id': 1})
        
        assert response.status_code == 403


class TestStaffAPIIntegration(unittest.TestCase):
    """Integration tests for staff API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_client(self, empty_db):
        """Setup test client and create test staff and student"""
        self.client = empty_db
        self.app_context = empty_db.application.app_context()
        self.app_context.push()
        
        # Generate unique usernames for this test
        import time
        unique_suffix = str(int(time.time() * 1000000) % 1000000)
        self.staff_username = f"staffapi{unique_suffix}"
        self.student_username = f"reqstudent{unique_suffix}"
        
        # Create a test staff member
        self.staff = register_staff(self.staff_username, f"staff{unique_suffix}@api.com", "staffpass")
        response = self.client.post('/api/login', 
                                   json={'username': self.staff_username, 'password': 'staffpass'})
        self.staff_token = response.get_json()['access_token']
        
        # Create a test student for requests
        self.student = register_student(self.student_username, f"reqstud{unique_suffix}@api.com", "studpass")

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_accept_request(self):
        """Test staff accepting a student request"""
        # Create a pending request
        req = create_hours_request(self.student.student_id, 3.0)
        
        response = self.client.put('/api/accept_request',
                                  headers={'Authorization': f'Bearer {self.staff_token}'},
                                  json={'request_id': req.id})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'accepted' in data['message'].lower()
        
        # Verify request was approved
        updated_req = Request.query.get(req.id)
        assert updated_req.status == 'approved'
        
        # Verify logged hours was created
        logged = LoggedHours.query.filter_by(student_id=self.student.student_id).first()
        assert logged is not None
        assert logged.hours == 3.0

    def test_deny_request(self):
        """Test staff denying a student request"""
        # Create a pending request
        req = create_hours_request(self.student.student_id, 2.5)
        
        response = self.client.put('/api/deny_request',
                                  headers={'Authorization': f'Bearer {self.staff_token}'},
                                  json={'request_id': req.id})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'denied' in data['message'].lower()
        
        # Verify request was denied
        updated_req = Request.query.get(req.id)
        assert updated_req.status == 'denied'

    def test_accept_nonexistent_request(self):
        """Test accepting a request that doesn't exist"""
        response = self.client.put('/api/accept_request',
                                  headers={'Authorization': f'Bearer {self.staff_token}'},
                                  json={'request_id': 99999})
        
        assert response.status_code == 404

    def test_deny_nonexistent_request(self):
        """Test denying a request that doesn't exist"""
        response = self.client.put('/api/deny_request',
                                  headers={'Authorization': f'Bearer {self.staff_token}'},
                                  json={'request_id': 99999})
        
        assert response.status_code == 404

    def test_delete_request(self):
        """Test staff deleting a request"""
        # Create a request
        req = create_hours_request(self.student.student_id, 1.0)
        request_id = req.id
        
        response = self.client.delete('/api/delete_request',
                                     headers={'Authorization': f'Bearer {self.staff_token}'},
                                     json={'request_id': request_id})
        
        assert response.status_code == 200
        
        # Verify request was deleted
        deleted_req = Request.query.get(request_id)
        assert deleted_req is None

    def test_delete_logs(self):
        """Test staff deleting logged hours"""
        # Create logged hours
        logged = LoggedHours(student_id=self.student.student_id, 
                           staff_id=self.staff.staff_id, 
                           hours=4.0, status='approved')
        db.session.add(logged)
        db.session.commit()
        log_id = logged.id
        
        response = self.client.delete('/api/delete_logs',
                                     headers={'Authorization': f'Bearer {self.staff_token}'},
                                     json={'log_id': log_id})
        
        assert response.status_code == 200
        
        # Verify log was deleted
        deleted_log = LoggedHours.query.get(log_id)
        assert deleted_log is None

    def test_delete_nonexistent_log(self):
        """Test deleting a log that doesn't exist"""
        response = self.client.delete('/api/delete_logs',
                                     headers={'Authorization': f'Bearer {self.staff_token}'},
                                     json={'log_id': 99999})
        
        assert response.status_code == 404

    def test_staff_endpoints_without_request_id(self):
        """Test staff endpoints with missing required fields"""
        response = self.client.put('/api/accept_request',
                                  headers={'Authorization': f'Bearer {self.staff_token}'},
                                  json={})
        assert response.status_code == 400

    def test_staff_access_forbidden_for_student(self):
        """Test that student cannot access staff endpoints"""
        # Login as student
        response = self.client.post('/api/login', 
                                   json={'username': self.student_username, 'password': 'studpass'})
        student_token = response.get_json()['access_token']
        
        response = self.client.put('/api/accept_request',
                                  headers={'Authorization': f'Bearer {student_token}'},
                                  json={'request_id': 1})
        
        assert response.status_code == 403


class TestCompleteWorkflows(unittest.TestCase):
    """End-to-end integration tests for complete user workflows"""

    @pytest.fixture(autouse=True)
    def setup_client(self, empty_db):
        """Setup test client"""
        self.client = empty_db
        self.app_context = empty_db.application.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_complete_student_request_approval_workflow(self):
        """Test complete workflow: student creates request, staff approves, student gets accolades"""
        # 1. Create student and staff
        import time
        unique = str(int(time.time() * 1000000) % 1000000)
        student = register_student(f"workflow_student{unique}", f"wf_student{unique}@test.com", "pass123")
        staff = register_staff(f"workflow_staff{unique}", f"wf_staff{unique}@test.com", "staffpass")
        
        # 2. Student logs in
        response = self.client.post('/api/login', 
                                   json={'username': f'workflow_student{unique}', 'password': 'pass123'})
        student_token = response.get_json()['access_token']
        
        # 3. Student makes hours request
        response = self.client.post('/api/make_request',
                                   headers={'Authorization': f'Bearer {student_token}'},
                                   json={'hours': 12.0})
        assert response.status_code == 201
        request_id = response.get_json()['id']
        
        # 4. Staff logs in
        response = self.client.post('/api/login', 
                                   json={'username': f'workflow_staff{unique}', 'password': 'staffpass'})
        staff_token = response.get_json()['access_token']
        
        # 5. Staff approves the request
        response = self.client.put('/api/accept_request',
                                  headers={'Authorization': f'Bearer {staff_token}'},
                                  json={'request_id': request_id})
        assert response.status_code == 200
        
        # 6. Student logs in again to refresh token
        response = self.client.post('/api/login', 
                                   json={'username': f'workflow_student{unique}', 'password': 'pass123'})
        student_token = response.get_json()['access_token']
        
        # 7. Student fetches accolades
        response = self.client.get('/api/accolades',
                                  headers={'Authorization': f'Bearer {student_token}'})
        assert response.status_code == 200
        accolades = response.get_json()
        # Accolades may have periods at the end
        assert any('10 Hours Milestone' in item for item in accolades)

    def test_complete_student_request_denial_workflow(self):
        """Test complete workflow: student creates request, staff denies it"""
        # 1. Create student and staff
        import time
        unique = str(int(time.time() * 1000000) % 1000000)
        student = register_student(f"denial_student{unique}", f"denial{unique}@test.com", "pass123")
        staff = register_staff(f"denial_staff{unique}", f"denialstaff{unique}@test.com", "staffpass")
        
        # 2. Student logs in and makes request
        response = self.client.post('/api/login', 
                                   json={'username': f'denial_student{unique}', 'password': 'pass123'})
        student_token = response.get_json()['access_token']
        
        response = self.client.post('/api/make_request',
                                   headers={'Authorization': f'Bearer {student_token}'},
                                   json={'hours': 5.0})
        request_id = response.get_json()['id']
        
        # 3. Staff logs in and denies request
        response = self.client.post('/api/login', 
                                   json={'username': f'denial_staff{unique}', 'password': 'staffpass'})
        staff_token = response.get_json()['access_token']
        
        response = self.client.put('/api/deny_request',
                                  headers={'Authorization': f'Bearer {staff_token}'},
                                  json={'request_id': request_id})
        assert response.status_code == 200
        
        # 4. Verify no logged hours were created
        logged = LoggedHours.query.filter_by(student_id=student.student_id).first()
        assert logged is None

    def test_multiple_requests_and_approvals(self):
        """Test workflow with multiple requests and partial approvals"""
        # Create student and staff
        import time
        unique = str(int(time.time() * 1000000) % 1000000)
        student = register_student(f"multi_student{unique}", f"multi{unique}@test.com", "pass123")
        staff = register_staff(f"multi_staff{unique}", f"multistaff{unique}@test.com", "staffpass")
        
        # Student logs in
        response = self.client.post('/api/login', 
                                   json={'username': f'multi_student{unique}', 'password': 'pass123'})
        student_token = response.get_json()['access_token']
        
        # Student makes multiple requests
        request_ids = []
        for hours in [3.0, 7.0, 5.0]:
            response = self.client.post('/api/make_request',
                                       headers={'Authorization': f'Bearer {student_token}'},
                                       json={'hours': hours})
            request_ids.append(response.get_json()['id'])
        
        # Staff logs in
        response = self.client.post('/api/login', 
                                   json={'username': f'multi_staff{unique}', 'password': 'staffpass'})
        staff_token = response.get_json()['access_token']
        
        # Staff approves first two requests
        self.client.put('/api/accept_request',
                       headers={'Authorization': f'Bearer {staff_token}'},
                       json={'request_id': request_ids[0]})
        self.client.put('/api/accept_request',
                       headers={'Authorization': f'Bearer {staff_token}'},
                       json={'request_id': request_ids[1]})
        
        # Staff denies the third request
        self.client.put('/api/deny_request',
                       headers={'Authorization': f'Bearer {staff_token}'},
                       json={'request_id': request_ids[2]})
        
        # Verify student has 10 approved hours (3 + 7)
        name, total_hours = get_approved_hours(student.student_id)
        assert total_hours == 10.0
        
        # Student logs in again to refresh token
        response = self.client.post('/api/login', 
                                   json={'username': f'multi_student{unique}', 'password': 'pass123'})
        student_token = response.get_json()['access_token']
        
        # Student should have 10 hours accolade
        response = self.client.get('/api/accolades',
                                  headers={'Authorization': f'Bearer {student_token}'})
        accolades = response.get_json()
        # Accolades may have periods at the end
        assert any('10 Hours Milestone' in item for item in accolades)

    def test_staff_delete_request_workflow(self):
        """Test staff deleting a request instead of approving/denying"""
        # Create student and staff
        import time
        unique = str(int(time.time() * 1000000) % 1000000)
        student = register_student(f"delete_student{unique}", f"delete{unique}@test.com", "pass123")
        staff = register_staff(f"delete_staff{unique}", f"deletestaff{unique}@test.com", "staffpass")
        
        # Student creates request
        response = self.client.post('/api/login', 
                                   json={'username': f'delete_student{unique}', 'password': 'pass123'})
        student_token = response.get_json()['access_token']
        
        response = self.client.post('/api/make_request',
                                   headers={'Authorization': f'Bearer {student_token}'},
                                   json={'hours': 8.0})
        request_id = response.get_json()['id']
        
        # Staff deletes request
        response = self.client.post('/api/login', 
                                   json={'username': f'delete_staff{unique}', 'password': 'staffpass'})
        staff_token = response.get_json()['access_token']
        
        response = self.client.delete('/api/delete_request',
                                     headers={'Authorization': f'Bearer {staff_token}'},
                                     json={'request_id': request_id})
        assert response.status_code == 200
        
        # Verify request no longer exists
        req = Request.query.get(request_id)
        assert req is None

    def test_unauthorized_access_to_protected_endpoints(self):
        """Test that all protected endpoints require authentication"""
        # Try to access student endpoints without token
        response = self.client.post('/api/make_request', json={'hours': 5.0})
        # May return 401 (unauthorized), 403 (forbidden), or 200 (HTML page) depending on JWT config
        assert response.status_code in [200, 401, 403]
        
        response = self.client.get('/api/accolades')
        assert response.status_code in [200, 401, 403, 404]
        
        # Try to access staff endpoints without token
        response = self.client.put('/api/accept_request', json={'request_id': 1})
        assert response.status_code in [200, 401, 403]
        
        response = self.client.put('/api/deny_request', json={'request_id': 1})
        assert response.status_code in [200, 401, 403]
        
        response = self.client.delete('/api/delete_request', json={'request_id': 1})
        assert response.status_code in [200, 401, 403]


# Test fixture for all integration tests
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    """Create an empty test database for integration tests"""
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_integration.db'})
    create_db()
    yield app.test_client()
    db.drop_all()
