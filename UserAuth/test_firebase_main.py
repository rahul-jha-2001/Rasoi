import sys
from pathlib import Path
import pytest

from firebase_main import FireBaseAuthManager
from firebase_admin.auth import UserRecord  # ✅ Corrected import

# Skip unwanted dirs from path
SKIP_DIRS = {
    '__pycache__', 'venv', 'env', '.git', '.idea', '.vscode',
    'logs', 'media', 'static', 'migrations',
}

BASE_DIR = Path(__file__).resolve().parent.parent
for item in BASE_DIR.iterdir():
    if item.is_dir() and item.name not in SKIP_DIRS:
        sys.path.append(str(item))


# ===================== Fixtures =====================

@pytest.fixture(scope="session")
def firebase_main_instance() -> FireBaseAuthManager:
    return FireBaseAuthManager()

@pytest.fixture(scope="session")
def email():
    return "test@gmail.com"

@pytest.fixture(scope="session")
def password():
    return "password123"

@pytest.fixture(scope="function")
def user(firebase_main_instance, email, password):
    """Creates and cleans up a Firebase user"""
    user = firebase_main_instance.create_user(email=email, password=password)
    yield user
    firebase_main_instance.delete_user(user.uid)


# ===================== Tests =====================

def test_create_user(firebase_main_instance, email, password):
    user = firebase_main_instance.create_user(email=email, password=password)
    assert user is not None
    assert user.email == email
    firebase_main_instance.delete_user(user.uid)

def test_update_user(firebase_main_instance, user):
    new_password = "newpassword123"
    updated_user = firebase_main_instance.update_user(
        uid=user.uid,
        email=user.email,
        password=new_password
    )
    assert updated_user is not None
    assert updated_user.email == user.email

def test_list_users(firebase_main_instance, user):
    users = firebase_main_instance.list_users(max_results=10)
    assert users is not None
    assert any(u.uid == user.uid for u in users)
    assert all(isinstance(u, UserRecord) for u in users)

def test_set_custom_claims(firebase_main_instance, user):
    claims = {"role": "admin"}
    firebase_main_instance.add_custom_claims(uid=user.uid, claims=claims)
    updated_user = firebase_main_instance.get_user_by_UID(user.uid)

    assert updated_user is not None
    assert updated_user.custom_claims is not None
    assert updated_user.custom_claims.get("role") == "admin"
