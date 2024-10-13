# tests/utils.py
from app.services.user import UserService
from app.models import User
from app.schemas import UserCreate

TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword"
TEST_USER_FULL_NAME = "Test User"

def create_test_user(db, email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, full_name=TEST_USER_FULL_NAME):
    user_in = UserCreate(email=email, password=password, full_name=full_name)
    return UserService.create_user(db=db, user=user_in)

def clear_db(db):
    db.query(User).delete()
    db.commit()
