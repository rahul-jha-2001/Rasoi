from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User
from datetime import timedelta,datetime
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
            
            user = authenticate(username = data["Username"],password = data["Password"])
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                uuid = User.objects.get(Email = data["Username"]).get_Uuid()
                
                response = Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "access_token": access_token,
                    "uuid": str(uuid)
                },status=status.HTTP_200_OK)

                # Set secure cookies
                expires = datetime.now() + timedelta(days=7)  # 7 days expiry
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    expires=expires,
                    httponly=True,
                    secure=not settings.DEBUG,  # Secure in production
                    samesite='Lax',
                    path='/api/token/refresh/'  # Restrict cookie path
                )
                response.set_cookie(
                    key='access_token',
                    value=str(access_token),
                    expires=expires,
                    httponly=True,
                    secure=not settings.DEBUG,  # Secure in production
                    samesite='Lax',
                    path='/api/token/access/'  # Restrict cookie path
                )
                response.set_cookie(
                    key='UserUuid',
                    value=str(uuid),
                    expires=expires,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    path='/api/'
                )

                return response
            return Response(
                {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "Message":"Invaild Credentials"
                })
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
                "Username":serializer.validated_data["Email"]
                
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
        return Response(data=data,status=status.HTTP_200_OK)
        