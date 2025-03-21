import os
import django
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cart.settings')
django.setup()

import grpc
import Proto.Cart_pb2 as pb # Import the generated protobuf module
import Proto.Cart_pb2_grpc  as Cart_pb2_gprc# Import the gRPC service module

def test_create_cart():
    # Create a gRPC channel
    channel = grpc.insecure_channel("localhost:50051")  # Change to your actual server address
    stub = Cart_pb2_gprc.CartServiceStub(channel)  # Replace with your actual service name

    # Create a request
    request = pb.CreateCartRequest(
        store_uuid="123e4567-e89b-12d3-a456-426614174000",
        user_phone_no="9876543210",
        order_type="DINEIN",  # Use the correct enum value from ORDERTYPE
        table_no="A12",
        vehicle_no="",
        vehicle_description="", 
    )

    try:
        # Send request
        response = stub.CreateCart(request)
        print("Cart Created Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

if __name__ == "__main__":
    test_create_cart()
