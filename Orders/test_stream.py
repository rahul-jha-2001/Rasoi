import sys
import os
from  datetime import datetime
import logging
from concurrent import futures

import django
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()


import grpc
from grpc import StatusCode
import traceback
from decimal import Decimal as DecimalType
from dotenv import load_dotenv
from google.protobuf import empty_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from Proto import order_pb2,order_pb2_grpc,cart_pb2,cart_pb2_grpc

from Proto.order_pb2 import OrderState,OrderType,PaymentMethod,PaymentState
from Order.models import Order,OrderItem,OrderItemAddOn,OrderPayment

def test_stream_orders():
    # Connect to gRPC server
    channel = grpc.insecure_channel(f"localhost:50053")    
    cart_stub = order_pb2_grpc.OrderServiceStub(channel)

    # Create a request
    request = order_pb2.StreamOrderRequest(store_uuid="9c0a689e-c1f4-4bcd-b64a-29d1861db326")  # Replace with a real store UUID

    # Add metadata (Auth headers)
    metadata = [
        ("authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJSYXNvaSIsImlhdCI6MTc0MzY5MzA5MywiZXhwIjoxNzQzNzM2MjkzLCJzdG9yZV91dWlkIjoiOWMwYTY4OWUtYzFmNC00YmNkLWI2NGEtMjlkMTg2MWRiMzI2Iiwicm9sZSI6IlN0b3JlIn0.gw5iHhNhHYPOxfjazuvYN2jQxJk6ed-IkER56G6bLn0")
    ]

    try:
        # Call the streaming RPC with metadata
        for response in cart_stub.StreamOrders(request, metadata=metadata):
            print(f"Received order: {response.order}")
    except grpc.RpcError as e:
        print(f"Stream closed: {e.details()}")

if __name__ == "__main__":
    test_stream_orders()
