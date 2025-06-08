
import threading
import sys
from pathlib import Path
import time
import grpc
import pytest
from grpc_serve import serve
from Proto import user_auth_pb2
from firebase_main import FireBaseAuthManager
from firebase_main import UserRecord
from Proto.user_auth_pb2_grpc import AuthServiceStub

import django,os
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError
from django.db import transaction
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Product.settings')
django.setup()

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

# Define constants
SERVER_ADDRESS = 'localhost:50051'
META_DATA = [
    ("type", "internal"),
    ("service", "product")
]
from User.models import User,Store,Address 


@pytest.fixture(scope="session")
def grpc_server():
    """Start the gRPC server for testing and stop it after tests"""
    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start
    yield
    # If the server exposes a shutdown, call it here


@pytest.fixture(scope="session")
def grpc_channel(grpc_server):
    """Create a gRPC channel for tests"""
    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        yield channel


@pytest.fixture(scope="session")
def user_auth_stub(grpc_channel):
    """Create an AuthService stub"""
    return AuthServiceStub(grpc_channel)


@pytest.fixture(scope="session")
def firebase_UID():
    """Dummy Firebase UID for testing"""
    return "J33ViVQlwxQ66FiSRaPTQXgAyPF2"

@pytest.fixture(scope="session")
def email():
    return "test@gmail.com"

@pytest.fixture(scope="session")
def access_token():
    """Dummy access token for testing"""
    return "eyJhbGciOiJSUzI1NiIsImtpZCI6IjU5MWYxNWRlZTg0OTUzNjZjOTgyZTA1MTMzYmNhOGYyNDg5ZWFjNzIiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX3V1aWQiOiIzOGNhZGIxOS0yZDlmLTRlYmUtYmU3MC03ZDRlZGEzYTBjNDYiLCJmaXJlYmFzZV91aWQiOiJKMzNWaVZRbHd4UTY2RmlTUmFQVFFYZ0F5UEYyIiwidHlwZSI6InN0b3JlIiwicm9sZSI6ImFkbWluIiwic3RvcmVfdXVpZHMiOltdLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcmFzb2ktYXV0aCIsImF1ZCI6InJhc29pLWF1dGgiLCJhdXRoX3RpbWUiOjE3NDY4ODIyOTQsInVzZXJfaWQiOiJKMzNWaVZRbHd4UTY2RmlTUmFQVFFYZ0F5UEYyIiwic3ViIjoiSjMzVmlWUWx3eFE2NkZpU1JhUFRRWGdBeVBGMiIsImlhdCI6MTc0Njg4MjI5NCwiZXhwIjoxNzQ2ODg1ODk0LCJlbWFpbCI6InJhaHVsMjMwODIwMDFqaGFAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsicmFodWwyMzA4MjAwMWpoYUBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.0DyrYbJ2z_RnegXrrB9rMp5OAPa9HVYTJCc_e1FPjP4jAEi1D5Rp_BsBSbt2eZF1qQLDxdOQspEbBca290GqwsQz6YxRa-7z_eJPBLb-BY5h2ZQ-2EKdkI4w95Un4Lbq17gLOVdY5TRWRAsY9KMMiTlUkHrngPXvHafpeeAFlPnTDEHmiVrITqEkJh1On-9AubKnuSnIrrJbIQ51F4Nv0EawY-v9vb46sOGq14KjL0lzw2WCD8x0spEngi3A4ROeDBPHEvXGULzr1woQ_YGHjaA3KptfdPnQjW7pFIQMx3eJrB2swoRS95J7Y_OyghvLj_xzJG4eSdpKz8uD0HxCUQ"

@pytest.fixture(scope = "session")
def create_user(firebase_UID,email):
    user = User.objects.create(
        firebase_uid = firebase_UID,
        email = email
    )
    yield user
    user.delete()



# --------------------
# Test Cases
# --------------------
def test_grpc_create_user(user_auth_stub, firebase_UID, access_token):
    request = user_auth_pb2.CreateUserRequest(
        firebase_uid=firebase_UID,
        token=access_token
    )
    response = user_auth_stub.CreateUser(request, metadata=META_DATA)
    assert response is not None
    assert response.DESCRIPTOR.full_name == "google.protobuf.Empty"


