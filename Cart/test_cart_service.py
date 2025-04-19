import threading
import sys
from pathlib import Path
import time
import grpc
from concurrent import futures
import pytest
from uuid import uuid4
from grpc_serve import serve
from Proto import cart_pb2_grpc
from Proto import cart_pb2
from Proto.cart_pb2 import CartItem, Cart,CARTSTATE
from Proto.cart_pb2_grpc import CartServiceStub


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
PRODUCT_SERVER_ADDRESS = 'localhost:50052'
CART_SERVER_ADDRESS = 'localhost:50051'
META_DATA = [
    ("role", "internal"),
    ("service", "Cart")
]

import unittest
from unittest import mock
import uuid
import datetime
import os
import django
from django.test import TestCase, TransactionTestCase
from django.db import transaction
import grpc
from google.protobuf import empty_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from grpc_serve import serve


from Proto import product_pb2_grpc
from Proto import product_pb2
from utils.check_access import check_access
import logging
from dotenv import load_dotenv
load_dotenv()
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cart.settings')


# Fake product service
PRODUCT_SERVER_ADDRESS = 'localhost:50052'
CART_SERVER_ADDRESS = 'localhost:50051'
store_uuid = str(uuid.uuid4())
product_uuid = str(uuid.uuid4())
category_uuid = str(uuid.uuid4())
product_uuid = str(uuid.uuid4())
add_on_uuid = str(uuid.uuid4())
diet_pref_uuid = str(uuid.uuid4())
add_on_uuid = str(uuid.uuid4())
user_phone_no = str("9977636633")

META_DATA = [
    ("role", "internal"),
    ("service", "product")
]

class ProductService(product_pb2_grpc.ProductServiceServicer):
    
    def __init__(self):

        self.category = product_pb2.category(
            category_uuid=category_uuid,
            store_uuid=store_uuid,
            name="Test Category",
            description="This is a test category.",
            display_order=1,
            is_available=True,
            created_at=Timestamp(),
            updated_at=Timestamp()
        )
        self.diet_pref = product_pb2.dietary_preference(
            store_uuid=store_uuid,
            diet_pref_uuid=diet_pref_uuid,
            name="Vegan",
            description="Vegan dietary preference.",
            icon_url="http://example.com/icon.png"
        )
        self.product = product_pb2.product(
            product_uuid=product_uuid,
            store_uuid=store_uuid,
            name="Test Product",
            description="This is a test product.",
            status=product_pb2.Productstatus.PRODUCT_STATE_ACTIVE ,
            is_available=True,
            display_price=10.0,
            price=10.0,
            GST_percentage=18.0,
            category=self.category,
            dietary_pref=[self.diet_pref],
            image_URL="http://example.com/image.png",
            created_at=Timestamp(),
            updated_at=Timestamp()
        )
        self.add_on = product_pb2.add_on(
            add_on_uuid=add_on_uuid,
            name="Test Add-On",
            is_available=True,
            max_selectable=5,
            GST_percentage=18.0,
            price=5.0,
            product_uuid=product_uuid,
            created_at=Timestamp(),
            updated_at=Timestamp(),
            is_free=False
        )

    def GetProduct(self, request, context):
        if request.product_uuid != product_uuid or request.store_uuid != store_uuid:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            context.abort()
        return product_pb2.ProductResponse(product = self.product)

    def GetAddOn(self, request, context):
        if request.add_on_uuid != add_on_uuid or request.product_uuid != product_uuid:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Add-On not found")
            context.abort()
        return product_pb2.AddOnResponse(add_on = self.add_on)

def start_product_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Add your services to the server
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)    
    # Get the port from environment variables
    # Bind the server to the specified port
    server.add_insecure_port(PRODUCT_SERVER_ADDRESS)
    server.start()

    server.wait_for_termination()


@pytest.fixture(scope="session")
def grpc_product_server():
    product_server_thread = threading.Thread(target=start_product_service)
    product_server_thread.start()
    # Wait for the server to start
    time.sleep(1)

@pytest.fixture(scope="session")
def grpc_cart_server():
    cart_server_thread = threading.Thread(target=serve)
    cart_server_thread.start()
    yield


