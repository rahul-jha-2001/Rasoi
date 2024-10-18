
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.protobuf.json_format import MessageToJson,MessageToDict
import logging
import grpc
from dataclasses import dataclass
from typing import Optional, List
from proto import Product_pb2,Product_pb2_grpc
logger = logging.getLogger(__name__)


from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import authtoken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated


def grpc_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.details()}, code: {e.code()}")
            raise
    return wrapper

@dataclass
class ProductCreate:
    StoreUuid: str
    Name: str
    Price:float
    IsAvailable:bool
    CategoryUuid: str
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
        self.stub = Product_pb2_grpc.ProductServiceStub(self.channel)
    
    @grpc_error_handler
    def create_product(self, product_data: ProductCreate) -> Product_pb2.ProductResponse:
        """Create a new Product"""
        request = Product_pb2.CreateProductRequest(
            StoreUuid=product_data.StoreUuid,
            Name=product_data.Name,
            IsAvailable=product_data.IsAvailable,
            Price=product_data.Price,
            CategoryUuid=product_data.CategoryUuid,
            Description=product_data.Description,
            ImageUrl=product_data.ImageUrl
        )
        response = self.stub.CreateProduct(request)
        logger.info(f"Created Product: {response.ProductUuid}")
        return MessageToDict(response)

    @grpc_error_handler
    def get_product(self, ProductUuid: str, StoreUuid: str) -> Product_pb2.ProductResponse:
        """Get a Product by UUID"""
        request = Product_pb2.GetProductRequest(ProductUuid=ProductUuid, StoreUuid=StoreUuid)
        return MessageToDict(self.stub.GetProduct(request))

    @grpc_error_handler
    def update_product(self, update_data: ProductUpdate) -> Product_pb2.ProductResponse:
        """Update a Product"""
        request = Product_pb2.UpdateProductRequest(
            ProductUuid=update_data.ProductUuid
        )
        
        if update_data.Name is not None:
            request.Name = update_data.Name
        if update_data.IsAvailable is not None:
            request.IsAvailable = update_data.IsAvailable
        if update_data.Price is not None:
            request.Price = update_data.Price
        if update_data.CategoryUuid is not None:
            request.CategoryUuid = update_data.CategoryUuid
        if update_data.Description is not None:
            request.Description = update_data.Description
        if update_data.ImageUrl is not None:
            request.ImageUrl = update_data.ImageUrl

        response = self.stub.UpdateProduct(request)
        logger.info(f"Updated Product: {response.ProductUuid}")
        return MessageToDict(response)

    @grpc_error_handler
    def delete_product(self, ProductUuid: str) -> bool:
        """Delete a Product"""
        request = Product_pb2.DeleteProductRequest(ProductUuid=ProductUuid)
        response = self.stub.DeleteProduct(request)
        logger.info(f"Deleted Product: {ProductUuid}")
        return MessageToDict(response)

    @grpc_error_handler
    def list_products(self, StoreUuid: str) -> List[Product_pb2.ProductResponse]:
        """List all products for a store"""
        request = Product_pb2.ListProductsRequest(StoreUuid=StoreUuid)
        
        response = self.stub.ListProducts(request)
        return response.products
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()




class ProductView(APIView):
    permission_classes = [IsAuthenticated ]
    authentication_classes = [JWTAuthentication]
    client = Client(host=os.getenv("GRPC_PRODUCT_SERVER"),port=os.getenv("GRPC_PRODUCT_SERVER_PORT"))

    def get(self,request):
        if not "StoreUuid" in request.GET:
            return Response({"StoreUuid":"StoreUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        
        if not "ProductUuid" in request.GET:
            return Response({"ProductUuid":"ProductUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        
        StoreUuid = request.GET.get('StoreUuid')
        ProductUuid = request.GET.get("ProductUuid")
        product = self.client.get_product(StoreUuid=StoreUuid,ProductUuid=ProductUuid)
        return Response(product,status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data
        product  =  ProductCreate(StoreUuid=data.get("StoreUuid"),
                                    Name=data.get("Name"),
                                    Price=data.get("Price"),
                                    IsAvailable=data.get("IsAvailable"),
                                    CategoryUuid=data.get("CategoryUuid"),
                                    Description=data.get("Description"),
                                    ImageUrl=data.get("ImageUrl"))
        
        response = self.client.create_product(product)
        return Response(response,status.HTTP_201_CREATED)
    def patch(self,request):
        data  =  request.data
        if not "ProductUuid" in request.data:
            return Response({"ProductUuid":"ProductUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        product = ProductUpdate(
                                ProductUuid = data.get("ProductUuid"),
                                Name=data.get("Name"),
                                Price=data.get("Price"),
                                IsAvailable=data.get("IsAvailable"),
                                CategoryUuid=data.get("CategoryUuid"),
                                Description=data.get("Description"),
                                ImageUrl=data.get("ImageUrl"))
        response = self.client.update_product(product)
        return Response(response,status.HTTP_202_ACCEPTED)
    
    def delete(self,request):
        if not "ProductUuid" in request.data:
            return Response({"ProductUuid":"ProductUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        ProductUuid = request.data.get("ProductUuid")
        response = self.client.delete_product(ProductUuid)
        return Response(response,status.HTTP_202_ACCEPTED)


class ListProductView(APIView):
    permission_classes = [IsAuthenticated ]
    authentication_classes = [JWTAuthentication]
    client = Client(host=os.getenv("GRPC_PRODUCT_SERVER"),port=os.getenv("GRPC_PRODUCT_SERVER_PORT"))
    
    def get(self,request):
        if not "StoreUuid" in request.GET:
            return Response({"StoreUuid":"StoreUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        StoreUuid = request.GET.get('StoreUuid')
        products = self.client.list_products(StoreUuid)
        products = [MessageToDict(x) for x in products]
        return Response(products,status.HTTP_200_OK)