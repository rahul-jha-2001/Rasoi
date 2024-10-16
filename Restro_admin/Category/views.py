import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.protobuf.json_format import MessageToJson,MessageToDict
import logging
import grpc
from dataclasses import dataclass
from typing import Optional, List

from django.shortcuts import render
from proto import Category_pb2_grpc,Category_pb2

logger = logging.getLogger(__name__)


from dotenv import load_dotenv
load_dotenv()
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

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
    CategoryUuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    parent_Category_uuid: Optional[str] = None


class Client:
    
    def __init__(self, host: str = '127.0.0.1', port: int = 50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = Category_pb2_grpc.CategoryServiceStub(self.channel)

    
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
        return MessageToDict(response)

    @grpc_error_handler
    def get_Category(self, Category_uuid: str) -> Category_pb2.CategoryResponse:
        """Get a Category by UUID"""
        request = Category_pb2.GetCategoryRequest(CategoryUuid=Category_uuid)
        
        return MessageToDict(self.stub.GetCategory(request))
        
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
        return MessageToDict(response)

    
    @grpc_error_handler
    def delete_Category(self, Category_uuid: str) -> bool:
        """Delete a Category"""
        request = Category_pb2.DeleteCategoryRequest(CategoryUuid=Category_uuid)
        
        response = self.stub.DeleteCategory(request)
        logger.info(f"Deleted Category: {Category_uuid}")
        return MessageToDict(response)

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




class CategoryView(APIView):
    permission_classes = [IsAuthenticated ]
    authentication_classes = [JWTAuthentication]
    client = Client(host=os.getenv("GRPC_PRODUCT_SERVER"),port=os.getenv("GRPC_PRODUCT_SERVER_PORT"))

    def get(self,request):
        
        if not "CategoryUuid" in request.GET:
            return Response({"CategoryUuid":"CategoryUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        
        CategoryUuid = request.GET.get('CategoryUuid')
        Category = self.client.get_Category(Category_uuid=CategoryUuid)
        return Response(Category,status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data
        category  =  CategoryCreate(StoreUuid=data.get("StoreUuid"),
                                    Name=data.get("Name"),
                                    description= data.get("Description"),
                                    parent_Category_uuid=data.get("Parent"))
        
        response = self.client.create_Category(category)
        return Response(response,status.HTTP_201_CREATED)
    def patch(self,request):
        data  =  request.data
        if not "CategoryUuid" in request.data:
            return Response({"CategoryUuid":"CategoryUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        Category = CategoryUpdate(
                                CategoryUuid = data.get("CategoryUuid"),
                                Name=data.get("Name"),
                                Description=data.get("Description"),
                                parent_Category_uuid = data.get("parent")
                                )
        response = self.client.update_Category(Category)
        return Response(response,status.HTTP_202_ACCEPTED)
    
    def delete(self,request):
        if not "CategoryUuid" in request.data:
            return Response({"CategoryUuid":"CategoryUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        CategoryUuid = request.data.get("CategoryUuid")
        response = self.client.delete_Category(CategoryUuid)
        return Response(response,status.HTTP_202_ACCEPTED)


class ListCategoryView(APIView):
    permission_classes = [IsAuthenticated ]
    authentication_classes = [JWTAuthentication]
    client = Client(host=os.getenv("GRPC_PRODUCT_SERVER"),port=os.getenv("GRPC_PRODUCT_SERVER_PORT"))

    
    def get(self,request):
        if not "StoreUuid" in request.GET:
            return Response({"StoreUuid":"StoreUuid not present in request"},status.HTTP_400_BAD_REQUEST)
        StoreUuid = request.GET.get('StoreUuid')
        categories = self.client.list_categories(StoreUuid)
        categories = [MessageToDict(x) for x in categories]
        return Response(categories,status.HTTP_200_OK)