@pytest.fixture(scope="session")
def grpc_cart_stub(grpc_cart_server: None,):
    channel = grpc.insecure_channel(CART_SERVER_ADDRESS)
    stub = cart_pb2_grpc.CartServiceStub(channel)
    yield stub
    channel.close()
@pytest.fixture(scope="function")
def grpc_product_stub(grpc_product_server: None):
    channel = grpc.insecure_channel(PRODUCT_SERVER_ADDRESS)
    stub = product_pb2_grpc.ProductServiceStub(channel)
    yield stub
    channel.close()


@pytest.fixture(scope="function")
def cart(grpc_cart_stub):
    request = cart_pb2.CreateCartRequest(
        store_uuid=store_uuid,
        user_phone_no=user_phone_no,
        order_type=cart_pb2.ORDERTYPE.ORDER_TYPE_DINE_IN,
        table_no="A1",
    )
    response = grpc_cart_stub.CreateCart(request, metadata=META_DATA)
    yield response.cart

    try:
        grpc_cart_stub.DeleteCart(cart_pb2.DeleteCartRequest(cart_uuid=response.cart.cart_uuid), metadata=META_DATA)
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.NOT_FOUND:
            raise e

@pytest.fixture(scope="function")
def cart_item(grpc_cart_stub,cart):
    request = cart_pb2.AddCartItemRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no,
        product_uuid=product_uuid,
    )
    response = grpc_cart_stub.AddCartItem(request, metadata=META_DATA)
    yield response.cart.items[0]
    try:
        grpc_cart_stub.RemoveCartItem(cart_pb2.RemoveCartItemRequest(cart_uuid=cart.cart_uuid, cart_item_uuid=response.cart.items[0].cart_item_uuid), metadata=META_DATA)
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.NOT_FOUND:
            raise e
        
@pytest.fixture(scope="function")
def add_on(grpc_cart_stub,cart,cart_item):

    request = cart_pb2.CreateAddOnRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no,
        cart_item_uuid=cart_item.cart_item_uuid,
        add_on_uuid=add_on_uuid
    )
    response = grpc_cart_stub.CreateAddOn(request, metadata=META_DATA)
    yield response.cart.items[0].add_ons[0]
    try:
        grpc_cart_stub.RemoveAddOn(cart_pb2.RemoveAddOnRequest(cart_uuid=cart_item.cart_uuid, cart_item_uuid=cart_item.cart_item_uuid, add_on_uuid=response.cart.items[0].add_ons[0].add_on_uuid), metadata=META_DATA)
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.NOT_FOUND:
            raise e

@pytest.fixture(scope="function")
def coupon(grpc_cart_stub):
    request = cart_pb2.CreateCouponRequest(
        store_uuid=store_uuid,
        coupon=cart_pb2.Coupon(
            coupon_code = "TESTCOUPON",
            discount_type=cart_pb2.DISCOUNTTYPE.DISCOUNT_TYPE_PERCENTAGE,
            discount=10.0,
            valid_from=Timestamp().FromDatetime(datetime.datetime.now()-datetime.timedelta(days=1)),
            valid_to=Timestamp().FromDatetime(datetime.datetime.now()+datetime.timedelta(days=1)),
            usage_limit_per_user=1,
            total_usage_limit=10,
            min_spend=0,
            max_cart_value=100,
            is_for_new_users=True,
            description="Test coupon",
            max_discount=10.0,
            is_active=True
    )
    )
    response = grpc_cart_stub.CreateCoupon(request, metadata=META_DATA)
    yield response.coupon
    try:
        grpc_cart_stub.RemoveCoupon(cart_pb2.RemoveCouponRequest(coupon_uuid=response.coupon.coupon_uuid), metadata=META_DATA)
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.NOT_FOUND:
            raise e

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_create_cart(grpc_cart_stub):
    logger.debug("Starting test_create_cart")
    request = cart_pb2.CreateCartRequest(
        store_uuid=store_uuid,
        user_phone_no=user_phone_no,
        order_type=cart_pb2.ORDERTYPE.ORDER_TYPE_DINE_IN,
        table_no="A1",
    )
    logger.debug(f"Sending CreateCart request: {request}")
    response = grpc_cart_stub.CreateCart(request, metadata=META_DATA)
    cart = response.cart
    logger.debug(f"Received cart: {cart}")
    assert cart.cart_uuid is not None
    assert cart.store_uuid == store_uuid
    assert cart.user_phone_no == user_phone_no
    assert cart.cart_state == cart_pb2.CARTSTATE.CART_STATE_ACTIVE

    request = cart_pb2.DeleteCartRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no
    )
    logger.debug(f"Sending DeleteCart request: {request}")
    grpc_cart_stub.DeleteCart(request, metadata=META_DATA)
    logger.debug("Cart deleted successfully")

