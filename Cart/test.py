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
    except Exception as e:
        print(f"Error: {e}")
def test_get_cart():
    channel = grpc.insecure_channel("localhost:50051")
    stub = Cart_pb2_gprc.CartServiceStub(channel)

    request = pb.GetCartRequest(
        store_uuid="123e4567-e89b-12d3-a456-426614174000",
        user_phone_no="9876543210"
    )

    try:
        response = stub.GetCart(request)
        print("Cart Retrieved Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

def test_update_cart():
    channel = grpc.insecure_channel("localhost:50051")
    stub = Cart_pb2_gprc.CartServiceStub(channel)

    request = pb.UpdateCartRequest(
        store_uuid="123e4567-e89b-12d3-a456-426614174000",
        user_phone_no="9876543210",
        cart_uuid="123e4567-e89b-12d3-a456-426614174001",
        cart=pb.Cart(
            store_uuid="123e4567-e89b-12d3-a456-426614174000",
            user_phone_no="9876543210",
            order_type="DINEIN",
            table_no="A12",
            coupon_code="DISCOUNT10"
        )
    )

    try:
        response = stub.UpdateCart(request)
        print("Cart Updated Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

def test_delete_cart():
    channel = grpc.insecure_channel("localhost:50051")
    stub = Cart_pb2_gprc.CartServiceStub(channel)

    request = pb.DeleteCartRequest(
        store_uuid="123e4567-e89b-12d3-a456-426614174000",
        user_phone_no="9876543210",
        cart_uuid="123e4567-e89b-12d3-a456-426614174001"
    )

    try:
        response = stub.DeleteCart(request)
        print("Cart Deleted Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

def test_add_cart_item():
    channel = grpc.insecure_channel("localhost:50051")
    stub = Cart_pb2_gprc.CartServiceStub(channel)

    request = pb.AddCartItemRequest(
        cart_uuid="123e4567-e89b-12d3-a456-426614174001",
        cart_item=pb.CartItem(
            product_name="Pizza",
            product_uuid="123e4567-e89b-12d3-a456-426614174002",
            unit_price=12.99,
            quantity=2,
            tax_percentage=10.0,
            packaging_cost=1.5
        )
    )

    try:
        response = stub.AddCartItem(request)
        print("Cart Item Added Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

def test_create_addon():
    channel = grpc.insecure_channel("localhost:50051")
    stub = Cart_pb2_gprc.CartServiceStub(channel)

    request = pb.CreateAddOnRequest(
        cart_uuid="123e4567-e89b-12d3-a456-426614174001",
        cart_item_uuid="123e4567-e89b-12d3-a456-426614174003",
        add_on=pb.AddOn(
            add_on_name="Extra Cheese",
            add_on_uuid="123e4567-e89b-12d3-a456-426614174004",
            quantity=1,
            unit_price=2.5,
            is_free=False
        )
    )

    try:
        response = stub.CreateAddOn(request)
        print("Add-On Created Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

def test_add_coupon():
    channel = grpc.insecure_channel("localhost:50051")
    stub = Cart_pb2_gprc.CartServiceStub(channel)

    request = pb.AddCouponRequest(
        cart_uuid="123e4567-e89b-12d3-a456-426614174001",
        Coupon_code="DISCOUNT10"
    )

    try:
        response = stub.AddCoupon(request)
        print("Coupon Added Successfully:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

if __name__ == "__main__":
    test_create_cart()
    # test_get_cart()
    # test_update_cart()
    # test_delete_cart()
    # test_add_cart_item()
    # test_create_addon()
    # test_add_coupon()
