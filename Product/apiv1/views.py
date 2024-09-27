from django.shortcuts import render
from .models import product_model,category_model
from django.views import View
from .serializers import product_serializer,category_serializer
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils  import is_valid_uuid


class product_view(APIView):
    
    def get(self,request):
        store_id = request.GET.get("store_id",None)
        if not is_valid_uuid(store_id):
            return Response({"error":"store_id not a vaild UUID."},status = status.HTTP_400_BAD_REQUEST)
        products = product_model.objects.filter(store_id=store_id)
        serializer = product_serializer(products, many=True)  # Set many=True to serialize a queryset
        return Response(serializer.data)
        

    def post(self, request):
        print(request.data,"post")
        serializer = product_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        data = request.data
        if not "product_uuid" in data:
            return Response({"UUID":"UUID is requierd to update product."},status = status.HTTP_400_BAD_REQUEST)
        product_uuid  =  data.get("product_uuid")
        if not is_valid_uuid(product_uuid):
            return Response({"UUID":"UUID is not vaild."},status = status.HTTP_400_BAD_REQUEST)
        try:
            products = product_model.objects.get(product_uuid=product_uuid)
            print(products)
        except product_model.DoesNotExist:
            return Response({"error": "Products not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = product_serializer(products,data,partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
class category_view(APIView):
    
    def get(self,request):
        store_uuid = request.GET.get("store_uuid")
        if not is_valid_uuid(store_uuid):
            return Response({"error":"store_id not a vaild UUID."},status = status.HTTP_400_BAD_REQUEST)
        try:
            categories = category_model.objects.filter(store_uuid=store_uuid)
        except category_model.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)      # Use filter for multiple products
        serializer = category_serializer(categories, many=True)  # Set many=True to serialize a queryset
        return Response(serializer.data)
        

    def post(self,request):
        data = request.data
        serializer = category_serializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def put(self,request):
        data = request.data
        if not "category_uuid" in data:
            return Response({"category_UUID":"UUID is requierd to update category."},status = status.HTTP_400_BAD_REQUEST)
        category_uuid  =  data.get("category_uuid")
        if not is_valid_uuid(category_uuid):
            return Response({"UUID":"UUID is not vaild."},status = status.HTTP_400_BAD_REQUEST)
        try:
            categories = category_model.objects.get(category_uuid=category_uuid)
        except category_model.DoesNotExist:
            return Response({"error": "category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = category_serializer(categories,data,partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
#helper Function