def test_update_cart(grpc_cart_stub, cart):
    logger.debug("Starting test_update_cart")
    request = cart_pb2.UpdateCartRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no,
        order_type=cart_pb2.ORDERTYPE.ORDER_TYPE_TAKE_AWAY,
        vehicle_no="KA-01-HH-1234",
        vehicle_description="Red Sedan"
    )
    logger.debug(f"Sending UpdateCart request: {request}")
    response = grpc_cart_stub.UpdateCart(request, metadata=META_DATA)
    logger.debug(f"Received updated cart: {response.cart}")
    assert response.cart.vehicle_no == "KA-01-HH-1234"
    assert response.cart.vehicle_description == "Red Sedan" 
    assert response.cart.order_type == cart_pb2.ORDERTYPE.ORDER_TYPE_TAKE_AWAY

def test_get_cart(grpc_cart_stub, cart):
    logger.debug("Starting test_get_cart")
    request = cart_pb2.GetCartRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no
    )
    logger.debug(f"Sending GetCart request: {request}")
    response = grpc_cart_stub.GetCart(request, metadata=META_DATA)
    logger.debug(f"Received cart: {response.cart}")
    assert response.cart.cart_uuid == cart.cart_uuid
    assert response.cart.store_uuid == cart.store_uuid
    assert response.cart.user_phone_no == cart.user_phone_no
    assert response.cart.cart_state == cart_pb2.CARTSTATE.CART_STATE_ACTIVE

def test_get_cart_invalid_uuid(grpc_cart_stub):
    logger.debug("Starting test_get_cart_invalid_uuid")
    with pytest.raises(grpc.RpcError) as exc_info:
        request = cart_pb2.GetCartRequest(
            cart_uuid=str(uuid4()),
            store_uuid=store_uuid,
            user_phone_no=user_phone_no
        )
        logger.debug(f"Sending GetCart request with invalid UUID: {request}")
        grpc_cart_stub.GetCart(request, metadata=META_DATA)
    logger.debug(f"Received expected error: {exc_info.value}")
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_delete_cart(grpc_cart_stub, cart):
    logger.debug("Starting test_delete_cart")
    request = cart_pb2.DeleteCartRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no
    )
    logger.debug(f"Sending DeleteCart request: {request}")
    response = grpc_cart_stub.DeleteCart(request, metadata=META_DATA)
    logger.debug("Cart deleted successfully")
    assert response is not None
    
    logger.debug("Verifying cart deletion")
    with pytest.raises(grpc.RpcError) as exc_info:
        grpc_cart_stub.GetCart(
            cart_pb2.GetCartRequest(
                cart_uuid=cart.cart_uuid,
                store_uuid=cart.store_uuid,
                user_phone_no=cart.user_phone_no
            ), 
            metadata=META_DATA
        )
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    logger.debug("Cart deletion verified")

def test_add_cart_item(grpc_cart_stub, cart,grpc_product_server):
    logger.debug("Starting test_add_cart_item")
    request = cart_pb2.AddCartItemRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no,
        product_uuid=product_uuid,
    )
    logger.debug(f"Sending AddCartItem request: {request}")
    response = grpc_cart_stub.AddCartItem(request, metadata=META_DATA)
    logger.debug(f"Received cart with items: {response.cart}")
    assert len(response.cart.items) == 1
    assert response.cart.items[0].product_uuid == product_uuid

def test_remove_cart_item(grpc_cart_stub, cart_item,grpc_product_server):
    logger.debug("Starting test_remove_cart_item")
    request = cart_pb2.RemoveCartItemRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid
    )
    logger.debug(f"Sending RemoveCartItem request: {request}")
    response = grpc_cart_stub.RemoveCartItem(request, metadata=META_DATA)
    logger.debug(f"Received cart after item removal: {response.cart}")
    assert len(response.cart.items) == 0

