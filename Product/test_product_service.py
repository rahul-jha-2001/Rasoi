
import threading
import sys
from pathlib import Path
import time
import grpc
import pytest
from uuid import uuid4
from grpc_serve import serve
from Proto import product_pb2_grpc, product_pb2
from Proto.product_pb2 import Productstatus

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

# Fixtures for setup and teardown
@pytest.fixture(scope="session")
def grpc_server():
    """Start the gRPC server for testing and stop it after tests"""
    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start
    yield
    # If the server has a shutdown method, you'd call it here

@pytest.fixture(scope="session")
def grpc_channel():
    """Create a gRPC channel for tests"""
    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        yield channel

@pytest.fixture(scope="session")
def store_uuid():
    """Generate a store UUID to use across tests"""
    return str(uuid4())

@pytest.fixture(scope="session")
def product_stub(grpc_channel):
    """Create a product service stub"""
    return product_pb2_grpc.ProductServiceStub(grpc_channel)

@pytest.fixture
def category(product_stub, store_uuid):
    """Create and return a test category"""
    request = product_pb2.CreateCategoryRequest(
        store_uuid=store_uuid,
        name="Starters",
        description="test cat",
        display_order=1,
        is_available=True,
        is_active=True
    )
    
    response = product_stub.CreateCategory(request, metadata=META_DATA)
    category_uuid = response.category.category_uuid
    
    yield response.category
    
    # Cleanup - delete the category after tests
    try:
        delete_request = product_pb2.DeleteCategoryRequest(
            store_uuid=store_uuid,
            category_uuid=category_uuid
        )
        product_stub.DeleteCategory(delete_request, metadata=META_DATA)
    except Exception as e:
        print(f"Failed to delete category: {e}")

@pytest.fixture
def diet_pref(product_stub, store_uuid):
    """Create and return a test dietary preference"""
    request = product_pb2.CreateDietaryPreference(
        store_uuid=store_uuid,
        name="Vegan",
        description="Healthy"
    )
    
    response = product_stub.CreateDietPref(request, metadata=META_DATA)
    diet_pref_uuid = response.dietary_preference.diet_pref_uuid
    
    yield response.dietary_preference
    
    # Cleanup - delete the dietary preference after tests
    try:
        delete_request = product_pb2.DeleteDietaryPreference(
            store_uuid=store_uuid,
            diet_pref_uuid=diet_pref_uuid
        )
        product_stub.DeleteDietPref(delete_request, metadata=META_DATA)
    except Exception as e:
        print(f"Failed to delete dietary preference: {e}")

@pytest.fixture
def product(product_stub, category, diet_pref, store_uuid):
    """Create and return a test product"""
    request = product_pb2.CreateProductRequest(
        store_uuid=store_uuid,
        name="Green Salad",
        description="Fresh & crispy",
        status=Productstatus.PRODUCT_STATE_ACTIVE,
        is_available=True,
        display_price=50.0,
        price=45.0,
        GST_percentage=5.0,
        packaging_cost=3.0,
        category_uuid=category.category_uuid,
        diet_pref_uuid=diet_pref.diet_pref_uuid
    )
    
    response = product_stub.CreateProduct(request, metadata=META_DATA)
    product_uuid = response.product.product_uuid
    
    yield response.product
    
    # Cleanup - delete the product after tests
    try:
        delete_request = product_pb2.DeleteProductRequest(
            store_uuid=store_uuid,
            category_uuid=category.category_uuid,
            product_uuid=product_uuid
        )
        product_stub.DeleteProduct(delete_request, metadata=META_DATA)
    except Exception as e:
        print(f"Failed to delete product: {e}")


# # Tests for Category
def test_create_category(grpc_server, product_stub, store_uuid):
    """Test creating a category"""
    request = product_pb2.CreateCategoryRequest(
        store_uuid=store_uuid,
        name="Desserts",
        description="Sweet items",
        display_order=2,
        is_available=True,
        is_active=True
    )
    
    response = product_stub.CreateCategory(request, metadata=META_DATA)
    
    assert response.category.name == "Desserts"
    assert response.category.description == "Sweet items"
    assert response.category.display_order == 2
    assert response.category.is_available is True
    assert response.category.is_active is True
    assert response.category.store_uuid == store_uuid
    
    # Cleanup
    delete_request = product_pb2.DeleteCategoryRequest(
        store_uuid=store_uuid,
        category_uuid=response.category.category_uuid
    )
    product_stub.DeleteCategory(delete_request, metadata=META_DATA)

