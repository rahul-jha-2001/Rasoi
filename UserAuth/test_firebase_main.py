
import sys
from pathlib import Path

import pytest
from firebase_main import FireBaseAuthManager
from firebase_main import UserRecord
from Proto.user_auth_pb2_grpc import AuthServiceStub
# Keep your path setup code
SKIP_DIRS = {
    '__pycache__',
    'venv',
    'env',
    '.git',
    '.idea',
    '.vscode',
    'logs',
    'media',
    'static',
    'migrations',
}

BASE_DIR = Path(__file__).resolve().parent.parent
for item in BASE_DIR.iterdir():
    if item.is_dir() and item.name not in SKIP_DIRS:
        sys.path.append(str(item))



""" 
test cases for the fiberbase main class
"""

@pytest.fixture(scope="session")
def firebase_main_instance() -> FireBaseAuthManager:
    """Create an instance of the FirebaseMain class"""
    return FireBaseAuthManager()

@pytest.fixture(scope="session")
def email():
    """Provide a test email"""
    return "test@gmail.com"
@pytest.fixture(scope="session")
def password():
    """Provide a test password"""
    return "password123"
@pytest.fixture(scope="session")
def user(firebase_main_instance, email, password):
    """Create a test user"""
    user = firebase_main_instance.create_user(
        email=email,
        password=password
    )
    yield user
    firebase_main_instance.delete_user(user.uid)



def test_create_user(firebase_main_instance, email, password):
    user = firebase_main_instance.create_user(
        email= email,
        password= password
    )
    assert user is not None
    assert user.email == email
    firebase_main_instance.delete_user(user.uid)



def test_update_user(firebase_main_instance, user, email, password):
    """Test user update"""
    email = "test@gmail.com"
    password = "newpassword123"
    updated_user = firebase_main_instance.update_user(
        uid=user.uid,
        email=email,
        password=password
    )
    assert updated_user is not None
    assert updated_user.email == email


def test_list_users(firebase_main_instance,user):
    """Test listing users"""
    users = firebase_main_instance.list_users(max_results=10)
    assert users is not None
    assert len(users) > 0
    for user in users:
        assert isinstance(user, UserRecord)

# def test_delete_user(firebase_main_instance, email, password):
#     """Test user deletion"""
#     user = firebase_main_instance.create_user(
#         email=email,
#         password=password
#     )
#     assert user is not None
#     firebase_main_instance.delete_user(user.uid)



def test_set_custom_claims(firebase_main_instance, user):
    """Test setting custom claims"""
    claims = {"role": "admin"}
    firebase_main_instance.add_custom_claims(
        firebase_uid=user.uid,
        claims=claims
    )
    user = firebase_main_instance.get_user_by_UID(user.uid)
    assert user is not None
    assert user.custom_claims == claims
    assert user.custom_claims == claims
    assert user.custom_claims is not None
    assert user.custom_claims["role"] == "admin"