def test_add_quantity(grpc_cart_stub, cart_item):
    request = cart_pb2.AddQuantityRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
    )
    response = grpc_cart_stub.AddQuantity(request, metadata=META_DATA)
    
    assert response.cart.items[0].quantity == 2

def test_remove_quantity(grpc_cart_stub, cart_item):
    # First, add a quantity to ensure we have something to remove
    request = cart_pb2.AddQuantityRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
    )
    response = grpc_cart_stub.AddQuantity(request, metadata=META_DATA)
    
    assert response.cart.items[0].quantity == 2
    # Now, remove the quantity
    request = cart_pb2.RemoveQuantityRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
    )
    response = grpc_cart_stub.RemoveQuantity(request, metadata=META_DATA)
    
    assert response.cart.items[0].quantity == 1

def test_create_add_on(grpc_cart_stub,cart,cart_item):
    request = cart_pb2.CreateAddOnRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no,
        cart_item_uuid=cart_item.cart_item_uuid,
        add_on_uuid=add_on_uuid
    )
    response = grpc_cart_stub.CreateAddOn(request, metadata=META_DATA)
    
    assert len(response.cart.items[0].add_ons) == 1
    assert response.cart.items[0].add_ons[0].add_on_uuid == add_on_uuid


def test_remove_add_on(grpc_cart_stub,cart, cart_item, add_on):
    request = cart_pb2.RemoveAddOnRequest(
        cart_uuid=cart.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
        add_on_uuid=add_on.add_on_uuid
    )
    response = grpc_cart_stub.RemoveAddOn(request, metadata=META_DATA)
    
    assert len(response.cart.items[0].add_ons) == 0

def test_increase_add_on_quantity(grpc_cart_stub, cart_item, add_on):
    request = cart_pb2.IncreaseAddOnQuantityRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
        add_on_uuid=add_on.add_on_uuid
    )
    response = grpc_cart_stub.IncreaseAddOnQuantity(request, metadata=META_DATA)
    
    assert response.cart.items[0].add_ons[0].quantity == 2

def test_remove_add_on_quantity(grpc_cart_stub, cart_item, add_on):
    # First, increase the add-on quantity to ensure we have something to remove
    request = cart_pb2.IncreaseAddOnQuantityRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
        add_on_uuid=add_on.add_on_uuid
    )
    response = grpc_cart_stub.IncreaseAddOnQuantity(request, metadata=META_DATA)
    
    assert response.cart.items[0].add_ons[0].quantity == 2
    # Now, remove the add-on quantity
    request = cart_pb2.RemoveAddOnQuantityRequest(
        cart_uuid=cart_item.cart_uuid,
        cart_item_uuid=cart_item.cart_item_uuid,
        add_on_uuid=add_on.add_on_uuid
    )
    response = grpc_cart_stub.RemoveAddOnQuantity(request, metadata=META_DATA)
    
    assert response.cart.items[0].add_ons[0].quantity == 1

def test_validate_cart(grpc_cart_stub, cart):
    request = cart_pb2.ValidateCartRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no
    )
    response = grpc_cart_stub.ValidateCart(request, metadata=META_DATA)
    
    assert response.cart.cart_uuid == cart.cart_uuid
    assert response.cart.store_uuid == cart.store_uuid
    assert response.cart.user_phone_no == cart.user_phone_no
    assert response.cart.cart_state == cart_pb2.CARTSTATE.CART_STATE_LOCKED

def test_validate_cart_invalid_uuid(grpc_cart_stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        request = cart_pb2.ValidateCartRequest(
            cart_uuid=str(uuid4()),
            store_uuid=store_uuid,
            user_phone_no=user_phone_no
        )
        grpc_cart_stub.ValidateCart(request, metadata=META_DATA)
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND



def test_add_coupon(grpc_cart_stub, cart):
    request = cart_pb2.AddCouponRequest(
        cart_uuid=cart.cart_uuid,
        store_uuid=cart.store_uuid,
        user_phone_no=cart.user_phone_no,
        coupon_code="TESTCOUPON"
    )
    response = grpc_cart_stub.AddCoupon(request, metadata=META_DATA)
    
    assert response.cart.coupon_code == "TESTCOUPON"