def test_get_category(grpc_server, product_stub, category, store_uuid):
    """Test getting a category by ID"""
    request = product_pb2.GetCategoryRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid
    )
    
    response = product_stub.GetCategory(request, metadata=META_DATA)
    
    assert response.category.category_uuid == category.category_uuid
    assert response.category.name == category.name
    assert response.category.description == category.description

def test_update_category(grpc_server, product_stub, category, store_uuid):
    """Test updating a category"""
    request = product_pb2.UpdateCategoryRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        name="Updated Starters",
        is_available=False
    )
    
    response = product_stub.UpdateCategory(request, metadata=META_DATA)
    
    assert response.category.name == "Updated Starters"
    assert response.category.is_available is False
    assert response.category.description == category.description  # Unchanged

def test_list_categories(grpc_server, product_stub, category, store_uuid):
    """Test listing categories"""
    request = product_pb2.ListCategoryRequest(
        store_uuid=store_uuid,
        page=1,
        limit=10
    )
    
    response = product_stub.ListCategory(request, metadata=META_DATA)
    
    # Check if our test category is in the list
    category_found = False
    for cat in response.categories:
        if cat.category_uuid == category.category_uuid:
            category_found = True
            break
    
    assert category_found, "Created category not found in list"

# Tests for Dietary Preferences
def test_create_diet_pref(grpc_server, product_stub, store_uuid):
    """Test creating a dietary preference"""
    request = product_pb2.CreateDietaryPreference(
        store_uuid=store_uuid,
        name="Vegetarian",
        description="No meat"
    )
    
    response = product_stub.CreateDietPref(request, metadata=META_DATA)
    
    assert response.dietary_preference.name == "Vegetarian"
    assert response.dietary_preference.description == "No meat"
    assert response.dietary_preference.store_uuid == store_uuid
    
    # Cleanup
    delete_request = product_pb2.DeleteDietaryPreference(
        store_uuid=store_uuid,
        diet_pref_uuid=response.dietary_preference.diet_pref_uuid
    )
    product_stub.DeleteDietPref(delete_request, metadata=META_DATA)

def test_get_diet_pref(grpc_server, product_stub, diet_pref, store_uuid):
    """Test getting a dietary preference by ID"""
    request = product_pb2.GetDietaryPreference(
        store_uuid=store_uuid,
        diet_pref_uuid=diet_pref.diet_pref_uuid
    )
    
    response = product_stub.GetDietPref(request, metadata=META_DATA)
    
    assert response.dietary_preference.diet_pref_uuid == diet_pref.diet_pref_uuid
    assert response.dietary_preference.name == diet_pref.name
    assert response.dietary_preference.description == diet_pref.description

def test_create_diet_pref_invalid(grpc_server, product_stub, store_uuid):
    """Test creating a dietary preference with invalid data"""
    request = product_pb2.CreateDietaryPreference(
        store_uuid=store_uuid,
        name="",  # Invalid name
        description="No meat"
    )
    
    with pytest.raises(grpc.RpcError) as exc_info:
        product_stub.CreateDietPref(request, metadata=META_DATA)
    
    # Check if it's the expected error
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


# # Tests for Products
def test_create_product(grpc_server, product_stub, category, diet_pref, store_uuid):
    """Test creating a product"""
    request = product_pb2.CreateProductRequest(
        store_uuid=store_uuid,
        name="Green Salad",
        description="Fresh & crispy",
        status=Productstatus.PRODUCT_STATE_ACTIVE,
        is_available=True,
        display_price=50.0,
        price=45.0,
        GST_percentage=5.0,
        packaging_cost=3.0,
        category_uuid=category.category_uuid,
        diet_pref_uuid=diet_pref.diet_pref_uuid
    )
    
    response = product_stub.CreateProduct(request, metadata=META_DATA)
    product_uuid = response.product.product_uuid
    
    assert response.product.name == "Green Salad"
    assert response.product.description == "Fresh & crispy"
    assert response.product.status == Productstatus.PRODUCT_STATE_ACTIVE
    assert response.product.is_available is True
    assert response.product.display_price == 50.0
    assert response.product.price == 45.0
    assert response.product.GST_percentage == 5.0
    assert response.product.packaging_cost == 3.0
    assert response.product.category.category_uuid == category.category_uuid
    
    # Cleanup
    delete_request = product_pb2.DeleteProductRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        product_uuid=product_uuid
    )
    product_stub.DeleteProduct(delete_request, metadata=META_DATA)

