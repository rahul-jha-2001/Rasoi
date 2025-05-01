
import threading
import sys
from pathlib import Path
import time
import grpc
import pytest
from grpc_serve import serve
from Proto import user_auth_pb2
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

# Define constants
SERVER_ADDRESS = 'localhost:50051'
META_DATA = [
    ("role", "internal"),
    ("service", "product")
]


access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjkwOTg1NzhjNDg4MWRjMDVlYmYxOWExNWJhMjJkOGZkMWFiMzRjOGEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcmFzb2ktYXV0aCIsImF1ZCI6InJhc29pLWF1dGgiLCJhdXRoX3RpbWUiOjE3NDU5NDUxOTUsInVzZXJfaWQiOiIwTU00Q0pGRUlLZXk1RzB4Q0FQcDZxUXhyODUyIiwic3ViIjoiME1NNENKRkVJS2V5NUcweENBUHA2cVF4cjg1MiIsImlhdCI6MTc0NTk0NTE5NSwiZXhwIjoxNzQ1OTQ4Nzk1LCJlbWFpbCI6InJqaGE5NjJAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbInJqaGE5NjJAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.KBW7dCO_xP4gvsOZF_elv-YK14uK90M4eZvX2fqZrsY_9EfILvQ6cL_4b8GPtUHUlu9vTLtypVXiJXj6SNMvKNUCzxpjeIvupOwHsxkkwO5naPu1RfWUqJP_WqfAVNCNJXZ5Byzh3ibMjXboLLTVJvQwBo3nc_3wX399F2DbIGYiWw9OctVtA9Fow9kDQOh2gxIvwA0WC4eyhe0Q2lUQl83SbxnhPZdgR1jYqaJXvbCtrTWsTVwvi1CPwZV_1Ogx-NbCjya8oqWjEx6DtQ_WUlcuAeQqzr66ZHQVpREvm67VnCj9Ap1LDlOEsnaSMSPAzs6Jp-KPCwuBTlxdCaAkmQ"
firbase_UID = "0MM4CJFEIKey5G0xCAPp6qQxr852"
# Fixtures for setup and teardown
@pytest.fixture(scope="session")
def grpc_server():
    """Start the gRPC server for testing and stop it after tests"""
    server_thread = threading.Thread(target=serve, daemon=True)
    print("Starting gRPC server...")
    server_thread.start()
    time.sleep(1)  # Give server time to start
    yield
    # If the server has a shutdown method, you'd call it here

@pytest.fixture(scope="session")
def grpc_channel(grpc_server):
    """Create a gRPC channel for tests"""
    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        yield channel

@pytest.fixture(scope="session")
def user_auth_stub(grpc_channel):
    """Create a product service stub"""
    return AuthServiceStub(grpc_channel)

def test_create_user(user_auth_stub):
    """Test user creation"""
    request = user_auth_pb2.CreateUserRequest(
        firebase_uid=firbase_UID,
        token=access_token)
    response = user_auth_stub.CreateUser(request, metadata=META_DATA)
    assert response is not None
    assert response.DESCRIPTOR.full_name == "google.protobuf.Empty"

def test_verify_token(user_auth_stub):
    """Test token verification"""
    request = user_auth_pb2.VerifyTokenRequest(
        token=access_token,firebase_uid=firbase_UID)
    response = user_auth_stub.VerifyToken(request, metadata=META_DATA)
    assert response is not None
    assert response.DESCRIPTOR.full_name == "google.protobuf.Empty"

