
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(os.path.dirname(os.curdir))

import logging
import grpc
from typing import Optional, List
from dataclasses import dataclass
from Product.proto import Category_pb2,Product_pb2
from Product.proto import Category_pb2_grpc,Product_pb2_grpc

logger = logging.getLogger(__name__)

def grpc_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.details()}, code: {e.code()}")
            raise
    return wrapper


@dataclass
class CategoryCreate:
    store_uuid: str
    name: str
    description: str
    parent_Category_uuid: Optional[str] = None

@dataclass
class CategoryUpdate:
    Category_uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    parent_Category_uuid: Optional[str] = None

@dataclass
class ProdcutCreate:
    store_uuid: str
    name: str
    price:float
    IsAvailable:bool
    Category_uuid: str
    Description:str
    ImageUrl:str
@dataclass
class ProductUpdate:
    ProductUuid : str
    Name :str
    IsAvailable : bool
    Price: float
    CategoryUuid : str
    Description : str
    ImageUrl :str



class Client:
    def __init__(self, host: str = '127.0.0.1', port: int = 50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = Category_pb2_grpc.CategoryServiceStub(self.channel)
        self.stub = Product_pb2_grpc.ProductServiceStub(self.channel)
    
    @grpc_error_handler
    def create_product(self, product_data: ProdcutCreate) -> Product_pb2.ProductResponse:
        """Create a new Product"""
        request = Product_pb2.CreateProductRequest(
            StoreUuid=product_data.store_uuid,
            Name=product_data.name,
            IsAvailable=product_data.is_available,
            Price=product_data.price,
            CategoryUuid=product_data.category_uuid,
            Description=product_data.description,
            ImageUrl=product_data.image_url
        )
        response = self.stub.CreateProduct(request)
        logger.info(f"Created Product: {response.ProductUuid}")
        return response

    @grpc_error_handler
    def get_product(self, product_uuid: str, store_uuid: str) -> Product_pb2.ProductResponse:
        """Get a Product by UUID"""
        request = Product_pb2.GetProductRequest(ProductUuid=product_uuid, StoreUuid=store_uuid)
        return self.stub.GetProduct(request)

    @grpc_error_handler
    def update_product(self, update_data: ProductUpdate) -> Product_pb2.ProductResponse:
        """Update a Product"""
        request = Product_pb2.UpdateProductRequest(
            ProductUuid=update_data.product_uuid
        )
        
        if update_data.name is not None:
            request.Name = update_data.name
        if update_data.is_available is not None:
            request.IsAvailable = update_data.is_available
        if update_data.price is not None:
            request.Price = update_data.price
        if update_data.category_uuid is not None:
            request.CategoryUuid = update_data.category_uuid
        if update_data.description is not None:
            request.Description = update_data.description
        if update_data.image_url is not None:
            request.ImageUrl = update_data.image_url

        response = self.stub.UpdateProduct(request)
        logger.info(f"Updated Product: {response.ProductUuid}")
        return response

    @grpc_error_handler
    def delete_product(self, product_uuid: str) -> bool:
        """Delete a Product"""
        request = Product_pb2.DeleteProductRequest(ProductUuid=product_uuid)
        response = self.stub.DeleteProduct(request)
        logger.info(f"Deleted Product: {product_uuid}")
        return response.Success

    @grpc_error_handler
    def list_products(self, store_uuid: str) -> List[Product_pb2.ProductResponse]:
        """List all products for a store"""
        request = Product_pb2.ListProductsRequest(StoreUuid=store_uuid)
        
        response = self.stub.ListProducts(request)
        return list(response.products)
    
    @grpc_error_handler
    def create_Category(self, Category_data: CategoryCreate) -> Category_pb2.CategoryResponse:
        """Create a new Category"""
        request = Category_pb2.CreateCategoryRequest(
            StoreUuid=Category_data.store_uuid,
            Name=Category_data.name,
            Description=Category_data.description,
            ParentCategoryUuid=Category_data.parent_Category_uuid
        )
        
       
        response = self.stub.CreateCategory(request)
        logger.info(f"Created Category: {response.CategoryUuid}")
        return response

    @grpc_error_handler
    def get_Category(self, Category_uuid: str) -> Category_pb2.CategoryResponse:
        """Get a Category by UUID"""
        request = Category_pb2.GetCategoryRequest(CategoryUuid=Category_uuid)
        
        return self.stub.GetCategory(request)
        
    @grpc_error_handler
    def update_Category(self, update_data: CategoryUpdate) -> Category_pb2.CategoryResponse:
        """Update a Category"""
        request = Category_pb2.UpdateCategoryRequest(
            CategoryUuid=update_data.Category_uuid
        )
        
        if update_data.name is not None:
            request.Name = update_data.name
        if update_data.description is not None:
            request.Description = update_data.description
        if update_data.parent_Category_uuid is not None:
            request.ParentCategoryUuid = update_data.parent_Category_uuid

        response = self.stub.UpdateCategory(request)
        logger.info(f"Updated Category: {response.CategoryUuid}")
        return response

    
    @grpc_error_handler
    def delete_Category(self, Category_uuid: str) -> bool:
        """Delete a Category"""
        request = Category_pb2.DeleteCategoryRequest(CategoryUuid=Category_uuid)
        
        response = self.stub.DeleteCategory(request)
        logger.info(f"Deleted Category: {Category_uuid}")
        return response.Success

    @grpc_error_handler
    def list_categories(self, store_uuid: str) -> List[Category_pb2.CategoryResponse]:
        """List all categories for a store"""
        request = Category_pb2.ListCategoriesRequest(StoreUuid=store_uuid)
        
        response = self.stub.ListCategories(request)
        return list(response.categories)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

# Example usage
def main():
    logging.basicConfig(level=logging.INFO)
    
    with Client() as client:
        try:
            # Create a Category
            new_Category = ProdcutCreate(
                StoreUuid = "43860837-d81e-4832-9ef8-5989144c165e",
                Name = "Electronics-2",
                IsAvailable = False,
                Price = 40.20000076293945,
                CategoryUuid = "06012269-41bf-4e74-a586-f10218f9a9bc",
                Description = "Electronic products",
                ImageUrl = "http//:oaoao"
                )
            
            Category = client.create_Category(new_Category)
            print(f"Created Category: {Category.CategoryUuid}")

            # # Update the Category
            update_data = ProductUpdate(
                Category_uuid=Category.CategoryUuid,
                description="Updated description"
            )
            updated = client.update_Category(update_data)
            print(f"Updated Category: {updated.CategoryUuid}")

            # List categories
            categories = client.list_products("43860837-d81e-4832-9ef8-5989144c165e")
            print(f"Found {len(categories)} categories")
            print([x for x in categories])
            # Delete Category
            # deleted = client.delete_Category("00118883-99df-43c6-9070-08c63f63ff73")
            # print(f"Category deleted: {deleted}")

        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

if __name__ == "__main__":
    main()