def test_get_product(grpc_server, product_stub, category, diet_pref, store_uuid):
    """Test getting a product by ID"""
    # First create a product
    create_request = product_pb2.CreateProductRequest(
        store_uuid=store_uuid,
        name="Pasta",
        description="Italian specialty",
        status=Productstatus.PRODUCT_STATE_ACTIVE,
        is_available=True,
        display_price=100.0,
        price=90.0,
        GST_percentage=5.0,
        packaging_cost=5.0,
        category_uuid=category.category_uuid,
        diet_pref_uuid=diet_pref.diet_pref_uuid
    )
    
    create_response = product_stub.CreateProduct(create_request, metadata=META_DATA)
    product_uuid = create_response.product.product_uuid
    
    # Now get the product
    get_request = product_pb2.GetProductRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        product_uuid=product_uuid
    )
    
    get_response = product_stub.GetProduct(get_request, metadata=META_DATA)
    
    assert get_response.product.product_uuid == product_uuid
    assert get_response.product.name == "Pasta"
    
    # Cleanup
    delete_request = product_pb2.DeleteProductRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        product_uuid=product_uuid
    )
    product_stub.DeleteProduct(delete_request, metadata=META_DATA)

def test_update_product(grpc_server, product_stub, category, diet_pref, store_uuid):
    """Test updating a product"""
    # First create a product
    create_request = product_pb2.CreateProductRequest(
        store_uuid=store_uuid,
        name="Pizza",
        description="Classic Margherita",
        status=Productstatus.PRODUCT_STATE_ACTIVE,
        is_available=True,
        display_price=200.0,
        price=180.0,
        GST_percentage=5.0,
        packaging_cost=10.0,
        category_uuid=category.category_uuid,
        diet_pref_uuid=diet_pref.diet_pref_uuid
    )
    
    create_response = product_stub.CreateProduct(create_request, metadata=META_DATA)
    product_uuid = create_response.product.product_uuid
    
    # Now update the product
    update_request = product_pb2.UpdateProductRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        product_uuid=product_uuid,
        name="Deluxe Pizza",
        price=200.0,
        status=Productstatus.PRODUCT_STATE_OUT_OF_STOCK
    )
    
    update_response = product_stub.UpdateProduct(update_request, metadata=META_DATA)
    
    assert update_response.product.name == "Deluxe Pizza"
    assert update_response.product.price == 200.0
    assert update_response.product.status == Productstatus.PRODUCT_STATE_OUT_OF_STOCK
    assert update_response.product.description == "Classic Margherita"  # Unchanged
    
    # Cleanup
    delete_request = product_pb2.DeleteProductRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        product_uuid=product_uuid
    )
    product_stub.DeleteProduct(delete_request, metadata=META_DATA)

def test_list_products(grpc_server, product_stub, category, diet_pref, store_uuid):
    """Test listing products"""
    # Create a few products first
    products = []
    for i in range(3):
        create_request = product_pb2.CreateProductRequest(
            store_uuid=store_uuid,
            name=f"Product {i+1}",
            description=f"Description {i+1}",
            status=Productstatus.PRODUCT_STATE_ACTIVE,
            is_available=True,
            display_price=100.0 + i*10,
            price=90.0 + i*10,
            GST_percentage=5.0,
            packaging_cost=5.0,
            category_uuid=category.category_uuid,
            diet_pref_uuid=diet_pref.diet_pref_uuid
        )
        
        response = product_stub.CreateProduct(create_request, metadata=META_DATA)
        products.append(response.product)
    
    # Now list the products
    list_request = product_pb2.ListProductsRequest(
        store_uuid=store_uuid,
        category_uuid=category.category_uuid,
        page=1,
        limit=10
    )
    
    list_response = product_stub.ListProducts(list_request, metadata=META_DATA)
    
    # Check if all our products are in the list
    product_uuids = {p.product_uuid for p in products}
    found_uuids = {p.product_uuid for p in list_response.products}
    
    
    assert product_uuids.issubset(found_uuids), "Not all created products found in list"
    # Cleanup
    for product in products:
        delete_request = product_pb2.DeleteProductRequest(
            store_uuid=store_uuid,
            category_uuid=category.category_uuid,
            product_uuid=product.product_uuid
        )
        product_stub.DeleteProduct(delete_request, metadata=META_DATA)