def test_verify_token(user_auth_stub, firebase_UID, access_token):
    request = user_auth_pb2.VerifyTokenRequest(
        token=access_token,
        firebase_uid=firebase_UID
    )
    response = user_auth_stub.VerifyToken(request, metadata=META_DATA)
    assert response is not None
    assert response.DESCRIPTOR.full_name == "google.protobuf.Empty"


def test_create_store(user_auth_stub, firebase_UID):
    request = user_auth_pb2.CreateStoreRequest(
        user_uuid=firebase_UID,
        store_name="Test Store"
    )
    response = user_auth_stub.CreateStore(request, metadata=META_DATA)
    assert response is not None
    assert response.store is not None


def test_update_store(user_auth_stub, firebase_UID):
    # Use a placeholder store_uuid; should match an existing store in setup
    request = user_auth_pb2.UpdateStoreRequest(
        store_uuid="00000000-0000-0000-0000-000000000000",
        store_name="Updated Store"
    )
    response = user_auth_stub.UpdateStore(request, metadata=META_DATA)
    assert response is not None
    assert response.store is not None


def test_get_store(user_auth_stub, firebase_UID):
    request = user_auth_pb2.GetStoreRequest(
        user_uuid=firebase_UID,
        store_uuid="00000000-0000-0000-0000-000000000000"
    )
    response = user_auth_stub.GetStore(request, metadata=META_DATA)
    assert response is not None
    assert response.store.user_uuid == firebase_UID


def test_get_all_stores(user_auth_stub, firebase_UID):
    request = user_auth_pb2.GetAllStoreRequest(
        user_uuid=firebase_UID,
        page=1,
        limit=10
    )
    response = user_auth_stub.GetAllStores(request, metadata=META_DATA)
    assert response is not None
    # Response contains list of stores
    assert hasattr(response, 'stores')


def test_delete_store(user_auth_stub, firebase_UID):
    request = user_auth_pb2.DeleteStoreRequest(
        user_uuid=firebase_UID,
        store_uuid="00000000-0000-0000-0000-000000000000"
    )
    response = user_auth_stub.DeleteStore(request, metadata=META_DATA)
    assert response is not None


def test_create_address(user_auth_stub, firebase_UID):
    request = user_auth_pb2.AddAddressRequest(
        user_uuid=firebase_UID,
        store_uuid="00000000-0000-0000-0000-000000000000",
        address_1="123 Main St",
        city="Metropolis",
        pincode="123456",
        state="State",
        country="Country"
    )
    response = user_auth_stub.CreateAddress(request, metadata=META_DATA)
    assert response is not None
    assert response.address.address_uuid is not None


def test_update_address(user_auth_stub, firebase_UID):
    request = user_auth_pb2.UpdateAddressRequest(
        store_uuid="00000000-0000-0000-0000-000000000000",
        address_uuid="00000000-0000-0000-0000-000000000000",
        address_1="456 Elm St",
        city="Gotham",
        pincode="654321",
        state="New State",
        country="New Country"
    )
    response = user_auth_stub.UpdateAddress(request, metadata=META_DATA)
    assert response is not None


def test_get_address(user_auth_stub, firebase_UID):
    request = user_auth_pb2.GetAddressRequest(
        user_uuid=firebase_UID,
        store_uuid="00000000-0000-0000-0000-000000000000",
        address_uuid="00000000-0000-0000-0000-000000000000"
    )
    response = user_auth_stub.GetAddress(request, metadata=META_DATA)
    assert response is not None
    assert response.address.address_uuid is not None


def test_delete_address(user_auth_stub, firebase_UID):
    request = user_auth_pb2.DeleteAddressRequest(
        user_uuid=firebase_UID,
        store_uuid="00000000-0000-0000-0000-000000000000",
        address_uuid="00000000-0000-0000-0000-000000000000"
    )
    response = user_auth_stub.DeleteAddress(request, metadata=META_DATA)
    assert response is not None
