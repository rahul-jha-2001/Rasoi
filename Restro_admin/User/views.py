from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User

from .serializers import UserSerializer,LoginSerializer,RegisterSerializer
from rest_framework import authtoken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated


class LoginView(APIView):
    authentication_classes = []  # No authentication required for login
    permission_classes = [AllowAny]  # Allow any user to access the login
    def post(self,request):
        data = request.data

        
        serializer = LoginSerializer(data = data)
        
        if serializer.is_valid(raise_exception=True):
            
            user = authenticate(username = data["UserName"],password = data["PassWord"])
            if user:
                
                
                refresh = RefreshToken.for_user(user)
                uuid = User.objects.get(Email = data["UserName"]).get_Uuid()
                
                reponse = Response(
                    {
                        "status":status.HTTP_202_ACCEPTED,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        "Uuid":str(uuid)
                    }
                )
                reponse.set_cookie(
                key='auth_token',
                value=str(refresh),
                httponly=True,
                samesite='Lax',  # Ensures the cookie is sent with cross-site requests
                )
                reponse.set_cookie(
                key='UserUuid',
                value=str(uuid),
                httponly=True,
                samesite='Lax',  # Ensures the cookie is sent with cross-site requests
            )
                return reponse
            return Response(
                {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "Message":"Invaild Credentials"
                }
            )
        return Response({
                "status"  : status.HTTP_400_BAD_REQUEST,
                "data" : serializer.errors
            })
class RegisterView(APIView):
    authentication_classes = []  # No authentication required for login
    permission_classes = [AllowAny]  # Allow any user to access the login
    def post(self,request):
        data  =  request.data

        serializer  =  RegisterSerializer(data = data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                "UserName":serializer.validated_data["Email"]
                
            },status= status.HTTP_201_CREATED)
        return Response(
            {
                "errors":serializer.errors
            }
            ,status= status.HTTP_400_BAD_REQUEST )
class UserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    def get(self,reqeust,Email):
        user = reqeust.user
        
        if not user.is_authenticated:
            raise   NotAuthenticated
        
        UserObject = User.objects.get(Email = Email)
        serializer = UserSerializer(UserObject)
        data = serializer.data
        return Response({"data":data})
        