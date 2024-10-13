# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.user import UserService
from app.schemas import UserCreate
from tests.utils import create_test_user, TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_USER_FULL_NAME

client = TestClient(app)



def test_login_user(db):
    create_test_user(db)
    response = client.post("/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200, "Expected status code 200 for valid login"
    assert "access_token" in response.json(), "Response should contain access token"

@pytest.mark.parametrize("email, password, expected_status, expected_detail", [
    ("invalid@example.com", "wrongpassword", 400, "Invalid credentials"),
    (TEST_USER_EMAIL, None, 422, None), 
])
def test_invalid_login(db, email, password, expected_status, expected_detail):
    create_test_user(db)
    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == expected_status, f"Expected status code {expected_status} for {email}"
    if expected_detail:
        assert response.json() == {"detail": expected_detail}, "Response should contain the correct error message"

def test_register_existing_user(db):
    create_test_user(db)
    response = client.post("/auth/register", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_FULL_NAME
    })
    assert response.status_code == 400, "Expected status code 400 for duplicate user registration"
    assert response.json() == {"detail": f"A user with email '{TEST_USER_EMAIL}' already exists."}, \
        "Response should indicate duplicate email"

def test_create_user(db):
    user_in = UserCreate(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, full_name=TEST_USER_FULL_NAME)
    user = UserService.create_user(db=db, user=user_in)
    assert user.email == TEST_USER_EMAIL, "User email should match the provided email"

@pytest.mark.parametrize("email, password, expected_result", [
    (TEST_USER_EMAIL, TEST_USER_PASSWORD, True),      
    (TEST_USER_EMAIL, "wrongpassword", False),        
    ("nonexistent@example.com", TEST_USER_PASSWORD, False),  
])
def test_authenticate_user(db, email, password, expected_result):
    create_test_user(db)
    authenticated_user = UserService.authenticate_user(db=db, email=email, password=password)
    assert (authenticated_user is not None) == expected_result, \
        f"Expected authentication result for {email} with password {password} to be {expected_result}"
    if authenticated_user:
        assert authenticated_user.email == TEST_USER_EMAIL, "Authenticated user's email should match"
