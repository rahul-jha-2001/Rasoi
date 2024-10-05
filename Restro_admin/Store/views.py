from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import StoreSerializer
from .models import Store

from User.models import User
from rest_framework  import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import NotAuthenticated,NotFound


# Create your views here.

class StoreView(APIView):
    permission_classes = [IsAuthenticated ]
    authentication_classes = [JWTAuthentication] 
    def get(self,request):
        
        user = request.user
        
        stores = Store.objects.filter(user=user)

        if  not stores.exists():
            return Response({
                "data": []
            }, status=status.HTTP_200_OK)
        
        serializer = StoreSerializer(stores, many=True)
        
        data = serializer.data
        
        return Response(
            data={
                    "data" :data
                 }
        ,status= status.HTTP_200_OK)
    
    def post(self,request):
        
        data = request.data
        
        user = request.user 
        
        data["UserId"] = user.id
        
        serializer = StoreSerializer(data = data)
        
        if serializer.is_valid(raise_exception=True):
            
            serializer.save()
            
            return Response(status= status.HTTP_201_CREATED)
        
        return Response(
            {
                "Errors":serializer.errors
            }
        )
    
    def patch(self,request,StoreUuid):
        
        user = request.user

        try:
            store = Store.objects.get(StoreUuid=StoreUuid, user=user)
        
        except Store.DoesNotExist:
            
            raise NotFound("Store not found.")

        serializer = StoreSerializer(instance = store,data = request.data,partial = True)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status= status.HTTP_201_CREATED)
        
        return Response(
            {
                "Errors":serializer.errors
            }
        ,status = status.HTTP_400_BAD_REQUEST)
    
    