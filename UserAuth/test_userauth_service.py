
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


access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNmOWEwNTBkYzRhZTgyOGMyODcxYzMyNTYzYzk5ZDUwMjc3ODRiZTUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcmFzb2ktYXV0aCIsImF1ZCI6InJhc29pLWF1dGgiLCJhdXRoX3RpbWUiOjE3NDY3MDA1OTMsInVzZXJfaWQiOiJWdVJKSUVHOFc0UEIzeDZuWUJIbUNlVXNWbUIzIiwic3ViIjoiVnVSSklFRzhXNFBCM3g2bllCSG1DZVVzVm1CMyIsImlhdCI6MTc0NjcwMDU5MywiZXhwIjoxNzQ2NzA0MTkzLCJlbWFpbCI6InJhaHVsMjMwODIwMDFqaGFAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbInJhaHVsMjMwODIwMDFqaGFAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.ssSBs-zSRTcJuH-m7o-rNMOZmljtv3ugy54i8AyMEc4mFTnyEGd2jk8jrRF_o349txAtuBNtSX3lSxcupxDSYwqcD10Fsv56NvkZvAI62wEqH4WQiB-6dvbBmAIuk7LcUSnCupZBnWMs-PXzlub7dQBu9m9VGNCVlaJVyC6JevenxvHPOEYQxAukOzjHHSF6yr5WdhWtkIwhur8PxQ8pTPBuw0Sbs5NnIDHDRvT4yu9VBNu2LCE9PAPpBRIFvdkQ4bZp3BMCk0z8YvRjvbRfeLDFbMCuQjxssz4XY_8WDkoRwJ9-PxJBXrEjEfUjeVKh50EFoRmbBecNyDdVPQqXUw"
firbase_UID = "VuRJIEG8W4PB3x6nYBHmCeUsVmB3"
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