# # Error case tests
def test_get_nonexistent_category(grpc_server, product_stub, store_uuid):
    """Test getting a category that doesn't exist"""
    request = product_pb2.GetCategoryRequest(
        store_uuid=store_uuid,
        category_uuid=str(uuid4())  # Random UUID that doesn't exist
    )
    
    with pytest.raises(grpc.RpcError) as exc_info:
        product_stub.GetCategory(request, metadata=META_DATA)
    
    # Check if it's the expected error
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_create_product_invalid_category(grpc_server, product_stub, diet_pref, store_uuid):
#     """Test creating a product with invalid category"""
    request = product_pb2.CreateProductRequest(
        store_uuid=store_uuid,
        name="Invalid Product",
        description="This will fail",
        status=Productstatus.PRODUCT_STATE_ACTIVE,
        is_available=True,
        display_price=50.0,
        price=45.0,
        GST_percentage=5.0,
        packaging_cost=3.0,
        category_uuid=str(uuid4()),  # Random UUID that doesn't exist
        diet_pref_uuid=diet_pref.diet_pref_uuid
    )
    
    with pytest.raises(grpc.RpcError) as exc_info:
        product_stub.CreateProduct(request, metadata=META_DATA)
    
    # Check if it's the expected error
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_create_addOn(grpc_server,product_stub,product,category,diet_pref,store_uuid):
    """Test creating a AddOn"""
    request = product_pb2.CreateAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        name="Dressing",
        is_available=True,
        max_selectable =2,
        GST_percentage =5.0,
        price = 10.0,
        is_free = False,
    )
    
    response = product_stub.CreateAddOn(request, metadata=META_DATA)

    
    assert response.add_on.name == "Dressing"
    assert response.add_on.is_available is True
    assert response.add_on.max_selectable == 2
    assert response.add_on.GST_percentage == 5.0
    assert response.add_on.price == 10.0
    assert response.add_on.product_uuid == product.product_uuid



    # Cleanup
    delete_request = product_pb2.DeleteAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        add_on_uuid = response.add_on.add_on_uuid,
    )
    product_stub.DeleteAddOn(delete_request, metadata=META_DATA)

def test_get_invalid_addOn(grpc_server,product_stub,product,category,diet_pref,store_uuid):
    """Test getting a AddOn"""
    request = product_pb2.GetAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        add_on_uuid = str(uuid4()),
    )
    
    with pytest.raises(grpc.RpcError) as exc_info:
        product_stub.GetAddOn(request, metadata=META_DATA)
    
    # Check if it's the expected error
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_update_addOn(grpc_server,product_stub,product,category,diet_pref,store_uuid):

    request = product_pb2.CreateAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        name="Dressing",
        is_available=True,
        max_selectable =2,
        GST_percentage =5.0,
        price = 10.0,
    )
    response = product_stub.CreateAddOn(request, metadata=META_DATA)
    add_on_uuid = response.add_on.add_on_uuid
    # Now update the product
    update_request = product_pb2.UpdateAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        add_on_uuid = add_on_uuid,
        name="Updated Dressing",
        is_available=False,
        max_selectable =1,
        GST_percentage =10.0,
        price = 20.0,
    )
    update_response = product_stub.UpdateAddOn(update_request, metadata=META_DATA)
    assert update_response.add_on.name == "Updated Dressing"
    assert update_response.add_on.is_available is False
    assert update_response.add_on.max_selectable == 1
    assert update_response.add_on.GST_percentage == 10.0
    assert update_response.add_on.price == 20.0
    assert update_response.add_on.product_uuid == product.product_uuid  
    # Cleanup
    delete_request = product_pb2.DeleteAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        add_on_uuid = add_on_uuid,
    )
    product_stub.DeleteAddOn(delete_request, metadata=META_DATA)
def test_list_addOn(grpc_server,product_stub,product,category,diet_pref,store_uuid):
    """Test listing products"""
    # Create a few products first
    add_ons = []
    for i in range(3):
        create_request = product_pb2.CreateAddOnRequest(
            store_uuid=store_uuid,
            product_uuid= product.product_uuid,
            name=f"AddOn {i+1}",
            is_available=True,
            max_selectable =2,
            GST_percentage =5.0,
            price = 10.0 + i*10,
        )
        
        response = product_stub.CreateAddOn(create_request, metadata=META_DATA)
        add_ons.append(response.add_on)
    
    # Now list the products
    list_request = product_pb2.ListAddOnRequest(
        store_uuid=store_uuid,
        product_uuid= product.product_uuid,
        page=1,
        limit=10
    )
    
    list_response = product_stub.ListAddOn(list_request, metadata=META_DATA)
    
    # Check if all our products are in the list
    add_on_uuids = {p.add_on_uuid for p in add_ons}
    found_uuids = {p.add_on_uuid for p in list_response.add_ons}
    
    
    assert add_on_uuids.issubset(found_uuids), "Not all created products found in list"
    # Cleanup
    for add_on in add_ons:
        delete_request = product_pb2.DeleteAddOnRequest(
            store_uuid=store_uuid,
            product_uuid= product.product_uuid,
            add_on_uuid = add_on.add_on_uuid,
        )
        product_stub.DeleteAddOn(delete_request, metadata=META_DATA)


# ADD COUPON TESTS